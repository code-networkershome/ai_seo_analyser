# Project Walkthrough: AI-based SEO + Security Web Analyzer

This guide explains how the system works, the reasoning behind the code, and how you can run it yourself.

## System Architecture

We've built this system using a professional "Modular Architecture". This means instead of putting all the code in one giant file, we split it into smaller, manageable pieces based on what they do.

```mermaid
graph TD
    A[main.py: App Entry] --> B[api/analyze.py: The Route]
    C[frontend/app.py: Streamlit UI] --> B
    B --> D[services/firecrawl_client.py: Techie Crawler]
    B --> E[utils/seo_checks.py: SEO Specialist]
    B --> F[utils/security_checks.py: Security Guard]
    B --> G[utils/ai_explainer.py: Friendly Mentor]
    G --> H[Groq API (Llama 3)]
    D --> I[Firecrawl API]
```

## Why These Tools?

- **FastAPI**: We use this because it's extremely fast and handles many users at once. It also automatically checks that the data users send us (like the URL) is correct.
- **Firecrawl**: Scraping websites is hard because many sites try to block robots. Firecrawl acts like a real human browser, bypassing blocks and giving us clean data.
- **Groq**: We use Groq to translate technical jargon into simple English. It's the fastest AI inference engine available today, making our reports nearly instant.

## File-by-File Explanation

### 1. [main.py](file:///c:/Users/harsh/Desktop/AI_sec_det/backend/main.py)
This is the "Receptionist" of our app. It starts the server and directs incoming requests to the right place.

### 2. [firecrawl_client.py](file:///c:/Users/harsh/Desktop/AI_sec_det/backend/app/services/firecrawl_client.py)
The "Explorer". It uses its secret API key to visit the website you provide. It brings back the HTML (raw code) and Metadata (title, description). It also checks for special files like `robots.txt`.

### 3. [seo_checks.py](file:///c:/Users/harsh/Desktop/AI_sec_det/backend/app/utils/seo_checks.py)
The "Checker". It looks at the HTML and counts things. Does it have a title? How many headings? Are there images without descriptions? It creates a list of technical "issues".

### 4. [security_checks.py](file:///c:/Users/harsh/Desktop/AI_sec_det/backend/app/utils/security_checks.py)
The "Guard". It ensures the site is safe (HTTPS) and checks for exposed email addresses that spammers could steal. It also looks for trust files like `security.txt`.

### 5. [ai_explainer.py](file:///c:/Users/harsh/Desktop/AI_sec_det/backend/app/utils/ai_explainer.py)
The "Translator". It takes the boring technical issues (like "Missing Alt Tag") and turns them into helpful advice (like "Include descriptions for images so blind users can understand your site").

### 6. [app.py](file:///c:/Users/harsh/Desktop/AI_sec_det/frontend/app.py)
The "Face" of the project. A beautiful Streamlit interface that lets you enter a URL and see the results visually in tabs and cards.

---

## Setup & How to Run

### Step 1: Install Dependencies
Open your terminal in the `backend/` folder and run:
```bash
pip install -r requirements.txt
```
*Note: This includes `fastapi`, `uvicorn`, `firecrawl-py`, `groq`, and `textstat`.*

### Step 2: Configure API Keys
1. Copy `.env.example` to `.env`.
2. Add your **Firecrawl API Key** and **Groq API Key**.

### Step 3: Run the Backend
```bash
python main.py
```
*(Alternative for Windows: `py main.py`)*

You should see: `INFO: Uvicorn running on http://0.0.0.0:8000`

### Step 4: Connect Frontend
Once this is running, keep this terminal open and go to the `frontend/` folder to start the UI.

---

## Features & Modules

- **SEO Checks** (`seo_checks.py`):
  - Hierarchy (H1->H2->H3)
  - Readability (Flesch-Kincaid)
  - Content Depth (Word Count)
  - Tag Health (Title, Meta, Alt text)
- **Security** (`security_checks.py`):
  - HTTPS & SSL
  - Trust Files (robots.txt, security.txt, humans.txt)
  - Data Leakage (Email exposure)
- **AEO** (`aeo_checks.py`):
  - Answer Engine Optimization (AI-readiness)
  - Schema Markup detection
  - Heading-to-Answer alignment verification
- **AI Explainer** (`ai_explainer.py`):
  - Generates beginner-friendly reports using Groq (Llama 3).
