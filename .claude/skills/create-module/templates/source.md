# 소스 코드 템플릿 (CSR 패턴)

> create-module 스킬에서 참조하는 소스 코드 템플릿

**레이어 구조:**
```
controller.py → service.py → repository.py → models.py
(HTTP 처리)    (비즈니스)    (데이터 접근)    (테이블)
```

---

## models.py

```python
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime

class {Domain}(SQLModel, table=True):
    """
    {도메인} 테이블

    SPEC: docs/specs/{domain}.md 참조
    """
    __tablename__ = "{domain}"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    {필드들}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## entities.py

```python
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class Create{Domain}Request(BaseModel):
    """{domain} 생성 요청"""
    {필드들}

class Update{Domain}Request(BaseModel):
    """{domain} 수정 요청"""
    {필드들}

class {Domain}Response(BaseModel):
    """{domain} 응답"""
    id: UUID
    {필드들}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

---

## repository.py

> **역할: 데이터 접근만** (비즈니스 로직 금지)

```python
from sqlmodel import Session, select
from uuid import UUID

from .models import {Domain}

async def create(session: Session, {domain}: {Domain}) -> {Domain}:
    """생성"""
    session.add({domain})
    await session.commit()
    await session.refresh({domain})
    return {domain}

async def get_by_id(session: Session, {domain}_id: UUID) -> {Domain} | None:
    """ID로 조회"""
    return await session.get({Domain}, {domain}_id)

async def get_all(
    session: Session,
    offset: int = 0,
    limit: int = 20,
) -> list[{Domain}]:
    """목록 조회"""
    stmt = select({Domain}).offset(offset).limit(limit)
    result = await session.exec(stmt)
    return result.all()

async def update(session: Session, {domain}: {Domain}) -> {Domain}:
    """수정"""
    session.add({domain})
    await session.commit()
    await session.refresh({domain})
    return {domain}

async def delete(session: Session, {domain}: {Domain}) -> None:
    """삭제"""
    await session.delete({domain})
    await session.commit()
```

---

## service.py

> **역할: 비즈니스 로직** (검증, 변환, 트랜잭션 등)

```python
from fastapi import HTTPException
from sqlmodel import Session
from uuid import UUID

from . import repository
from .models import {Domain}
from .entities import Create{Domain}Request, Update{Domain}Request

async def create_{domain}(
    session: Session,
    request: Create{Domain}Request,
) -> {Domain}:
    """
    {domain} 생성

    비즈니스 로직:
    - 중복 검증 (필요시)
    - 데이터 변환
    """
    {domain} = {Domain}(**request.model_dump())
    return await repository.create(session, {domain})

async def get_{domain}(session: Session, {domain}_id: UUID) -> {Domain}:
    """
    {domain} 조회

    비즈니스 로직:
    - 존재 여부 검증
    """
    {domain} = await repository.get_by_id(session, {domain}_id)
    if not {domain}:
        raise HTTPException(404, "{도메인}을 찾을 수 없어요")
    return {domain}

async def list_{domain}s(
    session: Session,
    offset: int = 0,
    limit: int = 20,
) -> list[{Domain}]:
    """{domain} 목록 조회"""
    return await repository.get_all(session, offset, limit)

async def update_{domain}(
    session: Session,
    {domain}_id: UUID,
    request: Update{Domain}Request,
) -> {Domain}:
    """
    {domain} 수정

    비즈니스 로직:
    - 존재 여부 검증
    - 부분 업데이트
    """
    {domain} = await get_{domain}(session, {domain}_id)

    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr({domain}, key, value)

    return await repository.update(session, {domain})

async def delete_{domain}(session: Session, {domain}_id: UUID) -> None:
    """
    {domain} 삭제

    비즈니스 로직:
    - 존재 여부 검증
    - 연관 데이터 처리 (필요시)
    """
    {domain} = await get_{domain}(session, {domain}_id)
    await repository.delete(session, {domain})
```

---

## controller.py

> **역할: HTTP 요청/응답 처리만** (비즈니스 로직 금지)

```python
from fastapi import APIRouter, Depends
from sqlmodel import Session
from uuid import UUID

from src.core.database import get_session
from src.core.response import ApiResponse, Status
from . import service
from .entities import (
    Create{Domain}Request,
    Update{Domain}Request,
    {Domain}Response,
)

router = APIRouter(prefix="/{domain}", tags=["{domain}"])

@router.post("/", response_model=ApiResponse[{Domain}Response], status_code=201)
async def create(
    request: Create{Domain}Request,
    session: Session = Depends(get_session),
):
    """{도메인} 생성"""
    {domain} = await service.create_{domain}(session, request)
    return ApiResponse(
        status=Status.SUCCESS,
        message="{도메인} 생성이 완료됐어요",
        data={Domain}Response.model_validate({domain}),
    )

@router.get("/{{{domain}_id}}", response_model=ApiResponse[{Domain}Response])
async def get(
    {domain}_id: UUID,
    session: Session = Depends(get_session),
):
    """{도메인} 조회"""
    {domain} = await service.get_{domain}(session, {domain}_id)
    return ApiResponse(
        status=Status.SUCCESS,
        message="{도메인} 조회가 완료됐어요",
        data={Domain}Response.model_validate({domain}),
    )

@router.get("/", response_model=ApiResponse[list[{Domain}Response]])
async def list(
    offset: int = 0,
    limit: int = 20,
    session: Session = Depends(get_session),
):
    """{도메인} 목록 조회"""
    {domain}s = await service.list_{domain}s(session, offset, limit)
    return ApiResponse(
        status=Status.SUCCESS,
        message="{도메인} 목록 조회가 완료됐어요",
        data=[{Domain}Response.model_validate(d) for d in {domain}s],
    )

@router.put("/{{{domain}_id}}", response_model=ApiResponse[{Domain}Response])
async def update(
    {domain}_id: UUID,
    request: Update{Domain}Request,
    session: Session = Depends(get_session),
):
    """{도메인} 수정"""
    {domain} = await service.update_{domain}(session, {domain}_id, request)
    return ApiResponse(
        status=Status.SUCCESS,
        message="{도메인} 수정이 완료됐어요",
        data={Domain}Response.model_validate({domain}),
    )

@router.delete("/{{{domain}_id}}", status_code=204)
async def delete(
    {domain}_id: UUID,
    session: Session = Depends(get_session),
):
    """{도메인} 삭제"""
    await service.delete_{domain}(session, {domain}_id)
```
