---
name: fix
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
Task tool을 사용하여 `log-analyzer` 에이전트를 호출한다:
- 수집된 로그를 전달
- 에러 패턴 분석 요청
- 수정 방안 도출 요청

### Step 3: 코드 수정 및 PR 생성
log-analyzer 에이전트가 문제를 파악하면:
1. `fix/render-{timestamp}` 형식의 브랜치 생성
2. 문제 수정 코드 작성
3. 커밋 및 푸시
4. main 브랜치로 PR 생성

### Step 4: 배포 모니터링 에이전트 호출
Task tool을 사용하여 `deploy-monitor` 에이전트를 호출한다:
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
/render-autofix:fix
/render-autofix:fix kkachie-be
```

## 중요 사항

- 전체 워크플로우는 자동으로 진행되지만, 중요한 결정 사항은 사용자에게 확인을 요청한다
- 코드리뷰에서 수정 요청이 있으면 자동으로 반영한다
- 서비스가 라이브될 때까지 모니터링을 계속한다
