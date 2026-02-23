# Infra Notes

- Local orchestration is handled by the root `docker-compose.yml`.
- Production recommendation:
  1. Backend (FastAPI) on Render/Fly/Railway.
  2. Bot worker as separate always-on service.
  3. WebApp (Next.js) on Vercel/Render.
  4. Managed Postgres + Redis.

Bot and backend must be online 24/7 for notifications and matching consistency.
