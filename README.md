# 🚀 AI SEO Analyzer SaaS

A production-grade, AI-powered SEO, Security, and Answer Engine Optimization (AEO) audit tool. Built to give founders and marketers enterprise-level insights with a simple, beautiful interface.

![AI SEO Analyzer](https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&q=80&w=2426&ixlib=rb-4.0.3)

## ✨ Features

### 🤖 AI-Powered Analysis
- **GPT-4o Integration**: Translates technical issues into actionable business advice
- **Zero Hallucination**: AI only explains detected issues, never invents problems
- **Priority Roadmap**: Auto-generated improvement plan with emoji-coded priorities (🔴 High, 🟠 Medium, 🟢 Quick Win, 💡 Tips)

### 📊 Comprehensive Audits
- **SEO Analysis**: Title tags, meta descriptions, headings, content depth, readability
- **Security Scanning**: HTTPS, exposed secrets (AWS/Stripe/Google keys), sensitive files
- **AEO (Answer Engine Optimization)**: Question headings, FAQ sections, Schema markup for AI bots

### 🔐 User Authentication
- **Email/Password Auth**: Secure sign-up and sign-in with Supabase
- **Report Linking**: All scans are linked to user accounts with email tracking
- **Persistent History**: View all your past audits in Supabase dashboard

### 🎨 Premium UI/UX
- **Dark/Light Mode**: Intelligent theme switching with consistent styling
- **PDF Export**: Professional audit reports with all scores and recommendations
- **Toast Notifications**: Non-blocking feedback for all user actions
- **Responsive Design**: Works beautifully on desktop and mobile

### 🛡️ Enterprise Hardening
- **SSRF Protection**: DNS-based blocking of internal network probes
- **Rate Limiting**: 5 scans/hour per IP to prevent abuse
- **Secret Detection**: High-fidelity regex for AWS, Stripe, Google, Firebase keys
- **Safe Error Handling**: No internal traces exposed to clients

---

## 🏗️ Architecture

```
ai_seo_analyser/
├── backend/                 # Python FastAPI Backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── services/       # Firecrawl, Supabase clients
│   │   └── utils/          # SEO, Security, AEO checks, AI Explainer
│   ├── main.py             # FastAPI app with rate limiting
│   ├── requirements.txt    # Python dependencies
│   └── supabase_schema.sql # Database schema
├── frontend_web/           # React + Vite Frontend
│   ├── src/
│   │   └── App.tsx         # Main application component
│   └── vercel.json         # Vercel SPA routing
├── start_backend.bat       # One-click backend launcher
└── start_frontend.bat      # One-click frontend launcher
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+ | Node.js 18+
- [Supabase](https://supabase.com/) project (for auth + database)
- [OpenAI](https://openai.com/) API Key
- [Firecrawl](https://firecrawl.dev/) API Key

### 1. Database Setup (Supabase)
1. Go to **Supabase Dashboard → SQL Editor → New Query**
2. Copy and paste contents from `backend/supabase_schema.sql`
3. Click **Run** to create the `reports` table

### 2. Environment Setup

**Backend** (`backend/.env`):
```env
OPENAI_API_KEY=sk-...
FIRECRAWL_API_KEY=fc-...
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJ...
```

**Frontend** (`frontend_web/.env`):
```env
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...
```

### 3. Run Locally
```bash
# Terminal 1: Start Backend
./start_backend.bat

# Terminal 2: Start Frontend
./start_frontend.bat
```

- Backend: http://localhost:8000
- Frontend: http://localhost:5173

---

## ⚖️ Scoring System

**Severity-Weighted Penalty Algorithm**:
| Severity | Penalty |
|----------|---------|
| Critical | -20 pts |
| High     | -10 pts |
| Medium   | -5 pts  |
| Low      | -2 pts  |

*Score = max(0, 100 - sum(penalties))* — Calculated independently for SEO, Security, and AEO.

---

## 📊 Database Schema

| Column | Type | Description |
|--------|------|-------------|
| `id` | bigint | Primary key |
| `created_at` | timestamp | When scan was created |
| `url` | text | Analyzed URL |
| `domain` | text | Extracted domain (e.g., "example.com") |
| `page_title` | text | Page title for display |
| `seo_score` | int | SEO score (0-100) |
| `security_score` | int | Security score (0-100) |
| `aeo_score` | int | AEO score (0-100) |
| `report_json` | jsonb | Full report data |
| `user_id` | uuid | User who ran the scan |
| `user_email` | text | User's email for easy lookup |

---

## ☁️ Deployment

### Backend → Render
1. Create **Web Service** on Render
2. Set **Root Directory**: `backend`
3. Add environment variables
4. Deploy!

### Frontend → Vercel
1. Create new project on Vercel
2. Set **Root Directory**: `frontend_web`
3. Framework: **Vite**
4. Add `VITE_API_URL` (your Render backend URL)
5. Deploy!

---

## 📄 License
MIT License. Built with ❤️ for the SEO Community.
