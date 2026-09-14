from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Optional
from uuid import UUID, uuid4

import jwt
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.settings import security_settings, user_verification_settings

APP_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = APP_DIR / "templates"


def encode_access_token(
    data: dict,
    expiry: timedelta = timedelta(minutes=security_settings.TOKEN_EXPIRES_MINUTES),
) -> str:
    return jwt.encode(
        payload={**data, "exp": datetime.now(UTC) + expiry, "jti": str(uuid4())},
        algorithm=security_settings.ALGO,
        key=security_settings.SECRET,
    )


def decode_access_token(token: str) -> dict:
    return jwt.decode(
        jwt=token, key=security_settings.SECRET, algorithms=[security_settings.ALGO]
    )


_serializer = URLSafeTimedSerializer(
    secret_key=user_verification_settings.USER_VERIFY_TOKEN_SECRET,
)


def encode_email_validation_token(payload: dict[str, str]) -> str:
    return _serializer.dumps(payload, salt=user_verification_settings.EMAIL_TOKEN_SALT)

def decode_email_validation_token(token: str) -> Optional[dict[str,str]]:
    try:
        payload = _serializer.loads(
            token,
            salt=user_verification_settings.EMAIL_TOKEN_SALT,
            max_age=timedelta(
                minutes=user_verification_settings.EMAIL_TOKEN_DURATION_MINUTES
            ).total_seconds(),
        )
    except (BadSignature, SignatureExpired):
        return None

    return payload

def encode_password_reset_token(id: UUID) -> str:
    return _serializer.dumps(id.hex, salt=user_verification_settings.PASSWORD_TOKEN_SALT)

def decode_password_reset_token(token: str) -> Optional[UUID]:
    try:
        id = _serializer.loads(
            token,
            salt=user_verification_settings.PASSWORD_TOKEN_SALT,
            max_age=timedelta(
                minutes=user_verification_settings.PASSWORD_TOKEN_DURATION_MINUTES
            ).total_seconds(),
        )
    except (BadSignature, SignatureExpired):
        return None

    return UUID(id)

def encode_review_token(shipment_id: UUID) -> str:
    return _serializer.dumps(shipment_id.hex, salt=user_verification_settings.REVIEW_TOKEN_SALT)

def decode_review_token(token: str) -> UUID | None:
    try:
        id_hex = _serializer.loads(
            token,
            salt=user_verification_settings.REVIEW_TOKEN_SALT,
            max_age=timedelta(
                days=user_verification_settings.REVIEW_TOKEN_DURATION_DAYS
            ).total_seconds()
        )
    except (BadSignature, SignatureExpired):
        return None

    return UUID(id_hex)