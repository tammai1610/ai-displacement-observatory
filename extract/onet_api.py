"""
Fetch O*NET work activity and ability ratings for all occupations.

How it works:
  1. GET /occupations/ -> list of all occupation codes
  2. For each occupation, GET /work_activities and /abilities
  3. Uses async httpx with semaphore (3 concurrent requests, polite)
  4. Saves two Parquet files to data/raw/onet/

Run: uv run python extract/onet_api.py
     uv run python extract/onet_api.py --sample   (first 50 occupations only)
"""
import os
import asyncio
import httpx
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

BASE_URL_V2 = "https://api-v2.onetcenter.org/online"
BASE_URL_V19 = "https://services.onetcenter.org/ws"
RAW_DIR = Path(os.getenv("RAW_DATA_DIR", "./data/raw")) / "onet"
RAW_DIR.mkdir(parents=True, exist_ok=True)


def get_api_config() -> tuple[str, dict]:
    api_key = os.getenv("ONET_API_KEY")
    username = os.getenv("ONET_USERNAME")
    password = os.getenv("ONET_PASSWORD")

    if api_key:
        return (
            BASE_URL_V2,
            {
                "headers": {
                    "Accept": "application/json",
                    "X-API-Key": api_key,
                }
            },
        )

    if username and password:
        return (
            BASE_URL_V19,
            {
                "auth": (username, password),
                "headers": {"Accept": "application/json"},
            },
        )

    raise ValueError(
        "Set either ONET_API_KEY or both ONET_USERNAME and ONET_PASSWORD in .env."
    )


async def fetch_all_occupations(client: httpx.AsyncClient, base_url: str) -> list[dict]:
    """Get list of all O*NET occupation codes and titles."""
    r = await client.get(f"{base_url}/occupations/", params={"end": 1000})
    r.raise_for_status()
    return r.json()["occupation"]


async def fetch_work_activities(
    client: httpx.AsyncClient, base_url: str, onet_code: str
) -> list[dict]:
    """Fetch work activity importance ratings for one occupation."""
    path = (
        f"{base_url}/occupations/{onet_code}/details/work_activities"
        if "api-v2" in base_url
        else f"{base_url}/occupations/{onet_code}/work_activities"
    )
    r = await client.get(path, params={"end": 100} if "api-v2" in base_url else None)
    if r.status_code == 404:
        return []
    r.raise_for_status()
    return [
        {
            "onet_code": onet_code,
            "activity_id": item["id"],
            "activity_name": item["name"],
            "importance": item.get("score", {}).get("value"),
        }
        for item in r.json().get("element", [])
    ]


async def fetch_abilities(
    client: httpx.AsyncClient, base_url: str, onet_code: str
) -> list[dict]:
    """Fetch ability ratings for one occupation."""
    path = (
        f"{base_url}/occupations/{onet_code}/details/abilities"
        if "api-v2" in base_url
        else f"{base_url}/occupations/{onet_code}/abilities"
    )
    r = await client.get(path, params={"end": 100} if "api-v2" in base_url else None)
    if r.status_code == 404:
        return []
    r.raise_for_status()
    return [
        {
            "onet_code": onet_code,
            "ability_id": item["id"],
            "ability_name": item["name"],
            "importance": item.get("score", {}).get("value"),
        }
        for item in r.json().get("element", [])
    ]


async def run(sample: bool = False) -> None:
    limits = httpx.Limits(max_connections=3)
    base_url, client_options = get_api_config()
    async with httpx.AsyncClient(
        **client_options,
        limits=limits,
        timeout=30,
    ) as client:
        print("Fetching occupation list from O*NET...")
        occs = await fetch_all_occupations(client, base_url)
        if sample:
            occs = occs[:50]
            print(f"  Sample mode: using first 50 occupations")

        pd.DataFrame(occs).to_parquet(RAW_DIR / "occupations.parquet", index=False)
        print(f"  Saved {len(occs)} occupations")

        sem = asyncio.Semaphore(3)
        all_acts, all_abs = [], []

        async def fetch_one(occ: dict) -> tuple:
            async with sem:
                acts = await fetch_work_activities(client, base_url, occ["code"])
                abs_ = await fetch_abilities(client, base_url, occ["code"])
                await asyncio.sleep(0.3)
                return acts, abs_

        print(f"Fetching work activities + abilities for {len(occs)} occupations...")
        tasks = [fetch_one(o) for o in occs]
        for fut in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="O*NET"):
            acts, abs_ = await fut
            all_acts.extend(acts)
            all_abs.extend(abs_)

        pd.DataFrame(all_acts).to_parquet(RAW_DIR / "work_activities.parquet", index=False)
        pd.DataFrame(all_abs).to_parquet(RAW_DIR / "abilities.parquet", index=False)

        print(f"\nO*NET extract complete:")
        print(f"  work_activities.parquet  {len(all_acts):>8,} rows")
        print(f"  abilities.parquet        {len(all_abs):>8,} rows")
        print(f"  occupations.parquet      {len(occs):>8,} rows")


if __name__ == "__main__":
    import sys
    asyncio.run(run(sample="--sample" in sys.argv))
