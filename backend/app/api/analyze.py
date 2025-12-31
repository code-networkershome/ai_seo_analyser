from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, HttpUrl
from typing import Optional
import asyncio
import jwt
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

def extract_user_info_from_token(authorization: Optional[str]) -> dict:
    """Extract user_id and email from Supabase JWT token."""
    if not authorization or not authorization.startswith("Bearer "):
        return {"user_id": None, "email": None}
    try:
        token = authorization.replace("Bearer ", "")
        # Decode without verification - we trust Supabase issued this token
        payload = jwt.decode(token, options={"verify_signature": False})
        return {
            "user_id": payload.get("sub"),  # 'sub' is the user_id in Supabase JWTs
            "email": payload.get("email")   # email is also in the JWT
        }
    except Exception as e:
        print(f"Token decode error: {e}")
        return {"user_id": None, "email": None}

@router.post("/analyze")
async def analyze_website(request: AnalyzeRequest, authorization: Optional[str] = Header(None)):
    """
    The main engine of our app.
    1. It takes a URL.
    2. It crawls it (Async).
    3. It runs SEO and Security checks.
    4. It asks AI to explain everything (Async).
    5. It saves the report to Supabase (if configured).
    """
    import socket
    import ipaddress
    from urllib.parse import urlparse
    
    url_str = str(request.url)
    parsed_url = urlparse(url_str)
    hostname = parsed_url.hostname

    # --- SSRF & Internal Network Protection (DNS Level) ---
    try:
        ip_addr = socket.gethostbyname(hostname)
        ip_obj = ipaddress.ip_address(ip_addr)
        
        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_reserved:
             raise HTTPException(status_code=400, detail=f"Access to internal network ({ip_addr}) is strictly prohibited.")
             
        # Metadata service protection (AWS/GCP/Azure common IP)
        if ip_addr == "169.254.169.254":
             raise HTTPException(status_code=400, detail="Access to metadata service is prohibited.")

    except socket.gaierror:
        raise HTTPException(status_code=400, detail="Could not resolve hostname.")
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=400, detail="Invalid host for analysis.")

    try:
        # Initialize our tools
        client = FirecrawlClient()
        explainer = AIExplainer()
        db = get_supabase_client()

        # Step 1: Crawl the website AND check files concurrently
        print(f"Crawling {url_str}...")
        
        # We start the main crawl with a limit (Cost Control)
        crawl_task = client.scrape_url(url_str) # FirecrawlClient.scrape_url updated soon
        
        # We start the file checks in parallel
        files_to_check = ["robots.txt", "humans.txt", "security.txt", "llms.txt"]
        file_check_tasks = [client.check_file_exists(url_str, f) for f in files_to_check]
        
        # Wait for all network IO to finish
        results = await asyncio.gather(crawl_task, *file_check_tasks)
        
        crawl_result = results[0]
        file_results_list = results[1:] 
        
        # ... logic to extract crawl_data ...
        # (Assuming current extraction logic remains or is slightly improved)
        crawl_data = {}
        if isinstance(crawl_result, dict):
            crawl_data = crawl_result.get('data', crawl_result)
        elif hasattr(crawl_result, 'get'):
            crawl_data = crawl_result.get('data', crawl_result)
        elif hasattr(crawl_result, 'success') and crawl_result.success:
            crawl_data = getattr(crawl_result, 'data', crawl_result)
        else:
            crawl_data = crawl_result

        if not crawl_data or (isinstance(crawl_data, dict) and 'error' in crawl_data):
             error_msg = crawl_data.get('error', 'Unknown Error') if isinstance(crawl_data, dict) else f"Unexpected type: {type(crawl_data)}"
             raise HTTPException(status_code=500, detail=f"Failed to crawl. Site might be blocking us or is offline. Detail: {error_msg}")

        file_results = dict(zip(files_to_check, file_results_list))

        # Run our manual checks - these have impact/fix fields
        seo_issues_raw = perform_seo_checks(crawl_data)
        security_issues_raw = perform_security_checks(url_str, crawl_data, file_results)
        aeo_issues_raw = perform_aeo_checks(crawl_data.get('html', ''), crawl_data.get('metadata', {}))
        
        print(f"Raw issues count - SEO: {len(seo_issues_raw)}, Security: {len(security_issues_raw)}, AEO: {len(aeo_issues_raw)}")

        # Step 3: Severity-Based Deterministic Scoring
        # Calculation: 100 - sum(penalties)
        # Weights: Critical=20, High=10, Medium=5, Low=2
        severity_map = {"critical": 20, "high": 10, "medium": 5, "low": 2}
        
        def calculate_category_score(issues):
            penalty = 0
            for issue in issues:
                severity = issue.get('severity', 'low').lower()
                penalty += severity_map.get(severity, 2)
            return max(0, 100 - penalty)

        seo_score = calculate_category_score(seo_issues_raw)
        security_score = calculate_category_score(security_issues_raw)
        aeo_score = calculate_category_score(aeo_issues_raw)
        
        # Overall deterministic score
        total_penalty = (100 - seo_score) + (100 - security_score) + (100 - aeo_score)
        final_score = max(0, 100 - total_penalty)
        
        print(f"CALCULATED SCORES -> SEO: {seo_score}, Security: {security_score}, AEO: {aeo_score} | Overall: {final_score}")

        # Step 4: AI Explainer (Async)
        print("Backend: Generating AI explanations...")
        try:
            ai_response = await explainer.explain_issues(seo_issues_raw, security_issues_raw, aeo_issues_raw)
            
            # Helper function to merge impact/fix from raw issues
            def merge_impact_fix(ai_issues, raw_issues):
                """Ensure AI issues have impact/fix by falling back to raw issues"""
                # Create a lookup by issue title
                raw_lookup = {issue.get('issue', ''): issue for issue in raw_issues}
                
                merged = []
                for ai_issue in ai_issues:
                    issue_title = ai_issue.get('issue', '')
                    raw_issue = raw_lookup.get(issue_title, {})
                    
                    # Use AI values, but fallback to raw for missing impact/fix
                    merged_issue = {
                        "issue": ai_issue.get('issue', issue_title),
                        "severity": ai_issue.get('severity', raw_issue.get('severity', 'Low')),
                        "details": ai_issue.get('details', raw_issue.get('details', '')),
                        "impact": ai_issue.get('impact') or raw_issue.get('impact', ''),
                        "fix": ai_issue.get('fix') or raw_issue.get('fix', '')
                    }
                    merged.append(merged_issue)
                return merged
            
            final_report = {
                "seo_issues": merge_impact_fix(ai_response.get('seo_issues', []), seo_issues_raw),
                "security_issues": merge_impact_fix(ai_response.get('security_issues', []), security_issues_raw),
                "aeo_issues": merge_impact_fix(ai_response.get('aeo_issues', []), aeo_issues_raw),
                "quick_fixes": ai_response.get('quick_fixes', ["Review the issues above and prioritize by severity."])
            }
            
        except Exception as e:
            print(f"AI Explainer Exception: {e}")
            final_report = {
                "seo_issues": seo_issues_raw,
                "security_issues": security_issues_raw,
                "aeo_issues": aeo_issues_raw,
                "quick_fixes": ["AI Analysis partially failed. Showing raw technical check results."]
            }
        
        # Inject deterministic scores into the report - GUARANTEED
        final_report["seo_score"] = int(seo_score)
        final_report["security_score"] = int(security_score)
        final_report["aeo_score"] = int(aeo_score)
        
        print(f"*** FINAL RESPONSE ***")
        print(f"  Scores -> SEO: {final_report['seo_score']}, Security: {final_report['security_score']}, AEO: {final_report['aeo_score']}")
        print(f"  Issues -> SEO: {len(final_report.get('seo_issues', []))}, Security: {len(final_report.get('security_issues', []))}, AEO: {len(final_report.get('aeo_issues', []))}")

        # Step 5: Save to Supabase (Non-blocking)
        if db:
            try:
                # Extract user info from auth token
                user_info = extract_user_info_from_token(authorization)
                
                # Extract domain from URL for easy filtering
                parsed_url = urlparse(url_str)
                domain = parsed_url.netloc.replace("www.", "")
                
                # Get page title from crawl data
                page_title = crawl_data.get('metadata', {}).get('title', '')[:255] if crawl_data.get('metadata') else None
                
                insert_data = {
                    "url": url_str,
                    "domain": domain,
                    "page_title": page_title,
                    "seo_score": int(seo_score),
                    "security_score": int(security_score),
                    "aeo_score": int(aeo_score),
                    "report_json": final_report
                }
                
                # Add user info if logged in
                if user_info["user_id"]:
                    insert_data["user_id"] = user_info["user_id"]
                    insert_data["user_email"] = user_info["email"]
                    print(f"Saving report for user: {user_info['email']} ({user_info['user_id']})")
                else:
                    print("Saving anonymous report (no user logged in)")
                    
                await asyncio.to_thread(lambda: db.table("reports").insert(insert_data).execute())
            except Exception as e:
                print(f"Supabase Save Error: {e}")

        return final_report

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        # Hide raw trace from client for security
        raise HTTPException(status_code=500, detail="An unexpected error occurred during analysis. The target site might be blocking requests or is temporarily unavailable.")
