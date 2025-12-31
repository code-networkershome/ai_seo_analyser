import os
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

class AIExplainer:
    """
    Uses OpenAI's GPT Models to explain SEO and Security issues in simple English.
    Now Async!
    """
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("WARNING: OPENAI_API_KEY not found. AI analysis will be skipped.")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=self.api_key)

    async def explain_issues(self, seo_issues, security_issues, aeo_issues):
        """
        Sends the raw data to OpenAI and gets a structured, beginner-friendly report.
        """
        if not self.client:
            return {
                "seo_issues": seo_issues, 
                "security_issues": security_issues,
                "aeo_issues": aeo_issues,
                "quick_fixes": ["OpenAI API Key missing, cannot generate specific advice."]
            }

        prompt = f"""
        You are a world-class SEO consultant and web security expert trusted by Fortune 500 companies.
        Analyze the following audit data and provide a premium, actionable report.
        
        DATA:
        SEO Issues: {json.dumps(seo_issues)}
        Security Issues: {json.dumps(security_issues)}
        AEO (Answer Engine Optimization) Issues: {json.dumps(aeo_issues)}

        Your goal is to explain these findings to a non-technical business owner in a way that drives action.
        
        CRITICAL RULES:
        1. NO HALLUCINATIONS: Explain ONLY the provided issues. Do NOT invent new problems.
        2. EXPLAINER ONLY: You are translating technical issues, not detecting new ones.
        3. PROFESSIONAL TONE: Avoid hyperbole like "you'll rank #1" or "catastrophic failure". Be measured.
        4. If a category has 0 issues, say: "Audit successful: No issues detected in this category."
        5. INCLUDE impact and fix for EVERY issue - these are mandatory fields.
        
        OUTPUT FORMAT (JSON):
        {{
            "seo_issues": [ 
                {{"issue": "Issue Title", "severity": "High/Medium/Low", "details": "Clear explanation for business owners", "impact": "Specific business impact of this issue", "fix": "Exact step-by-step fix with code examples if relevant"}} 
            ],
            "security_issues": [ 
                {{"issue": "Issue Title", "severity": "Critical/High/Medium/Low", "details": "...", "impact": "...", "fix": "..."}} 
            ],
            "aeo_issues": [ 
                {{"issue": "Issue Title", "severity": "High/Medium/Low", "details": "...", "impact": "...", "fix": "..."}} 
            ],
            "quick_fixes": [
                "🔴 [HIGH PRIORITY] First critical action - explain what to do and estimated time (e.g., '10 min fix')",
                "🟠 [MEDIUM PRIORITY] Second important action - clear actionable step",
                "🟢 [QUICK WIN] Third easy improvement - something that takes under 5 minutes",
                "💡 [BONUS TIP] One advanced recommendation for maximum impact"
            ]
        }}
        
        QUICK_FIXES RULES:
        - Prioritize by: Critical security issues first, then High SEO issues, then AEO improvements
        - Each fix should be a complete, actionable sentence (not just "fix H1 tag")
        - Include time estimates when possible (e.g., "5 min", "30 min", "requires developer")
        - Use emojis for visual priority: 🔴 High, 🟠 Medium, 🟢 Quick Win, 💡 Pro Tip
        """

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a professional web audit translator. You translate code-detected issues into business value. Do NOT detect new issues. Output JSON only."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            ai_response = json.loads(content)
            
            # Sanitize: Only keep expected keys to prevent AI from overwriting scores
            sanitized_response = {
                "seo_issues": ai_response.get("seo_issues", seo_issues),
                "security_issues": ai_response.get("security_issues", security_issues),
                "aeo_issues": ai_response.get("aeo_issues", aeo_issues),
                "quick_fixes": ai_response.get("quick_fixes", ["Review the issues above and prioritize by severity."])
            }
            
            print(f"AI Explainer: Sanitized response - SEO issues: {len(sanitized_response['seo_issues'])}, Security: {len(sanitized_response['security_issues'])}, AEO: {len(sanitized_response['aeo_issues'])}")
            return sanitized_response

        except Exception as e:
            print(f"OpenAI Error: {e}")
            # Fallback to returning raw data if AI fails
            return {
                "seo_issues": seo_issues,
                "security_issues": security_issues,
                "aeo_issues": aeo_issues,
                "quick_fixes": ["AI Analysis failed. Please check raw data."]
            }
