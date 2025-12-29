from typing import Dict, List, Any
import re

def perform_security_checks(url: str, crawl_data: Dict[str, Any], file_checks: Dict[str, bool]) -> List[Dict[str, Any]]:
    """
    Analyzes the website for surface-level security and trust issues.
    These are 'passive' checks, meaning we don't try to hack anything.
    """
    issues = []
    
    # 1. HTTPS Check
    if not url.startswith("https://"):
        issues.append({
            "issue": "Insecure Connection (No HTTPS)",
            "severity": "High",
            "details": "Your website uses HTTP instead of HTTPS. This means data sent to your site isn't encrypted."
        })

    # 2. Essential Files Check (robots, humans, security, llms)
    check_files = {
        "robots.txt": ("Missing robots.txt", "Low", "This file tells search engines which parts of your site they can visit."),
        "humans.txt": ("Missing humans.txt", "Low", "An optional file to give credit to the people who built the site."),
        "security.txt": ("Missing security.txt", "Medium", "This helps security researchers contact you if they find a problem."),
        "llms.txt": ("Missing llms.txt", "Low", "A new standard to help AI bots understand your content better.")
    }

    for filename, (title, severity, desc) in check_files.items():
        if not file_checks.get(filename, False):
            issues.append({
                "issue": title,
                "severity": severity,
                "details": desc
            })

    # 3. Exposed Email Addresses
    # We look for email patterns in the text content
    content = crawl_data.get('markdown', '') + crawl_data.get('html', '')
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content)
    # Filter out common false positives if any, or just report unique ones
    unique_emails = list(set(emails))
    if unique_emails:
        issues.append({
            "issue": "Exposed Email Addresses",
            "severity": "Medium",
            "details": f"Found {len(unique_emails)} email addresses in the page source. Spammers can easily scrape these."
        })

    # 4. Internal Link Structure
    # Quickly scan hrefs to see if they look valid (not 'undefined' or malformed)
    html = crawl_data.get('html', '')
    # Match href="..." where content starts with / 
    internal_links = re.findall(r'href=["\'](/[^"\']*)["\']', html)
    malformed_links = [link for link in internal_links if '//' in link or len(link) < 2]
    
    if malformed_links:
         issues.append({
            "issue": "Malformed Internal Links",
            "severity": "Low",
            "details": f"Found {len(malformed_links)} internal links that look broken (e.g. double slashes). Check your navigation menu."
        })

    return issues
