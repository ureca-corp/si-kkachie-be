# Run Migration

모델 변경 시 Alembic 마이그레이션을 생성하고 적용합니다.

## 사용 시점

Phase 4 (코드 생성) 내부에서 모델 생성/수정 직후 자동 호출됩니다.

```
모델 생성/수정
    ↓
run-migration (이 스킬)
    ↓
테스트 실행
```

## 워크플로우

### Step 1: 변경 감지

```bash
uv run alembic check
```

- 출력이 없으면 → 변경 없음, 종료
- "FAILED" 출력 → 마이그레이션 필요

### Step 2: 마이그레이션 파일 생성

```bash
uv run alembic revision --autogenerate -m "변경 설명"
```

**메시지 컨벤션:**
- 새 모델: `add {model_name} table`
- 컬럼 추가: `add {column} to {table}`
- 컬럼 수정: `alter {column} in {table}`
- 컬럼 삭제: `drop {column} from {table}`

### Step 3: 생성된 파일 검토

`migrations/versions/` 디렉토리에서 새로 생성된 파일 확인:

```python
def upgrade() -> None:
    # 예상되는 변경 확인
    op.create_table(...)
    op.add_column(...)

def downgrade() -> None:
    # 롤백 로직 확인
    op.drop_column(...)
    op.drop_table(...)
```

**검토 포인트:**
- [ ] upgrade()가 의도한 변경만 포함하는지
- [ ] downgrade()가 올바르게 롤백하는지
- [ ] 불필요한 변경이 포함되지 않았는지

### Step 4: 마이그레이션 적용

```bash
uv run alembic upgrade head
```

### Step 5: 검증

```bash
# 현재 상태 확인
uv run alembic current

# 히스토리 확인
uv run alembic history --verbose
```

## 자주 사용하는 명령어

| 명령어 | 설명 |
|--------|------|
| `uv run alembic check` | 변경 감지 |
| `uv run alembic revision --autogenerate -m "msg"` | 마이그레이션 생성 |
| `uv run alembic upgrade head` | 최신으로 적용 |
| `uv run alembic downgrade -1` | 한 단계 롤백 |
| `uv run alembic current` | 현재 버전 확인 |
| `uv run alembic history` | 히스토리 확인 |

## 주의사항

### SQLite 제한

SQLite는 일부 ALTER 작업을 지원하지 않습니다:

```python
# 지원 안 됨
op.alter_column(...)  # 컬럼 타입 변경
op.drop_column(...)   # 컬럼 삭제 (batch mode 필요)

# 해결: batch mode 사용
with op.batch_alter_table('users') as batch_op:
    batch_op.drop_column('old_column')
```

### 데이터 마이그레이션

스키마 변경 외에 데이터 변환이 필요한 경우:

```python
def upgrade() -> None:
    # 1. 새 컬럼 추가 (nullable)
    op.add_column('users', sa.Column('full_name', sa.String()))

    # 2. 데이터 마이그레이션
    connection = op.get_bind()
    connection.execute(
        sa.text("UPDATE users SET full_name = first_name || ' ' || last_name")
    )

    # 3. NOT NULL 적용
    op.alter_column('users', 'full_name', nullable=False)
```

## env.py 모델 등록

새 모델을 추가할 때 `migrations/env.py`에 import 추가 필수:

```python
# migrations/env.py
from src.modules.{domain}.models import {Model}  # noqa: F401
```

autogenerate가 모델을 인식하려면 반드시 import되어야 합니다.

## 에러 처리

### "Target database is not up to date"

```bash
# 먼저 현재 상태로 업그레이드
uv run alembic upgrade head

# 그 다음 새 마이그레이션 생성
uv run alembic revision --autogenerate -m "msg"
```

### "Can't locate revision"

```bash
# 마이그레이션 히스토리 초기화 (개발 환경만)
rm -rf migrations/versions/*
uv run alembic revision --autogenerate -m "initial"
uv run alembic upgrade head
```
