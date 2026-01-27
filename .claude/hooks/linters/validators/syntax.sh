#!/bin/bash

# Level 0: Syntax Check (uv run 사용)

FILE_PATH="$1"

if ! uv run python -m py_compile "$FILE_PATH" 2>&1; then
    echo "    ❌ Syntax error detected"
    exit 1
fi

exit 0
