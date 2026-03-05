"use client";

import { ProfileProvider } from "@/lib/use-profile";
import WebAppInit from "@/components/webapp-init";
import type { ReactNode } from "react";

export function Providers({ children }: { children: ReactNode }) {
    return (
        <>
            <WebAppInit />
            <ProfileProvider>{children}</ProfileProvider>
        </>
    );
}
