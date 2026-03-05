"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useProfile } from "@/lib/use-profile";

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
    { href: "/matches", icon: ClockIcon, label: "Matches" },
    { href: "/settings", icon: GearIcon, label: "Settings" },
];

const GAME_THEMES: Record<string, { gradient: string; accent: string; glow: string }> = {
    "Valorant": { gradient: "linear-gradient(135deg, #fd4556 0%, #1f1225 100%)", accent: "#fd4556", glow: "rgba(253,69,86,0.3)" },
    "CS2": { gradient: "linear-gradient(135deg, #de9b35 0%, #1a1a2e 100%)", accent: "#de9b35", glow: "rgba(222,155,53,0.3)" },
    "League of Legends": { gradient: "linear-gradient(135deg, #c89b3c 0%, #091428 100%)", accent: "#c89b3c", glow: "rgba(200,155,60,0.3)" },
    "Dota 2": { gradient: "linear-gradient(135deg, #e44d2e 0%, #1a1a2e 100%)", accent: "#e44d2e", glow: "rgba(228,77,46,0.3)" },
    "Apex Legends": { gradient: "linear-gradient(135deg, #cd3333 0%, #1a1a2e 100%)", accent: "#cd3333", glow: "rgba(205,51,51,0.3)" },
    "Overwatch 2": { gradient: "linear-gradient(135deg, #fa9c1e 0%, #1a1a2e 100%)", accent: "#fa9c1e", glow: "rgba(250,156,30,0.3)" },
    "Fortnite": { gradient: "linear-gradient(135deg, #9d4dbb 0%, #1a1a2e 100%)", accent: "#9d4dbb", glow: "rgba(157,77,187,0.3)" },
};

const DEFAULT_THEME = { gradient: "linear-gradient(135deg, #a78bfa 0%, #1a0a2e 100%)", accent: "#a78bfa", glow: "rgba(167,139,250,0.3)" };

export default function BottomNav() {
    const pathname = usePathname();
    const { profile } = useProfile();
    const theme = GAME_THEMES[profile?.game_name || ""] || DEFAULT_THEME;

    return (
        <nav className="bottom-nav">
            {tabs.map((tab, i) => {
                const isActive = tab.center ? false
                    : pathname === tab.href || (tab.href !== "/" && pathname.startsWith(tab.href));
                const Icon = tab.icon;

                if (tab.center) {
                    return (
                        <Link key={i} href={tab.href} className="nav-item center-item">
                            <span className="nav-icon" style={{
                                animation: "glowBorder 3s ease-in-out infinite",
                                background: theme.gradient,
                                boxShadow: `0 4px 16px ${theme.glow}`
                            }}>
                                <Icon />
                            </span>
                        </Link>
                    );
                }

                return (
                    <Link key={i} href={tab.href} className={`nav-item${isActive ? " active" : ""}`}
                        style={{
                            color: isActive ? theme.accent : "var(--text-muted)",
                            transition: "color 0.25s ease, transform 0.2s ease"
                        }}>
                        <span className="nav-icon" style={{
                            transition: "transform 0.2s ease, filter 0.3s ease",
                            transform: isActive ? "scale(1.15)" : "scale(1)",
                            filter: isActive ? `drop-shadow(0 0 6px ${theme.glow})` : "none",
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
