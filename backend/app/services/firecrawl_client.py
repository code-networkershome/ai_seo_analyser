import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from firecrawl import FirecrawlApp
import requests
from typing import Dict, Any, Optional

# Load environment variables (like our API key) from the .env file
load_dotenv()

class FirecrawlClient:
    """
    A client to interact with the Firecrawl API.
    Now supports ASYNC execution for higher performance.
    """
    def __init__(self):
        self.api_key = os.getenv("FIRECRAWL_API_KEY")
        self.executor = ThreadPoolExecutor(max_workers=3)

    async def scrape_url(self, url: str) -> Dict[str, Any]:
        """
        Asynchronously scrapes a URL using Firecrawl v1 API directly via HTTP.
        """
        if not self.api_key:
            return {"error": "API Key missing"}
            
        print(f"DEBUG: Scrapping {url} via direct API call")
        try:
            loop = asyncio.get_event_loop()
            
            def _do_scrape():
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "url": url,
                    "formats": ["markdown", "html"]
                }
                response = requests.post(
                    "https://api.firecrawl.dev/v1/scrape",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                if response.status_code != 200:
                    return {"error": f"API Error {response.status_code}: {response.text}"}
                
                # Firecrawl v1 returns data inside a 'data' key
                json_res = response.json()
                return json_res.get('data', json_res)
                
            result = await loop.run_in_executor(self.executor, _do_scrape)
            return result
        except Exception as e:
            print(f"DEBUG: Firecrawl Direct Error: {str(e)}")
            return {"error": str(e)}

    def _scrape_sync(self, url: str) -> Dict[str, Any]:
        # Deprecated
        return {}

    async def check_file_exists(self, base_url: str, filename: str) -> bool:
        """
        Checks if a file exists (Async) using httpx would be best, 
        but for now we'll wrap requests to keep dependencies simple or use httpx if available.
        Let's use requests in threadpool for consistency with the rest of this class
        until we fully migrate to httpx everywhere.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._check_file_sync, base_url, filename)

    def _check_file_sync(self, base_url: str, filename: str) -> bool:
        base_url = base_url.rstrip('/')
        target_url = f"{base_url}/{filename}"
        try:
            response = requests.head(target_url, timeout=5, allow_redirects=True)
            return response.status_code == 200
        except:
            return False
