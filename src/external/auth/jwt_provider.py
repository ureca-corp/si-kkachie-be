from datetime import UTC, datetime, timedelta

import bcrypt
from jose import JWTError, jwt

from src.external.auth.base import IAuthProvider


class JWTAuthProvider(IAuthProvider):
    """JWT 기반 인증 공급자"""

    def __init__(
        self,
        secret_key: str,
        algorithm: str,
        expire_minutes: int = 30,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expire_minutes = expire_minutes

    def create_token(self, user_id: str, expires_minutes: int | None = None) -> str:
        minutes = (
            expires_minutes if expires_minutes is not None else self.expire_minutes
        )
        expire = datetime.now(UTC) + timedelta(minutes=minutes)
        payload = {"sub": user_id, "exp": expire}
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> dict | None:
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except JWTError:
            return None

    def hash_password(self, password: str) -> str:
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode("utf-8")

    def verify_password(self, plain: str, hashed: str) -> bool:
        plain_bytes = plain.encode("utf-8")
        hashed_bytes = hashed.encode("utf-8")
        return bcrypt.checkpw(plain_bytes, hashed_bytes)
