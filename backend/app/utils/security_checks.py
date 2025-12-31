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
            "details": "Your website uses HTTP instead of HTTPS. This means data sent to your site isn't encrypted.",
            "impact": "User data (passwords, forms) can be intercepted. Browsers show 'Not Secure' warnings, hurting trust.",
            "fix": "Install an SSL certificate (free via Let's Encrypt) and redirect all HTTP to HTTPS."
        })

    # 2. Essential Files Check (robots, humans, security, llms)
    check_files = {
        "robots.txt": {
            "title": "Missing robots.txt",
            "severity": "Low",
            "details": "This file tells search engines which parts of your site they can visit.",
            "impact": "Search engines will crawl all pages indiscriminately, potentially indexing private sections.",
            "fix": "Create a robots.txt file in your root directory with crawling rules (User-agent: * Disallow: /private/)."
        },
        "humans.txt": {
            "title": "Missing humans.txt",
            "severity": "Low",
            "details": "The 'humans.txt' file is missing. Although optional, it's a nice way to give credit to your team.",
            "impact": "This is informational only. No direct SEO or security impact.",
            "fix": "Create a humans.txt file listing your team, technologies used, and acknowledgments."
        },
        "security.txt": {
            "title": "Missing security.txt",
            "severity": "Medium",
            "details": "This helps security researchers contact you responsibly if they find a vulnerability.",
            "impact": "Without it, white-hat hackers may not know how to report issues to you, leaving bugs unpatched.",
            "fix": "Create /.well-known/security.txt with your security contact email and disclosure policy."
        },
        "llms.txt": {
            "title": "Missing llms.txt",
            "severity": "Low",
            "details": "A new standard to help AI bots like ChatGPT and Perplexity understand your content better.",
            "impact": "AI models may not properly attribute or summarize your content in AI-powered search.",
            "fix": "Create an llms.txt file describing your site's purpose and content policies for AI crawlers."
        }
    }

    for filename, info in check_files.items():
        if not file_checks.get(filename, False):
            issues.append({
                "issue": info["title"],
                "severity": info["severity"],
                "details": info["details"],
                "impact": info["impact"],
                "fix": info["fix"]
            })

    # 3. Exposed Email Addresses
    content = crawl_data.get('markdown', '') + crawl_data.get('html', '')
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content)
    unique_emails = list(set(emails))
    if unique_emails:
        issues.append({
            "issue": "Exposed Email Addresses",
            "severity": "Medium",
            "details": f"Found {len(unique_emails)} email addresses in the page source. Spammers can easily scrape these.",
            "impact": "Exposed emails lead to spam, phishing attempts, and potential social engineering attacks.",
            "fix": "Use contact forms instead of plain text emails, or obfuscate emails with JavaScript."
        })

    # 5. Sensitive Data Exposure (API Keys, etc.)
    secret_patterns = {
        "AWS Access Key": r'AKIA[0-9A-Z]{16}',
        "Google API Key": r'AIza[0-9A-Za-z\-_]{35}',
        "Stripe Secret Key": r'sk_live_[0-9a-zA-Z]{24}',
        "Firebase API Key": r'AIzaSy[A-Za-z0-9_-]{33}'
    }
    
    for label, pattern in secret_patterns.items():
        match = re.search(pattern, content)
        if match:
            issues.append({
                "issue": f"Exposed {label}",
                "severity": "Critical",
                "details": f"A potential {label} was found in your website's source code ({match.group()[:8]}...). This is a high-risk security vulnerability.",
                "impact": "Attackers can use these keys to access your cloud infrastructure or billing accounts, leading to data theft or massive costs.",
                "fix": f"Immediately revoke the {label} in your provider's dashboard and store it in backend environment variables only."
            })

    # 6. Sensitive Path Detection
    sensitive_paths = {
        ".env": {
            "desc": "Environment variables file containing sensitive secrets.",
            "impact": "Exposes database passwords, API keys, and other secrets to attackers.",
            "fix": "Add .env to .gitignore and ensure it's not web-accessible."
        },
        ".git/config": {
            "desc": "Git configuration showing internal repository structure.",
            "impact": "Attackers can download your entire Git history including private code.",
            "fix": "Block access to .git folder using web server configuration (deny all in .htaccess or nginx)."
        },
        ".bak": {
            "desc": "Backup file which may contain source code or database dumps.",
            "impact": "Old backups often contain passwords or outdated vulnerable code.",
            "fix": "Delete all .bak files from public directories and store backups securely offline."
        },
        "config.php": {
            "desc": "Database configuration file references.",
            "impact": "Exposes database credentials allowing attackers to access your data.",
            "fix": "Move config files outside web root and use environment variables for credentials."
        },
        "web.config": {
            "desc": "Azure/IIS configuration file references.",
            "impact": "Reveals server configuration, security settings, and connection strings.",
            "fix": "Ensure web.config is not publicly accessible and contains no sensitive data."
        }
    }
    
    for path, info in sensitive_paths.items():
        if path in content.lower():
            issues.append({
                "issue": f"Sensitive File Reference: {path}",
                "severity": "High",
                "details": f"Found a reference to '{path}' in your source code. {info['desc']}",
                "impact": info["impact"],
                "fix": info["fix"]
            })

    return issues
