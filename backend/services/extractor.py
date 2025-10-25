import trafilatura
import httpx
from typing import Optional, Dict

class ContentExtractor:
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=15.0,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0"}
        )

    async def extract(self, url: str) -> Optional[Dict]:
        """Extract main content from URL"""
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            html = response.text

            # Extract with trafilatura
            text = trafilatura.extract(html, include_comments=False, include_tables=False)
            metadata = trafilatura.extract_metadata(html)

            if not text:
                return None

            return {
                "url": url,
                "text": text,
                "title": metadata.title if metadata else None,
                "author": metadata.author if metadata else None,
                "date": metadata.date if metadata else None,
            }
        except Exception as e:
            print(f"Extract error for {url}: {e}")
            return None

    async def close(self):
        await self.client.aclose()
