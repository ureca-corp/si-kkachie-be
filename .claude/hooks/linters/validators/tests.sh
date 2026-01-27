#!/bin/bash

# Level 4: Tests (pytest)

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$PROJECT_ROOT"

# pytest 확인
if ! command -v pytest &> /dev/null; then
    echo "    ⚠️  pytest not installed - skipping tests"
    exit 0
fi

# 테스트 실행
if ! pytest tests/ -v 2>&1; then
    echo "    ❌ Tests failed"
    exit 1
fi

echo "    ✅ All tests passed"
exit 0
