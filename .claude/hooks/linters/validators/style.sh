#!/bin/bash

# Level 1: Style Check (ruff via uv)

FILE_PATH="$1"

# ruff check (uv run 사용)
if ! uv run ruff check "$FILE_PATH" 2>&1; then
    echo "    ⚠️  Style issues found - attempting auto-fix..."

    # auto-fix 시도
    if uv run ruff check --fix "$FILE_PATH" 2>&1; then
        echo "    ✅ Auto-fixed"
        exit 0
    else
        echo "    ❌ Auto-fix failed"
        exit 1
    fi
fi

exit 0
