import os
from dotenv import load_dotenv
from firecrawl import FirecrawlApp
import requests
from typing import Dict, Any, Optional

# Load environment variables (like our API key) from the .env file
load_dotenv()

class FirecrawlClient:
    """
    A simple client to interact with the Firecrawl API.
    Firecrawl is great because it handles complex websites and returns 
    data in a format that's easy for us to process (like Markdown and clean JSON).
    """
    def __init__(self):
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            raise ValueError("FIRECRAWL_API_KEY not found in environment variables")
        self.app = FirecrawlApp(api_key=api_key)

    def scrape_url(self, url: str) -> Dict[str, Any]:
        """
        Scrapes a single URL and returns HTML, metadata, and clean content.
        """
        try:
            print(f"DEBUG: Attempting to scrape {url} using app.v1.scrape_url")
            # The newest firecrawl-py uses app.v1.scrape_url with keyword arguments
            result = self.app.v1.scrape_url(
                url, 
                formats=['html', 'markdown'], 
                only_main_content=False,
                wait_for=1000 # Wait only 1 second for JS to settle
            )
            # The result is now a V1ScrapeResponse object, we need to convert it to a dict
            # or access its attributes. Most SDKs have a .model_dump() or similar if they use Pydantic.
            print(f"DEBUG: Scrape result: {type(result)}")
            
            # Firecrawl v1 result objects usually have 'data' attribute or are dict-like
            if hasattr(result, 'model_dump'):
                return result.model_dump()
            return dict(result)

        except Exception as e:
            print(f"DEBUG: Firecrawl Exception for {url}: {e}")
            return {}

    def check_file_exists(self, base_url: str, filename: str) -> bool:
        """
        Checks if a specific file (like robots.txt) exists on the server.
        We do this by trying to fetch the URL and seeing if the server says 'OK'.
        """
        # Ensure base_url doesn't have a trailing slash before adding filename
        base_url = base_url.rstrip('/')
        target_url = f"{base_url}/{filename}"
        try:
            # We use a simple 'head' request to save time (we just want to see if it's there)
            response = requests.head(target_url, timeout=5, allow_redirects=True)
            return response.status_code == 200
        except:
            return False
