from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from app.services.firecrawl_client import FirecrawlClient
from app.utils.seo_checks import perform_seo_checks
from app.utils.security_checks import perform_security_checks
from app.utils.aeo_checks import perform_aeo_checks
from app.utils.ai_explainer import AIExplainer

router = APIRouter()

# This is our input 'Blueprint'. It tells FastAPI what to expect from the user.
class AnalyzeRequest(BaseModel):
    url: HttpUrl

@router.post("/analyze")
async def analyze_website(request: AnalyzeRequest):
    """
    The main engine of our app.
    1. It takes a URL.
    2. It crawls it.
    3. It runs SEO and Security checks.
    4. It asks AI to explain everything.
    """
    url_str = str(request.url)
    
    try:
        # Initialize our tools
        client = FirecrawlClient()
        explainer = AIExplainer()

        # Step 1: Crawl the website
        print(f"Crawling {url_str}...")
        crawl_data = client.scrape_url(url_str)
        
        if not crawl_data:
             raise HTTPException(status_code=500, detail="Failed to crawl the website.")

        # Step 2: Check for essential files (robots.txt, etc)
        # We do this separately because they might not be in the main crawl
        files_to_check = ["robots.txt", "humans.txt", "security.txt", "llms.txt"]
        file_results = {}
        for filename in files_to_check:
            file_results[filename] = client.check_file_exists(url_str, filename)

        # Step 3: Run our manual checks
        seo_issues = perform_seo_checks(crawl_data)
        security_issues = perform_security_checks(url_str, crawl_data, file_results)
        aeo_issues = perform_aeo_checks(crawl_data.get('html', ''), crawl_data.get('metadata', {}))

        # Step 4: Use AI to make it beginner-friendly
        print("Generating AI explanations...")
        final_report = explainer.explain_issues(seo_issues, security_issues, aeo_issues)

        return final_report

    except Exception as e:
        print(f"Error during analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))
