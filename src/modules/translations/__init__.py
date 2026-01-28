"""translations 도메인

Vertical Slice Architecture:
- translate_text.py: POST /translate/text
- translate_voice.py: POST /translate/voice
- list.py: GET /translations
- delete.py: DELETE /translations/{id}

공유 모듈 (언더스코어 prefix):
- _models.py: Translation 모델
- _repository.py: DB 접근
- _translation_service.py: 외부 번역 API
"""

from fastapi import APIRouter

from .delete import router as delete_router
from .list import router as list_router
from .translate_text import router as translate_text_router
from .translate_voice import router as translate_voice_router

# 모든 라우터 조합
router = APIRouter()
router.include_router(translate_text_router)
router.include_router(translate_voice_router)
router.include_router(list_router)
router.include_router(delete_router)

# 외부에서 사용할 수 있도록 모델 re-export
from ._models import Translation  # noqa: E402, F401
