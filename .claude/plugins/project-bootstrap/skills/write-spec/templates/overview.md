# _overview.md 템플릿

> write-spec 스킬에서 참조하는 전체 개요 템플릿

---

## 템플릿

```markdown
# Project Specification Overview

**생성일**: 2026-01-17
**도메인 수**: 3개 (users, orders, products)

---

## 외부 라이브러리

### 인증
- **선택**: JWT (python-jose, passlib)
- **이유**: 커스터마이징 자유, 종속성 최소
- **대안 고려**: Firebase Auth (빠른 개발)

### 결제
- **선택**: Toss Payments (toss-payments-python)
- **이유**: 한국 시장, 간편결제 통합
- **대안 고려**: Stripe (글로벌)

### 파일 업로드
- **선택**: AWS S3 (boto3)
- **이유**: 안정성, 확장성
- **대안 고려**: Cloudflare R2 (비용)

---

## 공통 규칙

### API 응답 포맷
모든 API는 `ApiResponse` 사용:
```json
{
  "status": "SUCCESS" | "ERROR_*",
  "message": "한글 메시지",
  "data": {...} | null
}
```

### Status 코드 네이밍
```python
# 올바른 방식
Status.USER_NOT_FOUND
Status.VALIDATION_ERROR

# 잘못된 방식 (문자열 직접 사용 금지)
"user_not_found"
```

### 에러 메시지
비개발자가 이해할 수 있는 자연스러운 한글:
- "로그인이 필요해요"
- "올바른 이메일 형식이 아니에요"

### 테스트 작성 필수
**모든 코드는 테스트와 함께 작성!**
- 테스트 없는 코드 = 미완성 코드
- finalize-implementation에서 100% 커버리지 요구
- TDD 권장: 테스트 먼저 작성 후 구현

---

## 도메인 목록

각 도메인의 상세 스펙은 개별 파일 참조:

1. [users.md](./users.md) - 회원 관리
2. [orders.md](./orders.md) - 주문 관리
3. [products.md](./products.md) - 상품 관리

---

## 디렉토리 구조

```
src/
├── core/                    # 앱 내부 프레임워크
│   ├── config.py
│   ├── database/
│   ├── response.py          # ApiResponse
│   └── exceptions.py
│
├── external/                # 외부 서비스 연동
│   ├── storage/             # S3
│   ├── email/               # SES, SendGrid
│   └── payment/             # Toss, Stripe
│
├── common/                  # 도메인 간 공유 로직
│   ├── auth/                # 인증/인가
│   └── pagination/
│
└── modules/                 # 비즈니스 도메인 (CSR 패턴)
    └── {domain}/
        ├── models.py        # Model
        ├── entities.py      # DTO
        ├── repository.py    # Repository
        ├── service.py       # Service
        └── controller.py    # Controller

tests/
└── modules/{domain}/
    ├── test_controller.py   # 엔드포인트 테스트
    └── test_service.py      # 비즈니스 로직 테스트
```
```
