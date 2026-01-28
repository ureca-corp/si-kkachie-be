---
name: Render Troubleshooting
description: Render 배포 문제 해결에 대한 가이드. Render 오류, 배포 실패, 연결 문제 등을 해결할 때 이 스킬을 사용한다.
version: 1.0.0
---

# Render Troubleshooting Guide

Render 배포 환경에서 발생하는 일반적인 문제와 해결 방법을 제공한다.

## 일반적인 오류 유형

### 1. 데이터베이스 연결 오류

#### Supabase + Render IPv6 문제
**증상:**
```
sqlalchemy.exc.OperationalError: connection to server at "db.xxx.supabase.co"
(IPv6 address), port 5432 failed: Network is unreachable
```

**원인:** Render 무료 티어는 IPv6를 지원하지 않으나, Supabase 직접 연결은 IPv6를 사용

**해결:**
1. Supabase Dashboard → Project Settings → Database
2. "Session pooler" 연결 문자열 복사 (IPv4 사용)
3. Render 환경 변수 `DATABASE_URL` 업데이트

```python
# 직접 연결 (IPv6) - 작동 안함
postgresql://postgres.xxx:password@db.xxx.supabase.co:5432/postgres

# Session pooler (IPv4) - 작동함
postgresql://postgres.xxx:password@aws-0-xxx.pooler.supabase.com:5432/postgres
```

#### 연결 풀 고갈
**증상:**
```
QueuePool limit of size X overflow Y reached
```

**해결:**
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True
)
```

### 2. 빌드 실패

#### 의존성 설치 실패
**증상:**
```
ERROR: Could not find a version that satisfies the requirement xxx
```

**해결:**
- `requirements.txt` 또는 `pyproject.toml` 확인
- 버전 충돌 해결
- Python 버전 호환성 확인

#### 메모리 부족
**증상:**
```
Killed (out of memory)
```

**해결:**
- 빌드 최적화: `--no-cache-dir` 플래그 사용
- 불필요한 의존성 제거
- Render 플랜 업그레이드 고려

### 3. 런타임 오류

#### 환경 변수 누락
**증상:**
```
KeyError: 'SOME_REQUIRED_VAR'
```

**해결:**
1. Render Dashboard → Service → Environment
2. 필요한 환경 변수 추가
3. 서비스 재배포

#### 포트 바인딩 실패
**증상:**
```
No open ports detected
```

**해결:**
```python
# 반드시 $PORT 환경 변수 사용
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 4. Health Check 실패

**증상:**
```
Health check failed
```

**원인:**
- 앱 시작 시간이 너무 오래 걸림
- Health check 경로가 없음
- Health check가 에러 반환

**해결:**
1. Health check 엔드포인트 구현:
```python
@app.get("/health")
def health():
    return {"status": "ok"}
```

2. Render 설정에서 Health Check Path 설정: `/health`

## Render MCP 도구 사용법

### 서비스 목록 조회
```
mcp__render__list_services()
```

### 로그 조회
```
mcp__render__list_logs(
    resource: ["srv-xxx"],
    limit: 100,
    direction: "backward"
)
```

### 배포 상태 조회
```
mcp__render__get_deploy(
    serviceId: "srv-xxx",
    deployId: "dep-xxx"
)
```

### 환경 변수 업데이트
```
mcp__render__update_environment_variables(
    serviceId: "srv-xxx",
    envVars: [{"key": "VAR_NAME", "value": "value"}]
)
```

## 배포 상태 코드

| 상태 | 설명 |
|------|------|
| `created` | 배포 생성됨 |
| `build_in_progress` | 빌드 중 |
| `update_in_progress` | 서비스 업데이트 중 |
| `live` | 서비스 라이브 |
| `deactivated` | 비활성화됨 |
| `build_failed` | 빌드 실패 |
| `update_failed` | 업데이트 실패 |
| `canceled` | 취소됨 |

## 모니터링 베스트 프랙티스

1. **로그 레벨 설정**: 프로덕션에서는 INFO 이상만 로그
2. **구조화된 로그**: JSON 형식 권장
3. **Health Check**: 단순하고 빠른 응답
4. **환경 변수**: 민감 정보는 절대 코드에 하드코딩 금지
