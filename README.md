# Elyx Monorepo

Production-oriented MVP for gamer matchmaking:
- Telegram Bot (aiogram v3, FSM)
- FastAPI backend (Postgres, Redis, SQLAlchemy async, Alembic)
- Telegram Web App (Next.js 14, TypeScript, Tailwind)

## Structure

- `backend/` — FastAPI API, matching logic, anti-abuse, migrations, tests
- `bot/` — Telegram bot UX and FSM flows
- `webapp/` — Telegram Mini App pages
- `infra/` — deployment notes

## Implemented core features

### Bot
- `/start` with registration bootstrap
- Registration FSM: nickname, gender, age, game, roles, tags, bio, media, confirm
- Main menu: Search / My Profile / Matches / Settings
- Search actions: Like / Skip / Send letter / Stop
- Mutual likes create match
- Profile editing: refill, change media, change bio
- Settings: Riot ID, Steam, refresh stats (stub)

### Backend API
- `GET /health`
- `GET /games`
- `GET/PUT /profiles/me`
- `GET /profiles/{id}`
- `GET /search/next`
- `POST /actions/like|skip|letter`
- `GET /matches`, `GET /matches/{id}`
- `POST /trust/upvote`, `POST /trust/downvote` (only after match)
- `POST /account/link/riot`, `POST /account/link/steam`
- `POST /account/refresh-stats` (stub)
- Telegram auth: `tg-init-data` HMAC validation for WebApp
- Bot->backend auth: `x-service-token` + `x-telegram-id`
- Rate limits via Redis:
  - letters: 5/day for free users
  - likes: 100/day for free users

### Matching
- Filters by same game
- Excludes already liked/skipped/matched users
- Score:
  - `0.45 * rank_similarity`
  - `0.35 * trust_score`
  - `0.15 * tag_overlap`
  - `0.05 * recency`

### Web App
Pages:
- `/` home/profile view
- `/profile/edit`
- `/account`
- `/matches`
- `/premium`
- `/admin` (moderation placeholder)

## Environment setup

1. Copy `.env.example` to `.env` in repo root.
2. Fill at minimum:
   - `BOT_TOKEN`
   - `SERVICE_TOKEN`

Also available examples:
- `backend/.env.example`
- `bot/.env.example`
- `webapp/.env.example`

## Local run (Docker)

```bash
docker compose up --build
```

Services:
- Backend: http://localhost:8000/health
- WebApp: http://localhost:3000
- Bot: run via polling in container

## Windows (No Docker) Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+

Allow local PowerShell scripts (one-time):

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Setup

1. Copy root env file:

```powershell
Copy-Item .env.example .env
```

2. Edit `.env` and set at minimum:
   - `BOT_TOKEN`
   - (optional) `DATABASE_URL` for real Postgres

`APP_ENV` defaults to `dev` and backend auto-falls back to SQLite (`elyx.db`) when Postgres is missing/unreachable.

### Run services

Run each service in separate terminals:

```powershell
./run_backend.ps1
./run_bot.ps1
./run_webapp.ps1
```

Or launch all three windows at once:

```powershell
./run_all.ps1
```

### Verify

- Backend health: http://127.0.0.1:8000/health
- WebApp: http://localhost:3000
- Bot: open Telegram and send `/start`

Note: Telegram in-app WebApp requires HTTPS in production, but local browser development over `http://localhost:3000` is supported.

## Telegram BotFather setup

1. `/setmenubutton` -> Web App URL (`http://localhost:3000` for local tests with tunnel)
2. `/setdomain` with your deployed web domain

For real Telegram Mini App testing, expose webapp/backend publicly (e.g., via ngrok/cloudflared).

## Tests

```bash
# from backend/
pytest -q
```

Includes unit tests for matching helpers.

## Deploy notes

Recommended split:
1. Backend service (FastAPI)
2. Bot worker (separate always-on process)
3. WebApp (Vercel/Render)
4. Managed Postgres + Redis

Bot and backend must stay online continuously for reliable notifications and matching.

## Notes / stubs

- Riot and Steam integrations are linked as account references; official stats sync is left as pluggable stub.
- Anti-fraud extensions (duplicate media detection, advanced anomaly checks) are scaffolded as next-step work.
