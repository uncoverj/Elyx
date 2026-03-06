# Deploy Guide (Railway + Vercel)

## 1) FastAPI backend on Railway

Use the backend service from the repo root.

### Railway service settings

- `Install Command`:
```bash
pip install -r backend/requirements.txt
```

- `Start Command`:
```bash
cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Required/important Railway env vars

- `APP_ENV=dev` (recommended unless you already have managed Postgres configured)
- `SERVICE_TOKEN=<your_secret_token>`
- `CORS_ORIGIN=*` (or your explicit frontend origins)

Optional:

- `DATABASE_URL=<postgres url>` (if omitted in `dev`, backend falls back to SQLite)
- `REDIS_URL=<redis url>`
- `HENRIK_API_KEY=<key>`
- `FACEIT_API_KEY=<key>`
- `STEAM_API_KEY=<key>`

### Verify backend

After deploy, open:

- `https://elyx-production.up.railway.app/health` -> `{"status":"ok"}`
- `https://elyx-production.up.railway.app/docs` -> Swagger UI


## 2) Next.js frontend on Vercel

Set these env vars in Vercel Project -> Settings -> Environment Variables:

- `NEXT_PUBLIC_BACKEND_URL=https://elyx-production.up.railway.app`
- `BACKEND_URL=https://elyx-production.up.railway.app`

Notes:

- Do not add trailing slash.
- Remove old `NEXT_PUBLIC_API_URL` if it points to `loca.lt` or any outdated URL.
- Redeploy after changing env vars.

### Vercel build settings (important)

- `Root Directory`: `webapp`
- `Framework Preset`: `Next.js`
- `Build Command`: `npm run build`
- `Install Command`: `npm install`
- `Output Directory`: `.next`
- `Node.js Version`: `20.x` (LTS)

### Production overrides fix

If you see:
`Configuration Settings in the current Production deployment differ from your current Project Settings`

do this in Vercel:

1. Open the current Production deployment.
2. Open `...` menu -> `Reset Production Overrides` (or remove all overrides manually).
3. Redeploy Production with `Use existing Build Cache` disabled.

### Verify frontend proxy

Open:

- `https://<your-vercel-domain>/api/health`

It should return:

```json
{"status":"ok"}
```


## 3) Dependency split policy

- Backend dependencies live in `backend/requirements.txt`.
- Bot dependencies live in `bot/requirements.txt`.
- Railway backend must install only `backend/requirements.txt`.

## 4) Telegram bot on Railway (separate service)

Deploy bot as a separate Railway service (Worker/Background service), not inside the backend service.

- `Install Command`:
```bash
pip install -r bot/requirements.txt
```

- `Start Command`:
```bash
cd bot && python -m app.main
```

Required bot env vars:

- `BOT_TOKEN=<telegram_bot_token>`
- `BACKEND_URL=https://elyx-production.up.railway.app`
- `SERVICE_TOKEN=<same as backend SERVICE_TOKEN>`
- `WEBAPP_URL=https://<your-vercel-domain>.vercel.app`

Optional bot env vars:

- `STRICT_BACKEND_CHECK=false`
- `DROP_PENDING_UPDATES=true`

Notes:

- Bot uses long polling, so no public HTTP route is required for the bot worker.
- Bot now clears stale webhook on startup, which prevents polling/webhook conflicts.
