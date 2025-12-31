# 🎨 AI SEO Analyzer - Frontend

A premium React dashboard for the AI SEO Analyzer, built with Vite, Tailwind CSS, and Framer Motion.

## ✨ Features

### 🔐 Authentication
- **Email/Password Auth**: Secure sign-up and sign-in with Supabase
- **Session Persistence**: Automatic session restoration on page load
- **Sign Out**: Clean session termination

### 📊 Analysis Dashboard
- **Three-Tab Interface**: SEO, Security, and AI Readiness reports
- **Score Cards**: Visual display of category scores (0-100)
- **Issue Cards**: Each issue shows severity, details, business impact, and fix

### 🎯 Improvement Roadmap
- **AI-Generated Priorities**: GPT-4o creates actionable recommendations
- **Priority Coding**: 🔴 High, 🟠 Medium, 🟢 Quick Win, 💡 Tips
- **Time Estimates**: Each fix includes estimated completion time

### 📄 PDF Export
- **Professional Reports**: Print-ready audit document
- **Complete Data**: All scores, issues, and recommendations included
- **Branded Design**: Clean layout with proper typography

### 🌗 Theme Support
- **Dark/Light Mode**: Toggle between themes
- **Consistent Styling**: All components properly themed
- **System Preference**: Respects user's OS theme setting

### 💬 Toast Notifications
- **Non-blocking Feedback**: Success/error messages don't interrupt workflow
- **Auto-dismiss**: Notifications fade after 3 seconds

---

## 🛠️ Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **Lucide React** for icons
- **Supabase JS** for auth

---

## 📦 Setup

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment
Create `.env` file:
```env
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...
```

### 3. Run Development Server
```bash
npm run dev
```

Open http://localhost:5173

---

## 📁 Project Structure

```
frontend_web/
├── src/
│   ├── App.tsx        # Main application (auth, dashboard, PDF)
│   ├── main.tsx       # React entry point
│   └── index.css      # Tailwind + custom styles
├── index.html         # HTML template
├── vercel.json        # Vercel SPA routing
└── tailwind.config.js # Tailwind configuration
```

---

## ☁️ Deployment (Vercel)

1. Create new project on Vercel
2. Set **Root Directory**: `frontend_web`
3. **Framework Preset**: Vite
4. Add environment variables:
   - `VITE_API_URL`: Your backend URL (Render)
   - `VITE_SUPABASE_URL`: Your Supabase project URL
   - `VITE_SUPABASE_ANON_KEY`: Your Supabase anon key
5. Deploy!

The `vercel.json` file handles SPA routing automatically.

---

## 🎨 UI Components

| Component | Description |
|-----------|-------------|
| Score Cards | Display SEO, Security, AEO scores |
| Issue Cards | Show issue title, severity badge, details, impact, fix |
| Tab Navigation | Switch between SEO, Security, AI Readiness |
| Improvement Roadmap | Priority-coded action items |
| Auth Modal | Sign in / Sign up form |
| Toast | Non-blocking notifications |
| PDF Report | Print-optimized audit document |
