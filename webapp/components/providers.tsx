"use client";

import { ProfileProvider } from "@/lib/use-profile";
import type { ReactNode } from "react";

export function Providers({ children }: { children: ReactNode }) {
    return <ProfileProvider>{children}</ProfileProvider>;
}
