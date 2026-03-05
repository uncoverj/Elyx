"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

function PowerIcon() {
    return (
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" />
            <path d="M12 6v2" /><path d="M17.2 8.8l-1.4 1.4" />
            <path d="M18 14h-2" /><path d="M6 14h2" />
            <path d="M6.8 8.8l1.4 1.4" /><path d="M12 12l3-3" />
        </svg>
    );
}

function StatsIcon() {
    return (
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="20" x2="18" y2="10" />
            <line x1="12" y1="20" x2="12" y2="4" />
            <line x1="6" y1="20" x2="6" y2="14" />
        </svg>
    );
}

function TrophyIcon() {
    return (
        <svg width="26" height="26" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C9.24 2 7 4.24 7 7v1H4c-1.1 0-2 .9-2 2v2c0 2.21 1.79 4 4 4h.26A7.013 7.013 0 0011 19.83V22H8v2h8v-2h-3v-2.17A7.013 7.013 0 0017.74 16H18c2.21 0 4-1.79 4-4v-2c0-1.1-.9-2-2-2h-3V7c0-2.76-2.24-5-5-5zM4 10h3v4.71A2.996 2.996 0 014 12v-2zm16 2c0 1.3-.84 2.4-2 2.83V10h3l-1 2z" />
        </svg>
    );
}

function HeartIcon() {
    return (
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z" />
        </svg>
    );
}

function SettingsIcon() {
    return (
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="3" />
            <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06A1.65 1.65 0 0019.32 9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z" />
        </svg>
    );
}

const SIDE_TABS = [
    { href: "/", icon: PowerIcon, label: "Power" },
    { href: "/roles", icon: StatsIcon, label: "Stats" },
    { href: "/matches", icon: HeartIcon, label: "Matches" },
    { href: "/settings", icon: SettingsIcon, label: "Settings" },
];

export default function BottomNav() {
    const pathname = usePathname();

    const isActive = (href: string) =>
        href === "/"
            ? pathname === "/"
            : pathname.startsWith(href);

    return (
        <nav className="tab-bar">
            {/* Left two tabs */}
            {SIDE_TABS.slice(0, 2).map((tab) => {
                const active = isActive(tab.href);
                return (
                    <Link key={tab.href} href={tab.href}
                        className={`tab-item${active ? " active" : ""}`}>
                        <tab.icon />
                        <span>{tab.label}</span>
                    </Link>
                );
            })}

            {/* Center button — raised */}
            <Link href="/leaderboard" className="tab-center">
                <div className="tab-center-btn">
                    <TrophyIcon />
                </div>
                <span className="tab-center-label">Leader</span>
            </Link>

            {/* Right two tabs */}
            {SIDE_TABS.slice(2).map((tab) => {
                const active = isActive(tab.href);
                return (
                    <Link key={tab.href} href={tab.href}
                        className={`tab-item${active ? " active" : ""}`}>
                        <tab.icon />
                        <span>{tab.label}</span>
                    </Link>
                );
            })}
        </nav>
    );
}
