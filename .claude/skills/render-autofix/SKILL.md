---
name: render-autofix
description: Render 배포 오류를 자동으로 감지하고 수정하는 전체 워크플로우를 실행합니다
argument-hint: "[service-name]"
allowed-tools:
  - Task
  - Bash
  - Read
  - Edit
  - Write
  - Glob
  - Grep
  - mcp__render__*
  - AskUserQuestion
---

# Render Auto-Fix Workflow

Render 배포 오류를 자동으로 감지, 분석, 수정하고 PR을 생성하여 머지까지 완료하는 전체 워크플로우를 실행한다.

## 워크플로우 단계

### Step 1: 서비스 선택 및 로그 수집
1. 인자로 service-name이 주어지지 않았다면 `mcp__render__list_services`로 서비스 목록을 가져온다
2. 여러 서비스가 있다면 사용자에게 선택을 요청한다
3. 선택된 서비스의 최근 로그를 `mcp__render__list_logs`로 수집한다 (limit: 100, direction: backward)

### Step 2: 로그 분석 에이전트 호출
Task tool을 사용하여 `render-log-analyzer` 에이전트를 호출한다:
- 수집된 로그를 전달
- 에러 패턴 분석 요청
- 수정 방안 도출 요청

### Step 3: 코드 수정 및 PR 생성
render-log-analyzer 에이전트가 문제를 파악하면:
1. `fix/render-{timestamp}` 형식의 브랜치 생성
2. 문제 수정 코드 작성
3. 커밋 및 푸시
4. main 브랜치로 PR 생성

### Step 4: 배포 모니터링 에이전트 호출
Task tool을 사용하여 `render-deploy-monitor` 에이전트를 호출한다:
- PR URL 전달
- 3분마다 코드리뷰 상태 확인
- 수정 요청이 있으면 반영 후 재푸시
- 승인되면 머지 진행
- 배포 완료까지 모니터링

### Step 5: 완료 보고
- 수정된 내용 요약
- PR URL
- 서비스 라이브 상태 확인 결과

## 사용 예시

```
/render-autofix
/render-autofix kkachie-be
```

## Render Troubleshooting Guide

### 일반적인 오류 유형

#### 1. 데이터베이스 연결 오류

**Supabase + Render IPv6 문제**
```
sqlalchemy.exc.OperationalError: connection to server at "db.xxx.supabase.co"
(IPv6 address), port 5432 failed: Network is unreachable
```

**해결:** Supabase Session pooler 연결 문자열 사용 (IPv4)

#### 2. 빌드 실패
- 의존성 설치 실패 → requirements.txt/pyproject.toml 확인
- 메모리 부족 → `--no-cache-dir` 사용

#### 3. 런타임 오류
- 환경 변수 누락 → Render Dashboard에서 추가
- 포트 바인딩 → `$PORT` 환경 변수 사용

#### 4. Health Check 실패
- `/health` 엔드포인트 구현 필요

### 배포 상태 코드

| 상태 | 설명 |
|------|------|
| `build_in_progress` | 빌드 중 |
| `update_in_progress` | 서비스 업데이트 중 |
| `live` | 서비스 라이브 |
| `build_failed` | 빌드 실패 |
| `update_failed` | 업데이트 실패 |

## 중요 사항

- 전체 워크플로우는 자동으로 진행되지만, 중요한 결정 사항은 사용자에게 확인을 요청한다
- 코드리뷰에서 수정 요청이 있으면 자동으로 반영한다
- 서비스가 라이브될 때까지 모니터링을 계속한다
