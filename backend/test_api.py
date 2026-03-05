import asyncio
import httpx
import os

async def main():
    faceit_key = os.getenv("FACEIT_API_KEY", "")
    riot_key = os.getenv("RIOT_API_KEY", "")

    # Faceit Test
    if faceit_key:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                "https://open.faceit.com/data/v4/players",
                params={"nickname": "Uncoverj"},
                headers={"Authorization": f"Bearer {faceit_key}", "Accept": "application/json"},
            )
            print("Faceit:", r.status_code, r.text)
    else:
        print("Faceit: FACEIT_API_KEY is not set")

    # Riot Test
    if riot_key:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                "https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/Uncoverj/1795",
                headers={"X-Riot-Token": riot_key},
            )
            print("Riot:", r.status_code, r.text)
    else:
        print("Riot: RIOT_API_KEY is not set")

if __name__ == "__main__":
    asyncio.run(main())
