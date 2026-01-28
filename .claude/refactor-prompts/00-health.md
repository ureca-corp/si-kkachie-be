# Health 모듈 Vertical Slice 리팩토링

## 목표
Layer-based 구조를 Vertical Slice 구조로 변환하여 기능별 응집도를 높인다.

## 특이사항
- 가장 단순한 모듈 (인증 없음, DB 없음)
- 리팩토링 연습용으로 먼저 진행 권장

## 현재 구조
```
src/modules/health/
├── __init__.py
└── controller.py      # 2개 엔드포인트

tests/modules/health/
├── __init__.py
└── test_controller.py
```

## 목표 구조
```
src/modules/health/
├── __init__.py           # router 조합
├── health.py             # GET /health
└── ready.py              # GET /health/ready

tests/modules/health/
├── __init__.py
├── test_health.py
└── test_ready.py
```

## 엔드포인트별 작업

### health.py
- **Endpoint**: GET /health
- **Response DTO**: HealthResponse (inline)
- **Service**: 없음 (단순 응답)

### ready.py
- **Endpoint**: GET /health/ready
- **Response DTO**: ReadyResponse (inline)
- **Service**: DB 연결 확인

## 검증
```bash
export $(cat .env.test | xargs) && uv run pytest tests/modules/health/ -v
uv run ty check src/modules/health/
uv run ruff check src/modules/health/
```

## 완료 조건
- [ ] 모든 테스트 통과
- [ ] 타입 체크 통과
- [ ] 스타일 체크 통과
- [ ] API 동작 동일
