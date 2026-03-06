# Elyx Zenith (Vite + React)

Modernized frontend for Elyx tracker with working backend integration:

- Telegram Mini App auth via `tg-init-data`
- Working account linking buttons (`/account/link/{provider}`)
- Working stats refresh (`/account/refresh-stats`)
- Working game switch (`PUT /profiles/me`)
- Real profile/games/accounts loading from backend

## Run locally

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
```

## Environment variables

Create `.env` (or `.env.local`) in project root:

```env
VITE_BACKEND_URL=https://elyx-production.up.railway.app
```

Optional fallback auth for browser testing outside Telegram:

```env
VITE_SERVICE_TOKEN=local-service-token
VITE_TELEGRAM_ID=123456789
VITE_TELEGRAM_USERNAME=my_username
```

## Telegram Mini App

`index.html` already includes:

- `https://telegram.org/js/telegram-web-app.js`

On app init, frontend calls:

- `Telegram.WebApp.ready()`
- `Telegram.WebApp.expand()`

and passes `tg-init-data` to backend automatically.
