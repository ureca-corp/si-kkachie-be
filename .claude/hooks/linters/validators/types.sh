#!/bin/bash

# Level 2: Type Check (ty via uv)

FILE_PATH="$1"

# ty check (uv run 사용)
if ! uv run ty check "$FILE_PATH" 2>&1; then
    echo "    ❌ Type errors found"
    exit 1
fi

exit 0
