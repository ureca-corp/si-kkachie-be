from src.external.auth.base import IAuthProvider


class SupabaseAuthProvider(IAuthProvider):
    """Supabase 인증 공급자

    주의:
    - Supabase Auth 토큰은 **클라이언트(Supabase SDK)** 에서 발급됩니다.
    - 백엔드는 Authorization Bearer 토큰을 **검증**하고 사용자 정보를 조회합니다.
    """

    def __init__(self, url: str | None = None, key: str | None = None):
        if not url:
            raise ValueError("SUPABASE_URL is required")
        if not key:
            raise ValueError("SUPABASE_KEY is required")

        # supabase client는 내부적으로 sync http를 사용합니다.
        from supabase import create_client

        self.url = url
        self.key = key
        self._client = create_client(url, key)

    def create_token(self, user_id: str, expires_minutes: int | None = None) -> str:
        # Supabase는 클라이언트 SDK에서 토큰 생성
        raise NotImplementedError("Supabase Auth는 클라이언트에서 토큰을 생성합니다")

    def verify_token(self, token: str) -> dict | None:
        try:
            response = self._client.auth.get_user(token)
        except Exception:
            return None

        if response.user is None:
            return None

        return {
            "id": response.user.id,
            "email": response.user.email,
        }

    def hash_password(self, password: str) -> str:
        # Supabase Auth는 비밀번호 해싱을 내부적으로 처리
        msg = "Supabase Auth는 비밀번호 해싱을 내부적으로 처리합니다"
        raise NotImplementedError(msg)

    def verify_password(self, plain: str, hashed: str) -> bool:
        # Supabase Auth는 비밀번호 검증을 내부적으로 처리
        msg = "Supabase Auth는 비밀번호 검증을 내부적으로 처리합니다"
        raise NotImplementedError(msg)
