from typing import Any

import httpx

from app.config import get_settings

settings = get_settings()


class BackendClient:
    def __init__(self) -> None:
        self.base_url = settings.backend_url.rstrip("/")
        self.service_token = settings.service_token

    def _headers(self, tg_id: int, username: str | None = None) -> dict[str, str]:
        h = {
            "x-service-token": self.service_token,
            "x-telegram-id": str(tg_id),
        }
        if username:
            h["x-telegram-username"] = username
        return h

    async def get(
        self,
        path: str,
        tg_id: int,
        username: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(
                f"{self.base_url}{path}",
                headers=self._headers(tg_id, username),
                params=params,
            )
            response.raise_for_status()
            return response.json()

    async def post(self, path: str, tg_id: int, payload: dict[str, Any] | None = None, username: str | None = None) -> Any:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                f"{self.base_url}{path}",
                headers=self._headers(tg_id, username),
                json=payload or {},
            )
            response.raise_for_status()
            return response.json()

    async def put(self, path: str, tg_id: int, payload: dict[str, Any], username: str | None = None) -> Any:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.put(
                f"{self.base_url}{path}",
                headers=self._headers(tg_id, username),
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    async def delete(self, path: str, tg_id: int, username: str | None = None) -> Any:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.delete(
                f"{self.base_url}{path}",
                headers=self._headers(tg_id, username),
            )
            response.raise_for_status()
            return response.json()


backend = BackendClient()
