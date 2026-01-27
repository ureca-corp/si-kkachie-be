## Kkachie Backend (FastAPI)

### Quickstart

#### 1) Install

This project uses Python 3.12+ and `uv`.

```bash
uv sync
```

#### 2) Configure env

If you use Supabase Local, you can auto-generate `.env`:

```bash
supabase start
uv run python scripts/supabase_local_env.py
```

Or copy `.env.example` to `.env` and set at least:

- `DATABASE_URL`
- `AUTH_BACKEND=supabase`
- `SUPABASE_URL`
- `SUPABASE_KEY` (publishable/anon key)
- (optional, recommended) `SUPABASE_JWT_SECRET` (Project Settings → API → JWT secret)

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
- Token validation is done by calling `supabase.auth.get_user(token)` on each request.

#### Google Login (Supabase Local)

This backend does **not** implement Google OAuth directly. Google login is handled by **Supabase Auth** (client-side), and the backend only verifies the resulting token.

To enable Google login in Supabase Local:

1) Create Google OAuth credentials in Google Cloud Console and add this redirect URI:
- `http://127.0.0.1:54321/auth/v1/callback`

2) Create `supabase/.env.local` from the example and fill values:

```bash
cp supabase/.env.local.example supabase/.env.local
```

3) Restart Supabase Local:

```bash
supabase stop
supabase start
```

#### Verify token endpoint

```bash
curl -X POST "http://localhost:8000/auth/verify-token" \
  -H "Authorization: Bearer ${SUPABASE_ACCESS_TOKEN}"
```

### Tests

For Supabase Local + Postgres based tests, see `.env.test` (used by CI/local runs):

```bash
DATABASE_URL=postgresql://... AUTH_BACKEND=supabase uv run pytest -q
```
