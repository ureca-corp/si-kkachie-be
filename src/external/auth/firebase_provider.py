from src.external.auth.base import IAuthProvider


class FirebaseAuthProvider(IAuthProvider):
    """Firebase 인증 공급자 (스텁)

    실제 구현 시:
    - firebase-admin 패키지 설치 필요
    - Firebase Console에서 서비스 계정 키 다운로드
    - FIREBASE_CREDENTIALS 환경변수에 경로 설정
    """

    def __init__(self, credentials_path: str | None = None):
        self.credentials_path = credentials_path
        # TODO: firebase_admin.initialize_app() 호출

    def create_token(self, user_id: str, expires_minutes: int | None = None) -> str:
        # Firebase는 클라이언트 SDK에서 토큰 생성
        # 서버에서는 커스텀 토큰만 생성 가능
        raise NotImplementedError("Firebase Auth는 클라이언트에서 토큰을 생성합니다")

    def verify_token(self, token: str) -> dict | None:
        # TODO: firebase_admin.auth.verify_id_token(token)
        raise NotImplementedError("Firebase Auth 구현 필요")

    def hash_password(self, password: str) -> str:
        # Firebase Auth는 비밀번호 해싱을 내부적으로 처리
        msg = "Firebase Auth는 비밀번호 해싱을 내부적으로 처리합니다"
        raise NotImplementedError(msg)

    def verify_password(self, plain: str, hashed: str) -> bool:
        # Firebase Auth는 비밀번호 검증을 내부적으로 처리
        msg = "Firebase Auth는 비밀번호 검증을 내부적으로 처리합니다"
        raise NotImplementedError(msg)
