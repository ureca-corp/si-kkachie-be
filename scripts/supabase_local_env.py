#!/usr/bin/env python3
"""Generate project .env from Supabase Local.

This script reads `supabase status -o env` output and writes a generated block
into the project root `.env` file (which is gitignored).

It is safe to run multiple times (idempotent).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


BEGIN_MARKER = "# --- supabase local (generated) ---"
END_MARKER = "# --- /supabase local (generated) ---"


def _parse_env_lines(text: str) -> dict[str, str]:
    env: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip()
        if not k:
            continue
        env[k] = v
    return env


def _build_generated_block(
    *,
    supabase_env: dict[str, str],
    storage_bucket: str,
) -> str:
    required = ["API_URL", "DB_URL", "ANON_KEY", "SERVICE_ROLE_KEY", "JWT_SECRET"]
    missing = [k for k in required if k not in supabase_env or not supabase_env[k]]
    if missing:
        missing_str = ", ".join(missing)
        raise RuntimeError(
            "supabase status output missing required vars: " f"{missing_str}"
        )

    lines = [
        BEGIN_MARKER,
        "AUTH_BACKEND=supabase",
        f"DATABASE_URL={supabase_env['DB_URL']}",
        f"SUPABASE_URL={supabase_env['API_URL']}",
        f"SUPABASE_KEY={supabase_env['ANON_KEY']}",
        f"SUPABASE_SERVICE_KEY={supabase_env['SERVICE_ROLE_KEY']}",
        f"SUPABASE_JWT_SECRET={supabase_env['JWT_SECRET']}",
        "STORAGE_BACKEND=supabase",
        f"SUPABASE_STORAGE_BUCKET={storage_bucket}",
        END_MARKER,
        "",
    ]
    return "\n".join(lines)


def _replace_or_append_block(*, original: str, block: str) -> str:
    if BEGIN_MARKER in original and END_MARKER in original:
        start = original.index(BEGIN_MARKER)
        end = original.index(END_MARKER)
        end = end + len(END_MARKER)
        before = original[:start].rstrip("\n")
        after = original[end:].lstrip("\n")
        if before:
            before += "\n\n"
        return f"{before}{block}{after}"

    # Append at end
    original = original.rstrip("\n")
    if original:
        original += "\n\n"
    return original + block


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Write project .env from `supabase status -o env`."
    )
    parser.add_argument(
        "--env-path",
        default=".env",
        help="Path to write env file (default: .env)",
    )
    parser.add_argument(
        "--bucket",
        default="profiles",
        help="Supabase storage bucket name (default: profiles)",
    )
    args = parser.parse_args()

    try:
        proc = subprocess.run(
            ["supabase", "status", "-o", "env"],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as e:
        print(
            "ERROR: `supabase` CLI not found. Install Supabase CLI first.",
            file=sys.stderr,
        )
        return 1
    except subprocess.CalledProcessError as e:
        stderr = (e.stderr or "").strip()
        msg = "ERROR: Supabase local is not running.\n\nRun:\n  supabase start\n"
        if stderr:
            msg += f"\nDetails:\n{stderr}\n"
        print(msg, file=sys.stderr)
        return 1

    supabase_env = _parse_env_lines(proc.stdout)
    try:
        block = _build_generated_block(
            supabase_env=supabase_env,
            storage_bucket=args.bucket,
        )
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    env_path = Path(args.env_path)
    original = env_path.read_text(encoding="utf-8") if env_path.exists() else ""
    updated = _replace_or_append_block(original=original, block=block)
    env_path.write_text(updated, encoding="utf-8")

    print(f"Wrote Supabase Local env block to {env_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

