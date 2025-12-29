from typing import Dict, List, Any
import re

def perform_aeo_checks(html: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Analyzes the content for Answer Engine Optimization (AEO) patterns.
    AEO focuses on being cited by AI models (ChatGPT, Gemini, Perplexity).
    
    Key metrics:
    1. Question-based headings (What/How/Why).
    2. Concise answers (40-60 words) immediately following headings.
    3. Structural clarity (FAQ sections, Schema markup).
    """
    issues = []
    
    # Pre-compute common regex
    # Matches headings H1-H3
    heading_pattern = re.compile(r'<(h[1-3])[^>]*>(.*?)</\1>', re.IGNORECASE | re.DOTALL)
    headings = heading_pattern.findall(html)
    
    # 1. Check for Question-based Headings
    # AI models often look for direct questions to answer users.
    question_starters = ["what", "how", "why", "where", "when", "who", "can", "does", "is", "are"]
    question_headings_count = 0
    
    for _, text in headings:
        clean_text = re.sub(r'<[^>]+>', '', text).strip().lower()
        if any(clean_text.startswith(starter) for starter in question_starters) or '?' in clean_text:
            question_headings_count += 1
            
    if question_headings_count == 0:
        issues.append({
            "issue": "No Question-Based Headings",
            "severity": "High",
            "details": "AI Search Engines look for 'What', 'How', 'Why' questions in headings. Your content lacks these direct question patterns."
        })

    # 2. Check for Concise Answer Paragraphs (Strict Alignment)
    # We look for <hX>...<p>Answer</p> where Answer is 40-60 words.
    # Regex to find <p> tag immediately following a closing heading tag
    # We allow some whitespace/newlines
    alignment_matches = re.finditer(r'</h[1-6]>\s*<p[^>]*>(.*?)</p>', html, re.IGNORECASE | re.DOTALL)
    strict_answer_count = 0
    
    for match in alignment_matches:
        p_content = match.group(1)
        clean_p = re.sub(r'<[^>]+>', '', p_content).strip()
        word_count = len(clean_p.split())
        if 40 <= word_count <= 60:
            strict_answer_count += 1
            
    if strict_answer_count == 0:
        issues.append({
            "issue": "Missing Strict Answer Alignment",
            "severity": "Medium",
            "details": "AI models prioritize answers immediately following headings. Found 0 headings followed instantly by a 40-60 word answer."
        })

    # 3. Detect FAQ Section
    # Look for "FAQ" or "Frequently Asked Questions" in content
    if not re.search(r'freq(uently)?\s*asked\s*quest(ions)?|faq', html, re.IGNORECASE):
        issues.append({
            "issue": "Missing FAQ Section",
            "severity": "Medium",
            "details": "An FAQ section is the easiest way to rank in AI answers. No obvious FAQ section was detected."
        })

    # 4. Check for Schema Markup (JSON-LD)
    has_schema = False
    scripts = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.IGNORECASE | re.DOTALL)
    for script_content in scripts:
        lower_content = script_content.lower()
        if '"faqpage"' in lower_content or '"howto"' in lower_content:
            has_schema = True
            break
            
    if not has_schema:
        issues.append({
            "issue": "Missing AI-Friendly Schema",
            "severity": "High",
            "details": "We didn't find 'FAQPage' or 'HowTo' schema markup. This code helps robots understand your content structure instantly."
        })

    # 5. AI Readiness Signals (Meta Robots)
    # Check if we are blocking AI bots via regular meta robots
    # <meta name="robots" content="noindex" /> is bad for visibility
    meta_robots = re.search(r'<meta\s+name=["\']robots["\']\s+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
    if meta_robots:
        content = meta_robots.group(1).lower()
        if "noindex" in content:
             issues.append({
                "issue": "AI Blocking Detected (noindex)",
                "severity": "Critical",
                "details": "Your meta robots tag says 'noindex'. This tells AI and Search Engines to IGNORE your page."
            })

    return issues
