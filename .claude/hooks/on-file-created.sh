#!/bin/bash

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Hook: PostToolUse (Write)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

set -e

# Hook Input 파싱
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_response.filePath // ""')

if [ -z "$FILE_PATH" ] || [[ ! "$FILE_PATH" =~ \.py$ ]]; then
    exit 0
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 LINT: Validating $FILE_PATH"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Python 검증 실행
"$CLAUDE_PROJECT_DIR/.claude/hooks/linters/run-python.sh" "$FILE_PATH"

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "✅ LINT: All checks passed"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
    echo ""
    echo "❌ LINT: Validation failed"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # JSON 응답으로 Claude에게 피드백
    cat << EOF
{
  "decision": "block",
  "reason": "Lint validation failed. Please fix the issues above using str_replace."
}
EOF
fi

exit $exit_code
