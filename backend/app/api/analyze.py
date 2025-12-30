from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
import asyncio
from app.services.firecrawl_client import FirecrawlClient
from app.utils.seo_checks import perform_seo_checks
from app.utils.security_checks import perform_security_checks
from app.utils.aeo_checks import perform_aeo_checks
from app.utils.ai_explainer import AIExplainer
from app.services.supabase_client import get_supabase_client

router = APIRouter()

# This is our input 'Blueprint'. It tells FastAPI what to expect from the user.
class AnalyzeRequest(BaseModel):
    url: HttpUrl

@router.post("/analyze")
async def analyze_website(request: AnalyzeRequest):
    """
    The main engine of our app.
    1. It takes a URL.
    2. It crawls it (Async).
    3. It runs SEO and Security checks.
    4. It asks AI to explain everything (Async).
    5. It saves the report to Supabase (if configured).
    """
    url_str = str(request.url)
    
    try:
        # Initialize our tools
        client = FirecrawlClient()
        explainer = AIExplainer()
        db = get_supabase_client()

        # Step 1: Crawl the website AND check files concurrently
        print(f"Crawling {url_str}...")
        
        # We start the main crawl
        crawl_task = client.scrape_url(url_str)
        
        # We start the file checks in parallel
        files_to_check = ["robots.txt", "humans.txt", "security.txt", "llms.txt"]
        file_check_tasks = [client.check_file_exists(url_str, f) for f in files_to_check]
        
        # Wait for all network IO to finish
        results = await asyncio.gather(crawl_task, *file_check_tasks)
        
        crawl_result = results[0]
        file_results_list = results[1:] # A list of booleans corresponding to files_to_check
        
        print(f"DEBUG: crawl_result type: {type(crawl_result)}")
        
        # Check if scraping was disabled due to missing key
        if isinstance(crawl_result, dict) and crawl_result.get('error') == "API Key missing":
             return {
                 "seo_issues": [],
                 "security_issues": [],
                 "aeo_issues": [],
                 "quick_fixes": ["❌ FIRECRAWL_API_KEY is missing in backend/.env. Please add it to start analyzing."]
             }

        # The v1 SDK might return an object with a .get method or a simple dict
        crawl_data = {}
        if isinstance(crawl_result, dict):
            crawl_data = crawl_result.get('data', crawl_result)
        elif hasattr(crawl_result, 'get'):
            crawl_data = crawl_result.get('data', crawl_result)
        elif hasattr(crawl_result, 'success') and crawl_result.success:
            # Newest Firecrawl SDK might return an object
            crawl_data = getattr(crawl_result, 'data', crawl_result)
        else:
            crawl_data = crawl_result

        if not crawl_data or (isinstance(crawl_data, dict) and 'error' in crawl_data):
             error_msg = crawl_data.get('error', 'Unknown Error') if isinstance(crawl_data, dict) else f"Unexpected type: {type(crawl_data)}"
             raise HTTPException(status_code=500, detail=f"Failed to crawl the website. Detail: {error_msg}")

        # Step 3: Reconstruct file results logic
        file_results = dict(zip(files_to_check, file_results_list))

        # Run our manual checks (CPU bound, fast enough to keep sync for now)
        seo_issues = perform_seo_checks(crawl_data)
        security_issues = perform_security_checks(url_str, crawl_data, file_results)
        aeo_issues = perform_aeo_checks(crawl_data.get('html', ''), crawl_data.get('metadata', {}))

        # Step 4: Use AI to make it beginner-friendly
        print("Generating AI explanations...")
        final_report = await explainer.explain_issues(seo_issues, security_issues, aeo_issues)
        
        # Step 5: Save to Supabase
        if db:
            try:
                # We await the thread pool execution
                await asyncio.to_thread(lambda: db.table("reports").insert({
                    "url": url_str,
                    "seo_score": 100 - (len(seo_issues) * 5),
                    "security_score": 100 - (len(security_issues) * 10),
                    "report_json": final_report
                }).execute())
            except Exception as db_err:
                # Silent fail for DB in production or log to actual logger
                pass

        return final_report

    except Exception as e:
        print(f"Error during analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))
