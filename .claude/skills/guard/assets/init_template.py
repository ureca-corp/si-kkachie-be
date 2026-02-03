"""{{DOMAIN}} 도메인"""

from fastapi import APIRouter

{{FEATURE_IMPORTS}}

router = APIRouter(prefix="/{{DOMAIN}}", tags=["{{DOMAIN}}"])
{{ROUTER_INCLUDES}}
