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
- `/start` with registration bootstrap and welcome message
- Registration FSM: nickname, gender, age, game, roles, tags, bio, media, Riot/Steam account link, confirm
- Main menu: Поиск / Мой профиль / Мэтчи / Лидерборд / Настройки
- Search actions: Лайк / Скип / Отправить письмо / Остановить поиск
- **Like notifications**: recipient gets "У вас новый лайк!" with "Посмотреть" button → shows sender's card → Лайк/Скип reaction
- **Letter notifications**: recipient gets the letter text with Лайк/Скип reaction buttons
- Mutual likes create match with notification to both users
- Matches pagination with inline ⬅️/➡️ navigation and @username button
- **Leaderboard**: per-game top players with pagination (⬅️/➡️), "Моя позиция" button, medals (🥇🥈🥉)
- Profile card format: trust score, nickname/age/gender, game, roles, stats (K/D, Rank, Win%, Unified Score), bio
- Premium badge (⭐) on premium profiles
- Profile editing: refill, change media, change bio
- Settings: Riot ID, Steam, refresh stats (with cooldown), Premium info, Support

### Backend API
- `GET /health`
- `GET /games` — Valorant, CS2, Dota 2, LoL, Apex Legends, Overwatch 2, Fortnite, Other
- `GET/PUT /profiles/me` — includes `is_premium`, stats with `unified_score`
- `GET /profiles/{id}`
- `GET /search/next`
- `POST /actions/like|skip|letter`
- `GET /matches`, `GET /matches/{id}`
- `POST /trust/upvote`, `POST /trust/downvote` — match-gated, cooldown, suspicion detection
- `POST /account/link/riot`, `POST /account/link/steam`
- `POST /account/refresh-stats` — **real API integration** with cooldown (free: 12h, premium: 15min):
  - **Valorant**: Henrik API (rank, RR, K/D, win rate)
  - **Dota 2**: OpenDota API (medal, MMR, K/D, win rate)
  - **CS2**: Steam Web API (K/D, win rate, hours played)
- `GET /leaderboard/{game_id}` — paginated leaderboard by unified_score
- `GET /leaderboard/{game_id}/me` — user's position + total
- `POST /leaderboard/rebuild` — admin trigger to rebuild all leaderboards
- `GET /premium/status` — current plan, days left, feature limits
- `POST /premium/activate` — activate 30-day premium
- Telegram auth: `tg-init-data` HMAC validation for WebApp
- Bot→backend auth: `x-service-token` + `x-telegram-id` + `x-telegram-username`
- **Background refresh loop**: every 30 min, auto-updates eligible users' stats + rebuilds leaderboards
- Rate limits via Redis (graceful fallback when Redis unavailable in dev):
  - letters: 5/day for free users (unlimited for premium)
  - likes: 100/day for free users (unlimited for premium)

### Unified Rank Scoring (0–10,000)
Each game’s ranks are mapped to a universal 0–10,000 scale for fair cross-comparison:
- **Valorant**: Iron 1 (500) → Radiant (8840) + RR bonus
- **CS2**: Silver I (500) → Global Elite (9000)
- **Dota 2**: Herald (700) → Immortal (7800), or raw MMR ×0.75+500
- **LoL**: Iron IV (500) → Challenger (8600) + LP bonus
- **Apex**: Rookie (500) → Apex Predator (8800)
- **Overwatch 2**: Bronze (500) → Champion (8500)

### Leaderboard
- Per-game leaderboard sorted by `unified_score`
- Cached in `leaderboard_entries` table for fast reads
- Rebuilt automatically after stats refresh
- Paginated (offset/limit), with user position lookup

### Matching
- Hard filter by same game
- Excludes already liked/skipped/matched users
- Score (unified_score-based):
  - `0.50 * rank_similarity` (unified_score gap, max 4000)
  - `0.25 * weighted_trust` (account-age-weighted votes)
  - `0.10 * tag_overlap`
  - `0.10 * activity_recency` (1h→1.0, 6h→0.9, 24h→0.7, 72h→0.4)
  - `0.05 * premium_boost`

### Trust System (enhanced)
- Vote only after match (enforced at API)
- 24h cooldown between vote changes
- **Weighted votes** by account age: <7d → 0.2, 7-30d → 0.6, 30d+ → 1.0
- Premium does NOT give stronger vote weight (anti-pay2win)
- Suspicion detection: 5+ downvotes in 24h → flagged

### Premium System
- 30-day subscription periods (stackable)
- Unlimited likes and letters
- Priority in search results
- ⭐ badge on profile card
- See who liked you (planned)

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
   - (optional) `STEAM_API_KEY` for CS2 stats — get one at https://steamcommunity.com/dev/apikey
   - (optional) `HENRIK_API_KEY` for Valorant stats — free tier works without key

`APP_ENV` defaults to `dev` and backend auto-falls back to SQLite (`elyx.db`) when Postgres is missing/unreachable.
Redis is also optional in dev — rate limiting is silently skipped when Redis is unavailable.

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
The bot should run as a Railway Worker with `cd bot && python -m app.main` and `BACKEND_URL` pointing to the backend public URL.

Detailed Railway + Vercel setup is documented in [DEPLOY.md](DEPLOY.md).

## Architecture (3-layer)

1. **Bot API** (aiogram v3) — registration, menus, search UX, notifications, leaderboard display
2. **Backend** (FastAPI) — DB, matching, trust, rate limits, leaderboard cache, premium
3. **Stats/Analytics** (services layer) — Riot/Steam/OpenDota API integrations, rank normalization, background refresh

The bot never calls game APIs directly — all stats go through the backend’s analytics service.

## Notes / roadmap

- **Valorant stats** use Henrik's unofficial API (free tier, no key needed, 30 req/min).
- **Dota 2 stats** use OpenDota API (free, no key needed, 60 req/min).
- **CS2 stats** use Steam Web API (requires `STEAM_API_KEY` for full data).
- **League of Legends** stats integration is planned but not yet implemented.
- **Background refresh**: runs every 30 min, respects free (18h) and premium (2h) intervals, 2s delay between users for API rate limits.
- Payment integration for Premium (Telegram Stars / Stripe) is next-step work.
- Anti-fraud extensions (duplicate media detection, advanced anomaly checks) are scaffolded as next-step work.
