import asyncio
import httpx

FACEIT_KEY = "99c9beba-57ee-482f-aa38-a85810d40e31"
HENRIK_KEY = "HDEV-addbd95e-b174-4a9d-95dd-f9d0850d9411"

async def test():
    async with httpx.AsyncClient(timeout=10) as client:
        # Test Faceit
        r = await client.get(
            "https://open.faceit.com/data/v4/players?nickname=s1mple",
            headers={"Authorization": f"Bearer {FACEIT_KEY}"}
        )
        print(f"Faceit: {r.status_code} - {'OK' if r.status_code == 200 else r.text[:120]}")

        # Test Henrik
        r = await client.get(
            "https://api.henrikdev.xyz/valorant/v1/account/TenZ/sentinels",
            headers={"Authorization": HENRIK_KEY}
        )
        print(f"Henrik: {r.status_code} - {'OK' if r.status_code == 200 else r.text[:120]}")

asyncio.run(test())
