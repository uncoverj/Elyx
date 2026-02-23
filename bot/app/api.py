from typing import Any

import httpx

from app.config import get_settings

settings = get_settings()


class BackendClient:
    def __init__(self) -> None:
        self.base_url = settings.backend_url.rstrip("/")
        self.service_token = settings.service_token

    def _headers(self, tg_id: int) -> dict[str, str]:
        return {
            "x-service-token": self.service_token,
            "x-telegram-id": str(tg_id),
        }

    async def get(self, path: str, tg_id: int) -> Any:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(f"{self.base_url}{path}", headers=self._headers(tg_id))
            response.raise_for_status()
            return response.json()

    async def post(self, path: str, tg_id: int, payload: dict[str, Any] | None = None) -> Any:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                f"{self.base_url}{path}",
                headers=self._headers(tg_id),
                json=payload or {},
            )
            response.raise_for_status()
            return response.json()

    async def put(self, path: str, tg_id: int, payload: dict[str, Any]) -> Any:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.put(
                f"{self.base_url}{path}",
                headers=self._headers(tg_id),
                json=payload,
            )
            response.raise_for_status()
            return response.json()


backend = BackendClient()
