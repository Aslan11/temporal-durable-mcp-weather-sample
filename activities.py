# activities.py

from temporalio import activity
import httpx

NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

@activity.defn
async def make_nws_request(url: str) -> dict | None:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            activity.logger.error(f"Failed to fetch {url}: {e}")
            return None
