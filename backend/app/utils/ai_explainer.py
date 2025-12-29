import os
from groq import Groq
from typing import List, Dict, Any
from dotenv import load_dotenv
import json

load_dotenv()

class AIExplainer:
    """
    Uses Groq (running Llama 3) to explain technical issues in plain English.
    We chose Groq because it is incredibly fast and uses an easy-to-use API 
    that works similarly to OpenAI.
    """
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        # Initialize the Groq client
        self.client = Groq(api_key=api_key)
        # We use llama3-8b-8192 as it's balanced for speed and reasoning
        self.model = "llama3-8b-8192"

    def explain_issues(self, seo_issues: List[Dict[str, Any]], security_issues: List[Dict[str, Any]], aeo_issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Takes a list of technical issues and returns human-friendly explanations and fixes using Groq.
        """
        if not seo_issues and not security_issues and not aeo_issues:
            return {
                "seo_issues": [],
                "security_issues": [],
                "aeo_issues": [],
                "quick_fixes": ["Your website looks great! No major issues found."]
            }

        # The prompt remains largely the same, but we ensure clear JSON instructions
        prompt = f"""
        You are a helpful website mentor for beginners. 
        I will give you a list of SEO, Security, and AEO (Answer Engine Optimization) issues found on a website.
        
        Your task:
        1. Explain each issue in plain English (no jargon).
        2. Explain why it matters to a website owner.
        3. Provide one simple, non-technical fix for each.
        4. Do NOT invent any new data or hallucinate. Use ONLY the issues provided.
        
        SEO ISSUES:
        {seo_issues}
        
        SECURITY ISSUES:
        {security_issues}

        AEO ISSUES:
        {aeo_issues}

        IMPORTANT: Your response MUST be valid JSON. 
        DO NOT include any text before or after the JSON.

        RESPONSE FORMAT:
        {{
          "seo_issues": [
            {{ "issue": "Name of issue", "severity": "Level", "details": "Human explanation and fix" }}
          ],
          "security_issues": [
            {{ "issue": "Name of issue", "severity": "Level", "details": "Human explanation and fix" }}
          ],
          "aeo_issues": [
            {{ "issue": "Name of issue", "severity": "Level", "details": "Human explanation and fix" }}
          ],
          "quick_fixes": [
            "short bullet point fix",
            "another fix"
          ]
        }}
        """

        try:
            # We call the Groq completions API
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model,
                # We force it to return JSON
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            content = response.choices[0].message.content
            return json.loads(content)

        except Exception as e:
            print(f"AI Explanation Error (Groq): {e}")
            # Fallback in case of AI error
            return {
                "seo_issues": seo_issues,
                "security_issues": security_issues,
                "aeo_issues": aeo_issues,
                "quick_fixes": ["Please check your website settings for SEO and Security improvements."]
            }
