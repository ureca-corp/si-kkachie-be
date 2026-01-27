#!/bin/bash

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Python 파일 검증 (단일 파일)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

set -e

FILE_PATH="$1"

if [ -z "$FILE_PATH" ]; then
    echo "Usage: $0 <python_file>"
    exit 1
fi

VALIDATORS_DIR="$(dirname "$0")/validators"

# Level 0: Syntax
echo "  Level 0: Syntax..."
"$VALIDATORS_DIR/syntax.sh" "$FILE_PATH" || exit 1

# Level 1: Style (+ auto-fix)
echo "  Level 1: Style..."
"$VALIDATORS_DIR/style.sh" "$FILE_PATH" || exit 1

# Level 2: Type
echo "  Level 2: Type..."
"$VALIDATORS_DIR/types.sh" "$FILE_PATH" || exit 1

# Level 3: Guidelines
echo "  Level 3: Guidelines..."
"$VALIDATORS_DIR/guidelines.sh" "$FILE_PATH" || exit 1

echo "  ✅ All levels passed"
exit 0
