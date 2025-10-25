import httpx
from typing import List, Dict
from core.config import settings

class SearXNGClient:
    def __init__(self):
        self.base_url = settings.searxng_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def search(self, query: str, categories: str = "general", engines: str = None, num_results: int = 20) -> List[Dict]:
        """Search via SearXNG JSON API"""
        params = {
            "q": query,
            "format": "json",
            "categories": categories,
        }
        if engines:
            params["engines"] = engines

        try:
            response = await self.client.get(f"{self.base_url}/search", params=params)
            response.raise_for_status()
            data = response.json()

            results = data.get("results", [])[:num_results]
            return [
                {
                    "url": r.get("url"),
                    "title": r.get("title"),
                    "content": r.get("content", ""),
                    "engine": r.get("engine"),
                }
                for r in results if r.get("url")
            ]
        except Exception as e:
            print(f"SearXNG error: {e}")
            return []

    async def close(self):
        await self.client.aclose()
