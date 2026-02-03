"""{{FEATURE_DESCRIPTION}}

{{HTTP_METHOD}} {{FULL_PATH}}
"""

from fastapi import APIRouter

# ─────────────────────────────────────────────────
# Request/Response DTO
# ─────────────────────────────────────────────────

{{REQUEST_DTO}}

{{RESPONSE_DTO}}

# ─────────────────────────────────────────────────
# Service (비즈니스 로직)
# ─────────────────────────────────────────────────

{{SERVICE_FUNCTION}}

# ─────────────────────────────────────────────────
# Controller (엔드포인트)
# ─────────────────────────────────────────────────

router = APIRouter()

{{CONTROLLER_FUNCTION}}
