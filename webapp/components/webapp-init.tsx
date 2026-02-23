"use client";

import { useEffect } from "react";

export default function WebAppInit() {
  useEffect(() => {
    const app = window.Telegram?.WebApp;
    if (!app) {
      return;
    }

    app.ready();
    app.expand();
  }, []);

  return null;
}
