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
        You are a world-class SEO and Cybersecurity expert (like a mix of Brian Dean and a white-hat hacker).
        Analyze the following raw audit data for a website and provide a premium, Semrush-style report.
        
        DATA:
        SEO Issues: {json.dumps(seo_issues)}
        Security Issues: {json.dumps(security_issues)}
        AEO (Answer Engine) Issues: {json.dumps(aeo_issues)}

        Your goal is to explain these findings to a non-technical business owner.
        
        OUTPUT FORMAT (JSON):
        {{
            "seo_issues": [ {{"issue": "Title Tag Missing", "severity": "High", "details": "Explanation..."}} ],
            "security_issues": [ {{"issue": "SSL Missing", "severity": "Critical", "details": "Explanation..."}} ],
            "aeo_issues": [ {{"issue": "No schema markup", "severity": "Medium", "details": "Explanation..."}} ],
            "quick_fixes": [ "Step-by-step actionable list of top 3 priorities" ]
        }}
        
        Keep explanations concise, professional, and actionable.
        """

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o", # Using a high-quality model
                messages=[
                    {"role": "system", "content": "You are a helpful SEO Audit assistant. Output JSON only."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content)

        except Exception as e:
            print(f"OpenAI Error: {e}")
            # Fallback to returning raw data if AI fails
            return {
                "seo_issues": seo_issues,
                "security_issues": security_issues,
                "aeo_issues": aeo_issues,
                "quick_fixes": ["AI Analysis failed. Please check raw data."]
            }
