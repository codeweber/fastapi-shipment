from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Optional, Any
from uuid import uuid4

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
import jwt

from app.settings import security_settings, email_token_settings

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
    secret_key=email_token_settings.EMAIL_TOKEN_SECRET,
    salt=email_token_settings.EMAIL_TOKEN_SALT,
)


def encode_email_validation_token(payload: dict[str, str]) -> str:
    return _serializer.dumps(payload)

def decode_email_validation_token(token: str) -> Optional[dict[str,str]]:
    try:
        payload = _serializer.loads(
            token,
            max_age=timedelta(
                minutes=email_token_settings.EMAIL_TOKEN_DURATION_MINUTES
            ).total_seconds(),
        )
    except (BadSignature, SignatureExpired):
        return None

    return payload
