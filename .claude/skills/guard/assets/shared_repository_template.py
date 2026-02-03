"""공유 Repository (DB 접근)"""

from sqlmodel import Session, select

from ._models import {{MODEL_CLASSES}}

{{REPOSITORY_FUNCTIONS}}
