#!/bin/bash

# Level 3: Guidelines Check (Custom)

FILE_PATH="$1"

has_error=0

# Check 1: No String Magic (Status 사용)
if grep -qE 'status\s*=\s*["'\'']SUCCESS["'\'']' "$FILE_PATH"; then
    echo "    ❌ String magic detected: status = \"SUCCESS\""
    echo "       Use: status = Status.SUCCESS"
    has_error=1
fi

# Check 2: Korean messages (macOS 호환)
if grep -q 'message\s*=' "$FILE_PATH"; then
    # 한글이 포함된 message가 있는지 확인 (macOS grep 호환)
    if ! grep -E 'message\s*=\s*["\x27].*' "$FILE_PATH" | grep -q '[가-힣]'; then
        echo "    ⚠️  No Korean message found"
        echo "       Use user-friendly Korean messages"
        # Warning only, not error
    fi
fi

if [ $has_error -eq 1 ]; then
    exit 1
fi

exit 0
