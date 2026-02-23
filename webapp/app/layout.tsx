import "./globals.css";
import Link from "next/link";
import type { ReactNode } from "react";

export const metadata = {
  title: "Elyx Web App",
  description: "Telegram Mini App for gamer matching",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="shell">
          <nav className="nav">
            <Link href="/">Home</Link>
            <Link href="/profile/edit">Profile</Link>
            <Link href="/matches">Matches</Link>
            <Link href="/account">Account</Link>
            <Link href="/premium">Premium</Link>
          </nav>
          {children}
        </div>
      </body>
    </html>
  );
}
