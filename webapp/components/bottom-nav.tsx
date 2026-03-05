"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useProfile } from "@/lib/use-profile";

function SpeedometerIcon() {
    return (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" />
            <path d="M12 6v2" /><path d="M17.2 8.8l-1.4 1.4" />
            <path d="M18 14h-2" /><path d="M6 14h2" />
            <path d="M6.8 8.8l1.4 1.4" /><path d="M12 12l3-3" />
        </svg>
    );
}

function PodiumIcon() {
    return (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="2" y="14" width="6" height="8" rx="1" />
            <rect x="9" y="8" width="6" height="14" rx="1" />
            <rect x="16" y="11" width="6" height="11" rx="1" />
        </svg>
    );
}

function ProfileIcon() {
    return (
        <svg width="28" height="28" viewBox="0 0 24 24" fill="white">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
        </svg>
    );
}

function ClockIcon() {
    return (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" />
            <polyline points="12,6 12,12 16,14" />
        </svg>
    );
}

function GearIcon() {
    return (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="3" />
            <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06A1.65 1.65 0 0019.32 9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z" />
        </svg>
    );
}

const tabs = [
    { href: "/", icon: SpeedometerIcon, label: "Power" },
    { href: "/roles", icon: PodiumIcon, label: "Stats" },
    { href: "/profile", icon: ProfileIcon, label: "", center: true },
    { href: "/matches", icon: ClockIcon, label: "Matches" },
    { href: "/settings", icon: GearIcon, label: "Settings" },
];

export default function BottomNav() {
    const pathname = usePathname();

    return (
        <nav className="tab-bar">
            {tabs.map((tab, i) => {
                const isActive = tab.center ? false
                    : pathname === tab.href || (tab.href !== "/" && pathname.startsWith(tab.href));
                const Icon = tab.icon;

                if (tab.center) {
                    return (
                        <Link key={i} href={tab.href} className="tab-center">
                            <Icon />
                        </Link>
                    );
                }

                return (
                    <Link key={i} href={tab.href} className={`tab-item ${isActive ? "active" : ""}`}>
                        <Icon />
                        {tab.label && <span>{tab.label}</span>}
                    </Link>
                );
            })}
        </nav>
    );
}
