"use client";

import { useEffect } from "react";

export default function WebAppInit() {
  useEffect(() => {
    const app = (window as any).Telegram?.WebApp;
    if (!app) return;
    app.ready();
    app.expand();
    // Set header color to match our dark theme
    try {
      app.setHeaderColor("#0a0d1a");
      app.setBackgroundColor("#0f1225");
    } catch { }
  }, []);

  return null;
}
