# Render Auto-Fix Plugin

Render 배포 오류를 자동으로 감지하고 수정하는 Claude Code 플러그인입니다.

## 기능

- **자동 로그 분석**: Render MCP를 통해 배포 로그를 수집하고 에러를 분석
- **코드 자동 수정**: 발견된 문제를 자동으로 수정
- **PR 생성 및 관리**: 수정 사항을 별도 브랜치에 커밋하고 PR 생성
- **코드리뷰 모니터링**: 3분마다 PR 상태를 확인하고 수정 요청 반영
- **배포 완료 확인**: 머지 후 서비스가 라이브될 때까지 모니터링

## 사용법

```bash
# 기본 사용 (서비스 선택 프롬프트)
/render-autofix:fix

# 특정 서비스 지정
/render-autofix:fix kkachie-be
```

## 워크플로우

```
1. 로그 수집 (Render MCP)
   ↓
2. 에러 분석 (log-analyzer 에이전트)
   ↓
3. 코드 수정
   ↓
4. 브랜치 생성 & 커밋 & 푸시
   ↓
5. PR 생성
   ↓
6. 코드리뷰 모니터링 (3분 간격)
   ↓
7. 수정 요청 반영 (있는 경우)
   ↓
8. PR 머지
   ↓
9. 배포 모니터링 (10초 간격)
   ↓
10. 서비스 라이브 확인
    ↓
완료!
```

## 컴포넌트

### Commands
- `/render-autofix:fix` - 전체 워크플로우 실행

### Agents
- `log-analyzer` - 로그 분석 및 코드 수정
- `deploy-monitor` - PR 및 배포 모니터링

### Skills
- `render-troubleshooting` - Render 문제 해결 가이드

## 사전 요구 사항

1. **Render MCP 서버 설정**
   - `mcp__render__*` 도구 사용 가능해야 함

2. **GitHub CLI 인증**
   ```bash
   gh auth login
   ```

3. **Git 설정**
   - 커밋 권한이 있는 저장소에서 실행

## 지원하는 오류 유형

- 데이터베이스 연결 오류 (Supabase IPv6 문제 등)
- 모듈 임포트 에러
- 환경 변수 누락
- 빌드 실패
- Health check 실패

## 설치

이 플러그인은 프로젝트 로컬 플러그인으로 `.claude/plugins/render-autofix/`에 위치합니다.

Claude Code 시작 시 자동으로 로드됩니다.

## 라이선스

MIT
