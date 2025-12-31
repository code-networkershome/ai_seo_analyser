# 🧠 AI SEO Analyzer - Backend Engine

The Python FastAPI backend that powers the AI SEO Analyzer. Handles web crawling, AI orchestration, scoring, and secure data persistence.

## 🚀 Core Features

### Analysis Pipeline
- **SEO Checks**: Title, meta description, headings (H1-H6), content depth, readability, DOM complexity
- **Security Checks**: HTTPS, exposed emails, API key detection (AWS, Stripe, Google, Firebase), sensitive files
- **AEO Checks**: Question-based headings, FAQ sections, JSON-LD schema, AI bot blocking detection

### AI Explainer
- **GPT-4o Integration**: Translates technical issues into business-friendly advice
- **Unique Impact/Fix**: Each issue has specific business impact and exact fix instructions
- **Priority Roadmap**: Auto-generates 4 prioritized recommendations with emoji coding

### Security Hardening
- **SSRF Protection**: DNS-based blocking of private IP ranges (10.x, 192.168.x, 127.x)
- **Rate Limiting**: 5 requests/hour per IP (in-memory middleware)
- **Safe Errors**: No internal stack traces exposed to clients

### User Tracking
- **JWT Token Extraction**: Reads user_id and email from Supabase auth tokens
- **Report Linking**: All scans saved with user_id, user_email for account history

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── analyze.py      # Main /analyze endpoint
│   ├── services/
│   │   ├── firecrawl_client.py   # Web scraping
│   │   └── supabase_client.py    # Database client
│   └── utils/
│       ├── seo_checks.py    # SEO analysis (9 checks)
│       ├── security_checks.py # Security analysis (6 checks)
│       ├── aeo_checks.py    # AEO analysis (5 checks)
│       └── ai_explainer.py  # GPT-4o AI explanations
├── main.py                  # FastAPI app with CORS, rate limiting
├── requirements.txt         # Python dependencies
├── supabase_schema.sql      # Database schema
└── .env.example             # Environment template
```

---

## 🔧 API Endpoints

### `POST /analyze`
Analyze a website for SEO, Security, and AEO issues.

**Request:**
```json
{
  "url": "https://example.com"
}
```

**Headers (Optional):**
```
Authorization: Bearer <supabase_jwt_token>
```

**Response:**
```json
{
  "seo_score": 78,
  "security_score": 89,
  "aeo_score": 70,
  "seo_issues": [...],
  "security_issues": [...],
  "aeo_issues": [...],
  "quick_fixes": [
    "🔴 [HIGH PRIORITY] Add H1 heading - 10 min fix",
    "🟠 [MEDIUM PRIORITY] Create security.txt - 20 min",
    "🟢 [QUICK WIN] Adjust meta description - 5 min",
    "💡 [BONUS TIP] Add FAQPage schema for AI visibility"
  ]
}
```

---

## 📦 Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env` and fill in:
```env
OPENAI_API_KEY=sk-...
FIRECRAWL_API_KEY=fc-...
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJ...
```

### 3. Setup Database
Run `supabase_schema.sql` in Supabase SQL Editor to create the `reports` table.

### 4. Run Server
```bash
uvicorn main:app --reload --port 8000
```

---

## ☁️ Deployment (Render)

1. Create **Web Service** on Render
2. Set **Root Directory**: `backend`
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add all environment variables from `.env.example`

---

## 📊 Scoring Algorithm

```
Score = max(0, 100 - sum(penalties))

Severity Weights:
- Critical: 20 points
- High: 10 points
- Medium: 5 points
- Low: 2 points
```

Each category (SEO, Security, AEO) is scored independently.
