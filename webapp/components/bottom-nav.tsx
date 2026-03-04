"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

function SpeedometerIcon() {
    return (
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" />
            <path d="M12 6v2" /><path d="M17.2 8.8l-1.4 1.4" />
            <path d="M18 14h-2" /><path d="M6 14h2" />
            <path d="M6.8 8.8l1.4 1.4" /><path d="M12 12l3-3" />
        </svg>
    );
}

function PodiumIcon() {
    return (
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="2" y="14" width="6" height="8" rx="1" />
            <rect x="9" y="8" width="6" height="14" rx="1" />
            <rect x="16" y="11" width="6" height="11" rx="1" />
        </svg>
    );
}

function TrophyIcon() {
    return (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C9.24 2 7 4.24 7 7v1H4c-1.1 0-2 .9-2 2v2c0 2.21 1.79 4 4 4h.26A7.013 7.013 0 0011 19.83V22H8v2h8v-2h-3v-2.17A7.013 7.013 0 0017.74 16H18c2.21 0 4-1.79 4-4v-2c0-1.1-.9-2-2-2h-3V7c0-2.76-2.24-5-5-5zM4 10h3v4.71A2.996 2.996 0 014 12v-2zm16 2c0 1.3-.84 2.4-2 2.83V10h3l-1 2z" />
        </svg>
    );
}

function ClockIcon() {
    return (
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" />
            <polyline points="12,6 12,12 16,14" />
        </svg>
    );
}

function GearIcon() {
    return (
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="3" />
            <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06A1.65 1.65 0 0019.32 9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z" />
        </svg>
    );
}

const tabs = [
    { href: "/", icon: SpeedometerIcon, label: "Power" },
    { href: "/roles", icon: PodiumIcon, label: "Stats" },
    { href: "/leaderboard", icon: TrophyIcon, label: "", center: true },
    { href: "/history", icon: ClockIcon, label: "Matches" },
    { href: "/account", icon: GearIcon, label: "Settings" },
];

export default function BottomNav() {
    const pathname = usePathname();

    return (
        <nav className="bottom-nav">
            {tabs.map((tab, i) => {
                const isActive = tab.center ? false
                    : pathname === tab.href || (tab.href !== "/" && pathname.startsWith(tab.href));
                const Icon = tab.icon;

                if (tab.center) {
                    return (
                        <Link key={i} href={tab.href} className="nav-item center-item">
                            <span className="nav-icon" style={{ animation: "glowBorder 3s ease-in-out infinite" }}>
                                <Icon />
                            </span>
                        </Link>
                    );
                }

                return (
                    <Link key={i} href={tab.href} className={`nav-item${isActive ? " active" : ""}`}
                        style={{ transition: "color 0.25s ease, transform 0.2s ease" }}>
                        <span className="nav-icon" style={{
                            transition: "transform 0.2s ease, filter 0.3s ease",
                            transform: isActive ? "scale(1.15)" : "scale(1)",
                            filter: isActive ? "drop-shadow(0 0 6px rgba(167, 139, 250, 0.6))" : "none",
                        }}>
                            <Icon />
                        </span>
                        {tab.label && (
                            <span style={{ fontSize: 10, fontWeight: isActive ? 600 : 400, transition: "all 0.2s ease" }}>
                                {tab.label}
                            </span>
                        )}
                    </Link>
                );
            })}
        </nav>
    );
}
