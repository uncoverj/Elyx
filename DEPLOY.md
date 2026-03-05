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
- Redeploy after changing env vars.

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
