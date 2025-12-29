from typing import Dict, List, Any
import re

def perform_seo_checks(crawl_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Analyzes the crawled data to find common SEO issues.
    SEO (Search Engine Optimization) is what helps a website show up on Google.
    """
    issues = []
    metadata = crawl_data.get('metadata', {})
    html = crawl_data.get('html', '')
    
    # 1. Page Title Check
    title = metadata.get('title')
    if not title:
        issues.append({
            "issue": "Missing Page Title",
            "severity": "High",
            "details": "The page does not have a <title> tag. This is the most important SEO element."
        })
    elif len(title) < 10:
        issues.append({
            "issue": "Title too short",
            "severity": "Medium",
            "details": f"The title '{title}' is very short. Aim for 50-60 characters."
        })

    # 2. Meta Description Check
    description = metadata.get('description')
    if not description:
        issues.append({
            "issue": "Missing Meta Description",
            "severity": "Medium",
            "details": "Meta descriptions help people understand what your page is about in search results."
        })
    elif len(description) < 50 or len(description) > 160:
         issues.append({
            "issue": "Meta Description Length",
            "severity": "Low",
            "details": f"Your description is {len(description)} chars. Optimal length is between 50-160 characters."
        })

    # 3. H1 Count Check (The main heading)
    h1_matches = re.findall(r'<h1', html, re.IGNORECASE)
    h1_count = len(h1_matches)
    if h1_count == 0:
        issues.append({
            "issue": "Missing H1 Heading",
            "severity": "High",
            "details": "Every page should have exactly one H1 tag to tell search engines the main topic."
        })
    elif h1_count > 1:
        issues.append({
            "issue": "Multiple H1 Headings",
            "severity": "Low",
            "details": f"Found {h1_count} H1 tags. It's best practice to have only one main heading."
        })

    # 4. H2 Count (Subheadings)
    h2_matches = re.findall(r'<h2', html, re.IGNORECASE)
    h2_count = len(h2_matches)
    # We just track this for info, maybe not a specific 'issue' unless 0
    if h2_count == 0:
        issues.append({
            "issue": "No H2 Headings",
            "severity": "Low",
            "details": "Subheadings (H2) help organize your content for readers and search engines."
        })

    # 5. Missing Image Alt Tags
    # Alt tags help visually impaired users and search engines 'see' your images
    images_without_alt = re.findall(r'<img(?!.*?alt=["\']).*?>', html, re.IGNORECASE)
    alt_count = len(images_without_alt)
    if alt_count > 0:
        issues.append({
            "issue": "Missing Image Alt Tags",
            "severity": "Medium",
            "details": f"Found {alt_count} images without 'alt' descriptions. This hurts accessibility."
        })

    # 6. Hierarchy Check (H1 -> H2 -> H3)
    # searching for all headers in order
    headers = re.findall(r'<(h[1-6])[^>]*>', html, re.IGNORECASE)
    # We want to see if we skip levels, e.g. H1 -> H3 (skipping H2 is debatable, but H2 -> H4 is bad)
    # Or if H2 appears before H1 (already caught by H1 count check effectively, but let's be strict)
    # Simple check: Ensure we don't have H3 without a preceding H2, etc.
    if h1_count == 1:
        # Simplified hierarchy check logic
        # If we find h(N) and the previous highest was h(N-2) or less...
        # actually, standard rule: don't skip levels downwards. h1->h2 ok, h2->h3 ok. h2->h4 bad.
        last_level = 0 
        for tag in headers:
            level = int(tag[1])
            if level - last_level > 1 and last_level != 0:
                 # e.g. last=2 (H2), current=4 (H4) -> 4-2=2 > 1. Bad.
                 issues.append({
                    "issue": "Incorrect Heading Hierarchy",
                    "severity": "Low",
                    "details": f"Found <h{level}> immediately after <h{last_level}>. You should not skip heading levels (e.g., don't go from H2 to H4)."
                })
                 break # Report once
            last_level = level

    # 7. Content Depth (Thin Content)
    # We need plain text. HTML to Text is rough with Regex but usually sufficient for estimation.
    text_content = re.sub(r'<[^>]+>', ' ', html)
    text_content = re.sub(r'\s+', ' ', text_content).strip()
    word_count = len(text_content.split())
    
    if word_count < 300:
        issues.append({
            "issue": "Thin Content",
            "severity": "High",
            "details": f"Page has only {word_count} words. Search engines prefer substantial content (at least 300 words)."
        })

    # 8. Readability Score
    try:
        from textstat import textstat
        # Flesch Reading Ease: 60-70 is standard. < 50 is hard.
        score = textstat.flesch_reading_ease(text_content)
        if score < 50:
             issues.append({
                "issue": "Poor Readability",
                "severity": "Medium",
                "details": f"Flesch Reading Ease score is {score:.1f} (Confusing). Aim for 60+. Use shorter sentences and simpler words."
            })
    except ImportError:
        pass # textstat might not be installed in all envs, skip if so

    # 9. DOM Complexity (Performance Proxy)
    # Count total tags
    total_tags = len(re.findall(r'<[a-zA-Z]+', html))
    if total_tags > 1500:
        issues.append({
            "issue": "Excessive DOM Size",
            "severity": "Low",
            "details": f"Found {total_tags} HTML elements. Large pages (>1500) can be slow to load and parse."
        })

    return issues

def get_seo_stats(crawl_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns raw counts and data for display.
    """
    html = crawl_data.get('html', '')
    return {
        "title": crawl_data.get('metadata', {}).get('title', 'Missing'),
        "h1_count": len(re.findall(r'<h1', html, re.IGNORECASE)),
        "h2_count": len(re.findall(r'<h2', html, re.IGNORECASE)),
        "internal_links": len(re.findall(r'href=["\']/', html)) # Simple relative link check
    }
