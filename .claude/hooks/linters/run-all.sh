#!/bin/bash

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 전체 프로젝트 검증 (Phase 완료 시)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

total=0
passed=0
failed=0

echo "Searching Python files..."

# src/ 아래 모든 .py 파일 찾기
while IFS= read -r file; do
    ((total++))
    
    echo ""
    echo "[$total] Checking: $file"
    
    if .claude/hooks/linters/run-python.sh "$file"; then
        ((passed++))
        echo "  ✅ Passed"
    else
        ((failed++))
        echo "  ❌ Failed"
    fi
done < <(find src -name "*.py" -type f 2>/dev/null)

# 결과 리포트
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Validation Report"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Total files:  $total"
echo "✅ Passed:    $passed"
echo "❌ Failed:    $failed"
echo ""

if [ $failed -eq 0 ]; then
    echo "🎉 All files passed validation!"
    exit 0
else
    echo "⚠️  $failed file(s) need attention"
    exit 1
fi
