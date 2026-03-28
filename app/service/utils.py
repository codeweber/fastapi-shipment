from datetime import UTC, datetime, timedelta

import jwt

from app.settings import security_settings


def encode_access_token(data: dict, expiry: timedelta = security_settings.TOKEN_EXPIRES_MINUTES) -> str:
    return jwt.encode(
        payload={**data, "exp": datetime.now(UTC) + expiry},
        algorithm=security_settings.ALGO,
        key=security_settings.SECRET,
    )


def decode_access_token(token: str) -> dict:
    return jwt.decode(
        jwt=token, key=security_settings.SECRET, algorithms=[security_settings.ALGO]
    )
