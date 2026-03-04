"use client";

export function Skeleton({ width = "100%", height = 16, radius = 8, className = "" }: {
    width?: string | number;
    height?: number;
    radius?: number;
    className?: string;
}) {
    return (
        <div
            className={`skeleton-pulse ${className}`}
            style={{
                width: typeof width === "number" ? `${width}px` : width,
                height: `${height}px`,
                borderRadius: `${radius}px`,
                background: "linear-gradient(90deg, rgba(255,255,255,0.04) 25%, rgba(255,255,255,0.08) 50%, rgba(255,255,255,0.04) 75%)",
                backgroundSize: "200% 100%",
                animation: "shimmer 1.5s ease-in-out infinite",
            }}
        />
    );
}

export function SkeletonCard({ lines = 3 }: { lines?: number }) {
    return (
        <div className="card fade-in" style={{ padding: 16 }}>
            <Skeleton width="40%" height={14} />
            <div style={{ marginTop: 10 }} />
            {Array.from({ length: lines }).map((_, i) => (
                <div key={i} style={{ marginTop: 8 }}>
                    <Skeleton width={`${80 - i * 15}%`} height={12} />
                </div>
            ))}
        </div>
    );
}

export function SkeletonProfile() {
    return (
        <div className="fade-in">
            {/* Hero */}
            <div style={{ height: 180, background: "rgba(255,255,255,0.02)", borderRadius: 0 }} />
            {/* Profile header */}
            <div style={{ padding: "0 16px", marginTop: -28, display: "flex", gap: 12, alignItems: "flex-end" }}>
                <Skeleton width={56} height={56} radius={28} />
                <div style={{ flex: 1 }}>
                    <Skeleton width="50%" height={18} />
                    <div style={{ marginTop: 6 }} />
                    <Skeleton width="35%" height={12} />
                </div>
            </div>
            {/* Stats grid */}
            <div style={{ padding: 16, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                {[1, 2, 3, 4].map((i) => (<SkeletonCard key={i} lines={2} />))}
            </div>
        </div>
    );
}
