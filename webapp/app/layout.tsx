import "./globals.css";
import Script from "next/script";
import type { ReactNode } from "react";

import BottomNav from "@/components/bottom-nav";
import { Providers } from "@/components/providers";

export const metadata = {
  title: "Elyx — Gaming Stats Tracker",
  description: "Track your gaming stats, find teammates, compete on leaderboards",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="theme-color" content="#0a0d1a" />
        <Script
          src="https://telegram.org/js/telegram-web-app.js"
          strategy="beforeInteractive"
        />
      </head>
      <body>
        <Providers>
          <div className="app-shell">
            <div className="app-content">
              {children}
            </div>
            <BottomNav />
          </div>
        </Providers>
      </body>
    </html>
  );
}
