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
            "details": "The page does not have a <title> tag. This is the most important SEO element.",
            "impact": "Search engines cannot determine what your page is about, resulting in poor rankings and low click-through rates.",
            "fix": "Add a <title> tag in your HTML <head> section with a descriptive, keyword-rich title (50-60 characters)."
        })
    elif len(title) < 10:
        issues.append({
            "issue": "Title too short",
            "severity": "Medium",
            "details": f"The title '{title}' is very short. Aim for 50-60 characters.",
            "impact": "Short titles may not adequately describe your content, reducing search visibility and user engagement.",
            "fix": "Expand your title to include relevant keywords and a clear value proposition (aim for 50-60 characters)."
        })

    # 2. Meta Description Check
    description = metadata.get('description')
    if not description:
        issues.append({
            "issue": "Missing Meta Description",
            "severity": "Medium",
            "details": "Meta descriptions help people understand what your page is about in search results.",
            "impact": "Google may generate a random snippet from your page, potentially showing irrelevant content in search results.",
            "fix": "Add a <meta name='description' content='...'> tag with a compelling 120-160 character summary."
        })
    elif len(description) < 50 or len(description) > 160:
         issues.append({
            "issue": "Meta Description Length",
            "severity": "Low",
            "details": f"Your meta description is {len(description)} characters. It should be between 50 and 160 characters to ensure it's fully displayed in search results, giving potential visitors a clear idea of your content.",
            "impact": "Too short descriptions lack context; too long ones get truncated, potentially hiding important information.",
            "fix": f"Adjust your meta description to be between 50-160 characters. Current: {len(description)} chars."
        })

    # 3. H1 Count Check (The main heading)
    h1_matches = re.findall(r'<h1', html, re.IGNORECASE)
    h1_count = len(h1_matches)
    if h1_count == 0:
        issues.append({
            "issue": "Missing H1 Heading",
            "severity": "High",
            "details": "Every page should have exactly one H1 tag to tell search engines the main topic.",
            "impact": "Without an H1, search engines may struggle to understand your page's primary topic, hurting rankings.",
            "fix": "Add a single <h1> tag containing your main keyword and clearly stating the page topic."
        })
    elif h1_count > 1:
        issues.append({
            "issue": "Multiple H1 Headings",
            "severity": "Low",
            "details": f"Your page has {h1_count} H1 headings. Best practice is to have only one main heading to clearly convey the main topic of the page.",
            "impact": "Multiple H1s can confuse search engines about the page's primary focus and dilute keyword relevance.",
            "fix": f"Keep only one H1 for your main title. Convert the other {h1_count - 1} H1 tags to H2 or lower."
        })

    # 4. H2 Count (Subheadings)
    h2_matches = re.findall(r'<h2', html, re.IGNORECASE)
    h2_count = len(h2_matches)
    if h2_count == 0:
        issues.append({
            "issue": "No H2 Headings",
            "severity": "Low",
            "details": "Subheadings (H2) help organize your content for readers and search engines.",
            "impact": "Lack of structure makes content harder to scan and may reduce featured snippet opportunities.",
            "fix": "Add H2 tags to break your content into logical sections with descriptive headings."
        })

    # 5. Missing Image Alt Tags
    images_without_alt = re.findall(r'<img(?!.*?alt=["\']).*?>', html, re.IGNORECASE)
    alt_count = len(images_without_alt)
    if alt_count > 0:
        issues.append({
            "issue": "Missing Image Alt Tags",
            "severity": "Medium",
            "details": f"Found {alt_count} images without 'alt' descriptions. This hurts accessibility and image SEO.",
            "impact": "Screen readers can't describe images to visually impaired users, and Google Images can't index them properly.",
            "fix": f"Add descriptive alt='...' attributes to all {alt_count} images describing what they show."
        })

    # 6. Hierarchy Check
    headers = re.findall(r'<(h[1-6])[^>]*>', html, re.IGNORECASE)
    if h1_count == 1:
        last_level = 0 
        for tag in headers:
            level = int(tag[1])
            if level - last_level > 1 and last_level != 0:
                 issues.append({
                    "issue": "Incorrect Heading Hierarchy",
                    "severity": "Low",
                    "details": f"Found <h{level}> immediately after <h{last_level}>. You should not skip heading levels (e.g., don't go from H2 to H4).",
                    "impact": "Broken hierarchy confuses screen readers and can negatively impact your content's semantic understanding.",
                    "fix": f"Insert an <h{last_level + 1}> between <h{last_level}> and <h{level}>, or demote the <h{level}> tag."
                })
                 break
            last_level = level

    # 7. Content Depth (Thin Content)
    text_content = re.sub(r'<[^>]+>', ' ', html)
    text_content = re.sub(r'\s+', ' ', text_content).strip()
    word_count = len(text_content.split())
    
    if word_count < 300:
        issues.append({
            "issue": "Thin Content",
            "severity": "High",
            "details": f"Page has only {word_count} words. Search engines prefer substantial content (at least 300 words).",
            "impact": "Thin content pages rarely rank well and may be seen as low-quality by search engines.",
            "fix": f"Expand your content by {300 - word_count} words with valuable, relevant information."
        })

    # 8. Readability Score
    try:
        from textstat import textstat
        score = textstat.flesch_reading_ease(text_content)
        if score < 50:
             issues.append({
                "issue": "Poor Readability",
                "severity": "Medium",
                "details": f"Flesch Reading Ease score is {score:.1f} (Difficult to read). Aim for 60+ for general audiences.",
                "impact": "Complex content leads to higher bounce rates and lower engagement, signaling poor quality to Google.",
                "fix": "Use shorter sentences (under 20 words), simpler vocabulary, and more paragraph breaks."
            })
    except ImportError:
        pass

    # 9. DOM Complexity
    total_tags = len(re.findall(r'<[a-zA-Z]+', html))
    if total_tags > 1500:
        issues.append({
            "issue": "Excessive DOM Size",
            "severity": "Low",
            "details": f"Your webpage contains {total_tags} HTML elements, which can slow down loading times. Aim for fewer than 1500 elements to ensure faster page speed and better user experience.",
            "impact": "Large DOMs increase memory usage, slow rendering, and hurt Core Web Vitals scores.",
            "fix": f"Reduce DOM size by removing unnecessary elements. Target: under 1500 (current: {total_tags})."
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
