export async function backendFetch(path: string, options: RequestInit = {}) {
  const initData =
    typeof window !== "undefined"
      ? (window as any)?.Telegram?.WebApp?.initData || ""
      : "";

  const base = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
  const response = await fetch(`${base}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "tg-init-data": initData,
      ...(options.headers || {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }

  return response.json();
}
