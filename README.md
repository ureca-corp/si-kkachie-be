## Kkachie Backend (FastAPI)

### Quickstart

#### 1) Install

This project uses Python 3.12+ and `uv`.

```bash
uv sync
```

#### 2) Configure env

Copy `.env.example` to `.env` and set:

- `DATABASE_URL` - PostgreSQL connection string
- `AUTH_BACKEND=supabase`
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase anon key
- `SUPABASE_JWKS_URL` (recommended) - For local JWT verification

#### 3) Run DB migrations

```bash
uv run alembic upgrade head
```

#### 4) Start API

```bash
uv run uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Supabase Auth integration

- The client (mobile/web) authenticates with **Supabase Auth** and sends `Authorization: Bearer <access_token>` to this API.
- The backend validates the token and maps the Supabase `user.id` to `profiles.user_id`.
- Token validation: JWKS URL configured → local signature verification, otherwise → `supabase.auth.get_user(token)` API call.

#### Verify token endpoint

```bash
curl -X POST "http://localhost:8000/auth/verify-token" \
  -H "Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}"
```

### Tests

```bash
uv run pytest -q
```

Uses in-memory SQLite by default. Set `DATABASE_URL` for PostgreSQL.
