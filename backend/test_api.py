import asyncio
import httpx

async def main():
    faceit_key = "cb241d7b-bdda-46d1-ad82-28b6b0502c56"
    riot_key = "RGAPI-c7ba0fb3-992a-4107-9c59-52fc764d691a"

    # Faceit Test
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "https://open.faceit.com/data/v4/players",
            params={"nickname": "Uncoverj", "game": "cs2"},
            headers={"Authorization": f"Bearer {faceit_key}", "Accept": "application/json"}
        )
        print("Faceit:", r.status_code, r.text)

    # Riot Test
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/Uncoverj/1795",
            headers={"X-Riot-Token": riot_key}
        )
        print("Riot:", r.status_code, r.text)

if __name__ == "__main__":
    asyncio.run(main())
