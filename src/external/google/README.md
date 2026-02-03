# Google Vertex AI Provider

Google Cloud Vertex AI (Gemini) 연동 모듈

## 연동 준비 완료 API 목록

| API | 설명 | 모델 |
|-----|------|------|
| Content Generation | 범용 콘텐츠 생성 | Gemini 2.0 Flash Lite |
| Translation | 컨텍스트 기반 AI 번역 | Gemini 2.0 Flash Lite |

## 필요한 환경 변수

| 변수명 | 설명 |
|--------|------|
| `GOOGLE_CLOUD_PROJECT` | Google Cloud 프로젝트 ID |
| `GOOGLE_CREDENTIALS_JSON` | 서비스 계정 키 JSON (서버용) |
| `GOOGLE_APPLICATION_CREDENTIALS` | 서비스 계정 키 파일 경로 (로컬용) |

## 사용법

```python
from src.external.google import get_vertex_provider, get_async_vertex_provider

# 동기
provider = get_vertex_provider()
if provider:
    # 범용 생성
    response = provider.generate_content("서울의 관광 명소를 추천해주세요")

    # 번역
    translated = provider.translate(
        text="Hello, world!",
        source_lang="en",
        target_lang="ko",
        context="웹사이트 인사말"  # 선택
    )

# 비동기
async_provider = get_async_vertex_provider()
if async_provider:
    response = await async_provider.generate_content("...")
    translated = await async_provider.translate(...)
```

## 공식 문서

- [Vertex AI Gemini API](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/gemini)
- [Vertex AI Python SDK](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal)
