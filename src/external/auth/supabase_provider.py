from src.external.auth.base import IAuthProvider


class SupabaseAuthProvider(IAuthProvider):
    """Supabase 인증 공급자 (스텁)

    실제 구현 시:
    - supabase 패키지 설치 필요
    - Supabase 프로젝트 URL과 anon key 필요
    - SUPABASE_URL, SUPABASE_KEY 환경변수 설정
    """

    def __init__(self, url: str | None = None, key: str | None = None):
        self.url = url
        self.key = key
        # TODO: supabase.create_client(url, key) 호출

    def create_token(self, user_id: str, expires_minutes: int | None = None) -> str:
        # Supabase는 클라이언트 SDK에서 토큰 생성
        raise NotImplementedError("Supabase Auth는 클라이언트에서 토큰을 생성합니다")

    def verify_token(self, token: str) -> dict | None:
        # TODO: supabase.auth.get_user(token)
        raise NotImplementedError("Supabase Auth 구현 필요")

    def hash_password(self, password: str) -> str:
        # Supabase Auth는 비밀번호 해싱을 내부적으로 처리
        msg = "Supabase Auth는 비밀번호 해싱을 내부적으로 처리합니다"
        raise NotImplementedError(msg)

    def verify_password(self, plain: str, hashed: str) -> bool:
        # Supabase Auth는 비밀번호 검증을 내부적으로 처리
        msg = "Supabase Auth는 비밀번호 검증을 내부적으로 처리합니다"
        raise NotImplementedError(msg)
