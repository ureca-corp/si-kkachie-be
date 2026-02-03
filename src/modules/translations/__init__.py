"""translations 도메인

Vertical Slice Architecture:
- translate_text.py: POST /translate/text
- translate_voice.py: POST /translate/voice
- list.py: GET /translations
- delete.py: DELETE /translations/{id}
- categories_list.py: GET /translation/categories
- threads_create.py: POST /translation/threads
- threads_list.py: GET /translation/threads
- threads_detail.py: GET /translation/threads/{thread_id}
- threads_delete.py: DELETE /translation/threads/{thread_id}

공유 모듈 (언더스코어 prefix):
- _models.py: Translation, Category, Thread 모델
- _repository.py: DB 접근
- _translation_service.py: 외부 번역 API
- _context_service.py: AI 컨텍스트 프롬프트 서비스
"""

from fastapi import APIRouter

from .categories_list import router as categories_list_router
from .delete import router as delete_router
from .list import router as list_router
from .threads_create import router as threads_create_router
from .threads_delete import router as threads_delete_router
from .threads_detail import router as threads_detail_router
from .threads_list import router as threads_list_router
from .translate_text import router as translate_text_router
from .translate_voice import router as translate_voice_router

# 모든 라우터 조합
router = APIRouter()
router.include_router(translate_text_router)
router.include_router(translate_voice_router)
router.include_router(list_router)
router.include_router(delete_router)
router.include_router(categories_list_router)
router.include_router(threads_create_router)
router.include_router(threads_list_router)
router.include_router(threads_detail_router)
router.include_router(threads_delete_router)

# 외부에서 사용할 수 있도록 모델 re-export
from ._models import Translation  # noqa: E402, F401
