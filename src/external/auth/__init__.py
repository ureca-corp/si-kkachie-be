from src.core.config import settings
from src.external.auth.base import IAuthProvider
from src.external.auth.firebase_provider import FirebaseAuthProvider
from src.external.auth.jwt_provider import JWTAuthProvider
from src.external.auth.supabase_provider import SupabaseAuthProvider

_auth_instance: IAuthProvider | None = None


def get_auth_provider() -> IAuthProvider:
    """설정에 따라 적절한 인증 공급자 반환"""
    global _auth_instance

    if _auth_instance is not None:
        return _auth_instance

    match settings.AUTH_BACKEND:
        case "jwt":
            _auth_instance = JWTAuthProvider(
                secret_key=settings.SECRET_KEY,
                algorithm=settings.ALGORITHM,
                expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            )

        case "firebase":
            _auth_instance = FirebaseAuthProvider(
                credentials_path=settings.FIREBASE_CREDENTIALS,
            )

        case "supabase":
            _auth_instance = SupabaseAuthProvider(
                url=settings.SUPABASE_URL,
                key=settings.SUPABASE_KEY,
            )

        case _:
            _auth_instance = JWTAuthProvider(
                secret_key=settings.SECRET_KEY,
                algorithm=settings.ALGORITHM,
                expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            )

    return _auth_instance


__all__ = [
    "FirebaseAuthProvider",
    "IAuthProvider",
    "JWTAuthProvider",
    "SupabaseAuthProvider",
    "get_auth_provider",
]
