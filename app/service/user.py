from datetime import UTC, datetime, timedelta
from typing import Optional
from uuid import UUID

from pwdlib import PasswordHash
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.model import DeliveryPartner, Seller, UserMixin
from app.model.errors import UnauthorizedException
from app.service import utils
from app.service.base import BaseService
from app.service.notification import NotificationService
from app.service.utils import decode_password_reset_token, encode_access_token
from app.settings import deployment_settings


class UserService(BaseService):
    def __init__(
        self,
        user_type: UserMixin,
        session: AsyncSession,
        redis: Redis,
        notification_service: NotificationService,
    ):
        super().__init__(model=user_type, session=session)
        self.redis = redis
        self._password_hash = PasswordHash.recommended()
        self.notification_service = notification_service

    def hash(self, password: str) -> str:
        return self._password_hash.hash(password)

    def verify(self, cleartext: str, encryptedtext: str) -> bool:
        return self._password_hash.verify(cleartext, encryptedtext)

    async def _get_user_by_email(self, email: str) -> Optional[UserMixin]:
        stmt = select(self.model).where(self.model.email == email)
        result = await self.session.scalars(stmt)
        maybe_user: UserMixin | None = result.one_or_none()
        return maybe_user

    async def token(self, username: str, password: str) -> Optional[str]:
        maybe_user = await self._get_user_by_email(username)

        if not maybe_user or not (self.verify(password, maybe_user.password_hash)):
            return None

        if not maybe_user.email_verified:
            raise UnauthorizedException("Email address has not been verified")

        token = encode_access_token(
            data={
                "user": {
                    "id": str(maybe_user.id),
                }
            }
        )

        return token

    async def blacklist_token(self, token_id: str, expiry: datetime) -> None:
        current_timestamp = datetime.now(UTC)
        if expiry <= current_timestamp:
            ttl = timedelta(days=1)
        else:
            ttl = (expiry - current_timestamp) + timedelta(days=1)
        await self.redis.set(token_id, current_timestamp.isoformat(), ttl)

    async def is_token_blacklisted(self, token_id: str) -> bool:
        result = await self.redis.get(token_id)
        if result:
            return True
        else:
            return False

    def send_verification(self, user: UserMixin) -> None:
        payload = {"email": user.email, "id": user.id.hex}

        token = utils.encode_email_validation_token(payload)

        match user:
            case Seller():
                path_prefix = "seller"
            case DeliveryPartner():
                path_prefix = "partner"
            case _:
                raise RuntimeError(
                    f"Cannot infer path_prefix for unknown type {user!r}"
                )

        self.notification_service.send_email_with_template(
            recipients=[user.email],
            subject="Verify Your Account",
            template_body={
                "username": user.name,
                "verification_url": f"http://{deployment_settings.HOST}:{deployment_settings.PORT}/{path_prefix}/verify?token={token}",
            },
            template_name="mail_email_verify.html",
        )

    async def verify_email(self, token: str) -> Optional[UUID]:

        token_payload = utils.decode_email_validation_token(token)

        if not token_payload:
            return None

        user_id = UUID(hex=token_payload.get("id"))
        user: UserMixin = await self._get(user_id)

        if not user:
            return None

        user.email_verified = True
        await self._update(user)
        return user_id

    async def send_password_reset(self, email: str, prefix: str) -> Optional[UUID]:

        maybe_user = await self._get_user_by_email(email)

        if not maybe_user:
            return None

        user_id = maybe_user.id
        token = utils.encode_password_reset_token(id=user_id)

        self.notification_service.send_email_with_template(
            recipients=[email],
            subject="Reset Your Password",
            template_body={
                "username": maybe_user.name,
                "password_reset_url": f"http://{deployment_settings.HOST}:{deployment_settings.PORT}{prefix}/reset_password?token={token}",
            },
            template_name="mail_password_reset.html",
        )

        return user_id

    async def reset_password(self, token: str, password: str) -> Optional[UserMixin]:

        user_id = decode_password_reset_token(token)
        maybe_user: UserMixin = (await self._get(user_id)) if user_id is not None else None

        if not maybe_user:
            return None

        maybe_user.password_hash = self.hash(password)
        updated_user = await self._update(maybe_user)
        return updated_user
