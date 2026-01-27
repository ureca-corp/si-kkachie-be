#!/bin/bash
# 아키텍처 검증 스크립트
# 순환참조 체크 및 다이어그램 자동 생성

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIAGRAMS_DIR="$PROJECT_ROOT/docs/diagrams"
SRC_DIR="$PROJECT_ROOT/src"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "╔══════════════════════════════════════════════════════════╗"
echo "║              ARCHITECTURE VERIFICATION                    ║"
echo "╚══════════════════════════════════════════════════════════╝"

# 다이어그램 디렉토리 생성
mkdir -p "$DIAGRAMS_DIR"

# ═══════════════════════════════════════════════════════════════
# Step 1: 순환참조 체크 (pydeps)
# ═══════════════════════════════════════════════════════════════
echo ""
echo "=== Step 1: 순환참조 체크 (pydeps) ==="

if [ -d "$SRC_DIR" ]; then
    # --show-cycles 출력이 비어있으면 순환참조 없음
    CYCLES=$(uv run pydeps "$SRC_DIR" --show-cycles --no-show 2>&1)
    if [ -z "$CYCLES" ]; then
        echo -e "${GREEN}✅ PASS: 순환참조 없음${NC}"
    else
        echo -e "${RED}❌ FAIL: 순환참조 발견!${NC}"
        echo ""
        echo "순환참조 상세:"
        echo "$CYCLES"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  SKIP: src/ 디렉토리 없음${NC}"
fi

# ═══════════════════════════════════════════════════════════════
# Step 2: 모듈 의존성 그래프 생성 (pydeps)
# ═══════════════════════════════════════════════════════════════
echo ""
echo "=== Step 2: 모듈 의존성 그래프 (pydeps) ==="

if [ -d "$SRC_DIR" ]; then
    uv run pydeps "$SRC_DIR" \
        --rankdir TB \
        --max-bacon=2 \
        --cluster \
        --no-show \
        -o "$DIAGRAMS_DIR/module-dependencies.svg" 2>/dev/null && \
    echo -e "${GREEN}✅ 생성: docs/diagrams/module-dependencies.svg${NC}" || \
    echo -e "${YELLOW}⚠️  WARN: 의존성 그래프 생성 실패${NC}"
else
    echo -e "${YELLOW}⚠️  SKIP: src/ 디렉토리 없음${NC}"
fi

# ═══════════════════════════════════════════════════════════════
# Step 3: 클래스 다이어그램 생성 (pyreverse → Mermaid)
# ═══════════════════════════════════════════════════════════════
echo ""
echo "=== Step 3: 클래스 다이어그램 (pyreverse → Mermaid) ==="

if [ -d "$SRC_DIR" ]; then
    # Mermaid 형식으로 출력 (AI 에이전트 친화적)
    uv run pyreverse "$SRC_DIR" \
        -o mmd \
        -d "$DIAGRAMS_DIR" \
        -p project 2>/dev/null && \
    echo -e "${GREEN}✅ 생성: docs/diagrams/classes_project.mmd${NC}" || \
    echo -e "${YELLOW}⚠️  WARN: 클래스 다이어그램 생성 실패${NC}"
else
    echo -e "${YELLOW}⚠️  SKIP: src/ 디렉토리 없음${NC}"
fi

# ═══════════════════════════════════════════════════════════════
# Step 4: Pydantic 모델 ER 다이어그램 (erdantic)
# ═══════════════════════════════════════════════════════════════
echo ""
echo "=== Step 4: Pydantic 모델 ER 다이어그램 (erdantic) ==="

# models.py 파일들 찾기
MODELS_FILES=$(find "$SRC_DIR" -name "models.py" 2>/dev/null || true)

if [ -n "$MODELS_FILES" ]; then
    for model_file in $MODELS_FILES; do
        # 도메인 이름 추출 (src/modules/users/models.py → users)
        domain_name=$(echo "$model_file" | grep -o 'modules/[^/]*' | cut -d'/' -f2 || echo "models")

        echo "  처리 중: $model_file ($domain_name)"

        # erdantic으로 다이어그램 생성
        uv run python -c "
import erdantic as erd
import importlib.util
import sys

# 모듈 직접 로드
spec = importlib.util.spec_from_file_location('models', '$model_file')
module = importlib.util.module_from_spec(spec)
sys.modules['models'] = module
spec.loader.exec_module(module)

# 모듈에서 SQLModel/Pydantic 클래스 찾기
from sqlmodel import SQLModel
from pydantic import BaseModel

for name in dir(module):
    obj = getattr(module, name)
    if isinstance(obj, type) and issubclass(obj, (SQLModel, BaseModel)) and obj not in (SQLModel, BaseModel):
        try:
            diagram = erd.create(obj)
            diagram.draw('$DIAGRAMS_DIR/${domain_name}_erd.png')
            print(f'  ✅ 생성: docs/diagrams/${domain_name}_erd.png')
            break
        except Exception as e:
            continue
" 2>/dev/null || echo -e "  ${YELLOW}⚠️  WARN: $domain_name ER 다이어그램 생성 실패${NC}"
    done
else
    echo -e "${YELLOW}⚠️  SKIP: models.py 파일 없음${NC}"
fi

# ═══════════════════════════════════════════════════════════════
# 결과 요약
# ═══════════════════════════════════════════════════════════════
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                    VERIFICATION COMPLETE                  ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║ 생성된 파일:                                              ║"

if [ -f "$DIAGRAMS_DIR/module-dependencies.svg" ]; then
    echo "║  - docs/diagrams/module-dependencies.svg (의존성)        ║"
fi
if [ -f "$DIAGRAMS_DIR/classes_project.mmd" ]; then
    echo "║  - docs/diagrams/classes_project.mmd (클래스, Mermaid)   ║"
fi
for erd_file in "$DIAGRAMS_DIR"/*_erd.png; do
    if [ -f "$erd_file" ]; then
        echo "║  - $(basename "$erd_file") (ER 다이어그램)                  ║"
    fi
done

echo "╚══════════════════════════════════════════════════════════╝"
