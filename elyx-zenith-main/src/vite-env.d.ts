/// <reference types="vite/client" />

interface TelegramWebApp {
  initData?: string;
  ready: () => void;
  expand: () => void;
  setHeaderColor?: (color: string) => void;
  setBackgroundColor?: (color: string) => void;
}

interface Window {
  Telegram?: {
    WebApp?: TelegramWebApp;
  };
}

interface ImportMetaEnv {
  readonly VITE_BACKEND_URL?: string;
  readonly VITE_SERVICE_TOKEN?: string;
  readonly VITE_TELEGRAM_ID?: string;
  readonly VITE_TELEGRAM_USERNAME?: string;
}
