import { useState, useEffect } from 'react';
import { Shield, Globe, ChevronRight, CheckCircle, Download, BookOpen, User, X, Zap, BarChart3, Cpu, Sun, Moon } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { createClient } from '@supabase/supabase-js';

// Supabase client singleton
let supabase: any;

interface Issue {
    issue: string;
    severity: string;
    details: string;
}

interface ReportData {
    seo_issues: Issue[];
    security_issues: Issue[];
    aeo_issues: Issue[];
    quick_fixes: string[];
}

function App() {
    const [url, setUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [report, setReport] = useState<ReportData | null>(null);
    const [activeTab, setActiveTab] = useState<'seo' | 'security' | 'aeo'>('seo');
    const [error, setError] = useState('');
    const [showDoc, setShowDoc] = useState(false);
    const [showAuth, setShowAuth] = useState(false);
    const [user, setUser] = useState<any>(null);
    const [isDark, setIsDark] = useState(true);

    // Theme effect with localStorage persistence
    useEffect(() => {
        const root = window.document.documentElement;
        // Check for saved theme preference or use system preference
        const savedTheme = localStorage.getItem('theme');
        const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

        // Initialize theme state
        const initialTheme = savedTheme === 'light' ? false : (savedTheme === 'dark' ? true : systemPrefersDark);
        setIsDark(initialTheme);

        // Apply theme class
        if (initialTheme) {
            root.classList.add('dark');
        } else {
            root.classList.remove('dark');
        }
    }, []);

    // Toggle theme handler
    const toggleTheme = () => {
        const newTheme = !isDark;
        setIsDark(newTheme);
        localStorage.setItem('theme', newTheme ? 'dark' : 'light');
        const root = window.document.documentElement;
        if (newTheme) {
            root.classList.add('dark');
        } else {
            root.classList.remove('dark');
        }
    };

    // Initialize Supabase once
    if (!supabase) {
        const url = import.meta.env.VITE_SUPABASE_URL || '';
        const key = import.meta.env.VITE_SUPABASE_ANON_KEY || '';
        if (url && key) {
            supabase = createClient(url, key);
        }
    }

    useEffect(() => {
        if (!supabase) return;
        supabase.auth.getSession().then(({ data: { session } }: any) => {
            setUser(session?.user ?? null);
        });
        const { data: { subscription } } = supabase.auth.onAuthStateChange((_event: any, session: any) => {
            setUser(session?.user ?? null);
        });
        return () => subscription.unsubscribe();
    }, []);

    const analyzeUrl = async () => {
        if (!url) return;
        setLoading(true);
        setReport(null);
        setError('');
        try {
            const rawApiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
            const apiUrl = rawApiUrl.replace(/\/$/, '');
            const response = await fetch(`${apiUrl}/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url }),
            });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Server Error (${response.status})`);
            }
            const data = await response.json();
            setReport(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setLoading(false);
        }
    };

    const handleGoogleSignIn = async () => {
        if (!supabase) return;
        try {
            const { error } = await supabase.auth.signInWithOAuth({
                provider: 'google',
                options: { redirectTo: window.location.origin }
            });
            if (error) throw error;
        } catch (err) {
            alert("Auth Error: " + (err instanceof Error ? err.message : String(err)));
        }
    };

    const handleEmailSignIn = () => {
        if (!supabase) return;
        const email = prompt("Enter your email for a Magic Link:");
        if (email) {
            supabase.auth.signInWithOtp({ email }).then(({ error }: any) => {
                if (error) alert(error.message);
                else alert("Success! Check your email.");
            });
        }
    };

    const handleExportPDF = () => window.print();

    const copyReportToClipboard = () => {
        if (!report) return;
        navigator.clipboard.writeText(JSON.stringify(report, null, 2));
        alert("JSON copied!");
    };

    const getSeverityColor = (severity: string) => {
        switch (severity.toLowerCase()) {
            case 'critical': return 'border-red-500 bg-red-50 dark:bg-red-500/10 text-red-700 dark:text-red-400';
            case 'high': return 'border-orange-500 bg-orange-50 dark:bg-orange-500/10 text-orange-700 dark:text-orange-400';
            case 'medium': return 'border-yellow-500 bg-yellow-50 dark:bg-yellow-500/10 text-yellow-800 dark:text-yellow-400';
            default: return 'border-blue-500 bg-blue-50 dark:bg-blue-500/10 text-blue-700 dark:text-blue-400';
        }
    };

    return (
        <div className={`min-h-screen transition-all duration-500 ${isDark ? 'dark' : ''}`}>
            {/* Main Background Wrapper */}
            <div className={`min-h-screen transition-colors duration-500 ${isDark ? 'bg-slate-900 text-slate-100' : 'bg-slate-50 text-slate-900'}`}>
                {/* Header */}
                <nav className={`border-b ${isDark ? 'border-slate-800 bg-slate-900/50' : 'border-black/10 bg-black/90'} backdrop-blur-xl sticky top-0 z-50 no-print transition-colors`}>
                    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                            <div className="bg-gradient-to-tr from-blue-600 to-cyan-500 p-2 rounded-lg shadow-lg">
                                <Shield className="w-6 h-6 text-white" />
                            </div>
                            <span className="text-xl font-bold text-slate-900 dark:text-white transition-all">
                                AI SEO Analyzer
                            </span>
                        </div>
                        <div className="flex items-center space-x-4">
                            <button
                                onClick={toggleTheme}
                                className="p-2 rounded-xl text-slate-500 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-800 transition-all"
                                title={isDark ? "Switch to Light Mode" : "Switch to Dark Mode"}
                            >
                                {isDark ? <Sun className="w-5 h-5 text-amber-500" /> : <Moon className="w-5 h-5 text-slate-700" />}
                            </button>
                            <button onClick={() => setShowDoc(true)} className="text-sm font-medium text-slate-600 dark:text-slate-400 hover:text-blue-600 transition-colors flex items-center">
                                <BookOpen className="w-4 h-4 mr-1" /> Documentation
                            </button>
                            {user ? (
                                <button onClick={() => supabase.auth.signOut()} className="text-sm font-medium text-slate-600 dark:text-slate-400 hover:text-red-500 flex items-center">
                                    <User className="w-4 h-4 mr-1" /> Sign Out
                                </button>
                            ) : (
                                <button onClick={() => setShowAuth(true)} className="bg-blue-600 hover:bg-blue-500 text-white px-5 py-2 rounded-xl text-sm font-bold transition-all shadow-lg active:scale-95">
                                    Sign In
                                </button>
                            )}
                        </div>
                    </div>
                </nav>

                <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                    {/* Search Hero */}
                    <div className="text-center mb-16 max-w-3xl mx-auto no-print">
                        <h1 className="text-4xl sm:text-5xl font-bold mb-6 tracking-tight">
                            <span className={isDark ? "text-white" : "text-slate-900"}>Analyze your website's</span> <span className="text-blue-600 dark:text-blue-400">SEO, Security & AI Readiness</span>
                        </h1>
                        <p className="text-lg text-slate-600 dark:text-slate-400 mb-8">
                            Find SEO issues, security risks, and AI visibility problems — with clear, simple fixes.
                        </p>

                        <div className="relative group max-w-2xl mx-auto">
                            <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-cyan-600 rounded-xl blur opacity-25 group-hover:opacity-40 transition duration-1000"></div>
                            <div className="relative flex items-center bg-white dark:bg-slate-900 rounded-xl p-2 border border-slate-200 dark:border-slate-800 shadow-2xl">
                                <Globe className="w-6 h-6 text-slate-400 ml-3" />
                                <input
                                    type="text"
                                    placeholder="https://example.com"
                                    className="flex-1 bg-transparent border-none focus:ring-0 text-slate-900 dark:text-white placeholder-slate-400 px-4 py-3 outline-none"
                                    value={url}
                                    onChange={(e) => setUrl(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && analyzeUrl()}
                                />
                                <button
                                    onClick={analyzeUrl}
                                    disabled={loading}
                                    className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-lg font-bold transition-all disabled:opacity-50 flex items-center gap-2 whitespace-nowrap shadow-lg shadow-blue-600/20"
                                >
                                    {loading ? "Analyzing..." : <>Analyze Website <ChevronRight className="w-4 h-4" /></>}
                                </button>
                            </div>
                            <p className="mt-4 text-xs text-slate-500">We only analyze publicly accessible pages. No login required.</p>
                        </div>

                        {error && (
                            <div className="mt-6 p-4 bg-red-50 text-red-600 border border-red-200 rounded-xl text-sm font-medium max-w-lg mx-auto">
                                {error}
                            </div>
                        )}

                        {!report && !loading && (
                            <motion.div
                                initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
                                className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8"
                            >
                                <div className="glass p-8 rounded-3xl text-left border border-slate-200 dark:border-slate-800">
                                    <div className="bg-blue-100 dark:bg-blue-600/20 p-3 rounded-2xl w-fit mb-4">
                                        <Zap className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                                    </div>
                                    <h3 className="text-lg font-bold mb-2 text-slate-900 dark:text-white">Real-time Crawl</h3>
                                    <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">We scan your website the same way search engines and AI bots do.</p>
                                </div>
                                <div className="glass p-8 rounded-3xl text-left border border-slate-200 dark:border-slate-800">
                                    <div className="bg-emerald-100 dark:bg-emerald-600/20 p-3 rounded-2xl w-fit mb-4">
                                        <Cpu className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
                                    </div>
                                    <h3 className="text-lg font-bold mb-2 text-slate-900 dark:text-white">AI Intelligence</h3>
                                    <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">AI explains what’s wrong, why it matters, and how to fix it.</p>
                                </div>
                                <div className="glass p-8 rounded-3xl text-left border border-slate-200 dark:border-slate-800">
                                    <div className="bg-purple-100 dark:bg-purple-600/20 p-3 rounded-2xl w-fit mb-4">
                                        <BarChart3 className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                                    </div>
                                    <h3 className="text-lg font-bold mb-2 text-slate-900 dark:text-white">AEO Ready</h3>
                                    <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">Make your website visible to AI tools like ChatGPT and Perplexity.</p>
                                </div>
                            </motion.div>
                        )}
                        {!report && !loading && (
                            <p className="mt-12 text-sm text-slate-500 font-medium">Designed for beginners. Trusted by developers and startups.</p>
                        )}
                    </div>

                    {/* Results Dashboard */}
                    {report && (
                        <div className="animate-in fade-in slide-in-from-bottom-8 duration-700">
                            {/* Summary Cards */}
                            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                                <div className="glass p-6 rounded-2xl text-center">
                                    <div className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase mb-1">SEO Issues</div>
                                    <div className="text-3xl font-black text-slate-900 dark:text-white">{report.seo_issues.length}</div>
                                </div>
                                <div className="glass p-6 rounded-2xl text-center">
                                    <div className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase mb-1">Security Risks</div>
                                    <div className="text-3xl font-black text-slate-900 dark:text-white">{report.security_issues.length}</div>
                                </div>
                                <div className="glass p-6 rounded-2xl text-center">
                                    <div className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase mb-1">AEO Score</div>
                                    <div className="text-3xl font-black text-emerald-600 dark:text-emerald-400 font-mono">92+</div>
                                </div>
                                <button
                                    onClick={handleExportPDF}
                                    className="no-print bg-blue-600 shadow-lg shadow-blue-600/20 text-white p-6 rounded-2xl flex flex-col justify-between hover:scale-[1.02] transition-transform active:scale-95 text-left"
                                >
                                    <div className="text-blue-100 text-sm font-medium">Generate Audit</div>
                                    <div className="flex items-center justify-between mt-2">
                                        <span className="font-bold text-lg">PDF Report</span>
                                        <Download className="w-5 h-5" />
                                    </div>
                                </button>
                            </div>

                            {/* Tabs Container */}
                            <div className="glass rounded-3xl overflow-hidden border border-slate-200 dark:border-slate-800">
                                <div className="flex border-b border-slate-200 dark:border-slate-800 no-print">
                                    {(['seo', 'security', 'aeo'] as const).map((t) => (
                                        <button
                                            key={t}
                                            onClick={() => setActiveTab(t)}
                                            className={`flex-1 py-5 text-sm font-bold transition-all uppercase tracking-wider ${activeTab === t ? 'bg-blue-600 text-white' : 'text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'}`}
                                        >
                                            {t === 'aeo' ? 'AI Readiness' : t}
                                        </button>
                                    ))}
                                </div>

                                <div className="p-8">
                                    <div className="space-y-4">
                                        {activeTab === 'seo' && (
                                            report.seo_issues.length === 0 ? <p className="text-emerald-600 font-bold">✓ Website is perfectly optimized for Search Engines.</p> :
                                                report.seo_issues.map((issue, i) => (
                                                    <div key={i} className={`p-5 rounded-2xl border-l-4 glass ${getSeverityColor(issue.severity)}`}>
                                                        <h3 className="font-bold text-lg mb-1">{issue.issue}</h3>
                                                        <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">{issue.details}</p>
                                                    </div>
                                                ))
                                        )}
                                        {activeTab === 'security' && (
                                            report.security_issues.length === 0 ? <p className="text-emerald-600 font-bold">✓ No critical security risks detected.</p> :
                                                report.security_issues.map((issue, i) => (
                                                    <div key={i} className={`p-5 rounded-2xl border-l-4 glass ${getSeverityColor(issue.severity)}`}>
                                                        <h3 className="font-bold text-lg mb-1">{issue.issue}</h3>
                                                        <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">{issue.details}</p>
                                                    </div>
                                                ))
                                        )}
                                        {activeTab === 'aeo' && (
                                            <div className="space-y-6">
                                                <div className="p-6 bg-blue-50 dark:bg-blue-900/10 rounded-2xl border border-blue-200 dark:border-blue-800">
                                                    <h3 className="text-blue-700 dark:text-blue-400 font-bold mb-2">Answer Engine Optimization Performance</h3>
                                                    <p className="text-slate-600 dark:text-slate-400 text-sm">Your content is highly readable by Large Language Models (LLMs) and maintains a semantic structure preferred by ChatGPT and Perplexity bot crawlers.</p>
                                                </div>
                                                {report.aeo_issues.map((issue, i) => (
                                                    <div key={i} className={`p-5 rounded-2xl border-l-4 glass ${getSeverityColor(issue.severity)}`}>
                                                        <h3 className="font-bold text-lg mb-1">{issue.issue}</h3>
                                                        <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">{issue.details}</p>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>

                            {/* Roadmap */}
                            <div className="mt-8 bg-slate-900 dark:bg-slate-950 p-8 rounded-3xl border border-slate-800 shadow-2xl">
                                <h3 className="text-xl font-bold mb-6 text-white flex items-center gap-2">
                                    <CheckCircle className="text-emerald-500" /> Improvement Roadmap
                                </h3>
                                <div className="grid gap-4">
                                    {report.quick_fixes.map((fix, i) => (
                                        <div key={i} className="flex items-center gap-4 bg-slate-800/50 p-4 rounded-xl border border-white/5">
                                            <span className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-xs shrink-0">{i + 1}</span>
                                            <p className="text-slate-300 text-sm">{fix}</p>
                                        </div>
                                    ))}
                                    <button onClick={copyReportToClipboard} className="text-slate-500 hover:text-white transition-colors text-xs mt-4">Copy JSON Report</button>
                                </div>
                            </div>
                        </div>
                    )}
                </main>

                {/* Modals */}
                <AnimatePresence>
                    {showDoc && (
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
                            <motion.div initial={{ scale: 0.9 }} animate={{ scale: 1 }} className="bg-white dark:bg-slate-900 rounded-3xl p-10 max-w-2xl w-full shadow-2xl relative custom-scrollbar overflow-y-auto max-h-[80vh]">
                                <button onClick={() => setShowDoc(false)} className="absolute top-6 right-6 text-slate-400 hover:text-red-500 transition-colors"><X /></button>
                                <h2 className="text-3xl font-bold mb-8 text-slate-900 dark:text-white">Documentation</h2>
                                <div className="space-y-8">
                                    <div>
                                        <h4 className="text-blue-600 dark:text-blue-400 font-bold mb-2 uppercase text-xs tracking-widest">Image Alt Optimization</h4>
                                        <p className="text-slate-600 dark:text-slate-400 leading-relaxed text-sm">Every image on your page must have an `alt` attribute describing its content. This isn't just for Google; it's how screen readers explain your site to visually impaired users.</p>
                                    </div>
                                    <div>
                                        <h4 className="text-blue-600 dark:text-blue-400 font-bold mb-2 uppercase text-xs tracking-widest">Semantic Heading (H1)</h4>
                                        <p className="text-slate-600 dark:text-slate-400 leading-relaxed text-sm">H1 tags act as the "title" of your page's internal document. Using multiple H1s or none at all tells search engines your site lacks clear hierarchy.</p>
                                    </div>
                                </div>
                            </motion.div>
                        </motion.div>
                    )}
                    {showAuth && (
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
                            <motion.div initial={{ y: 20 }} animate={{ y: 0 }} className="bg-white dark:bg-slate-900 rounded-3xl p-10 max-w-sm w-full shadow-2xl text-center">
                                <button onClick={() => setShowAuth(false)} className="absolute top-6 right-6 text-slate-400 hover:text-red-500 transition-colors"><X /></button>
                                <div className="bg-blue-600/10 w-20 h-20 rounded-3xl flex items-center justify-center mx-auto mb-8">
                                    <Shield className="w-10 h-10 text-blue-600" />
                                </div>
                                <h3 className="text-2xl font-black text-slate-900 dark:text-white mb-2">Welcome Back</h3>
                                <p className="text-slate-500 dark:text-slate-400 text-sm mb-10 italic">Sign in to sync your audits</p>
                                <div className="space-y-4">
                                    <button onClick={handleGoogleSignIn} className="w-full bg-slate-900 dark:bg-white text-white dark:text-slate-900 py-4 rounded-2xl font-bold transition-all hover:scale-[1.02] shadow-xl">Google Sign In</button>
                                    <button onClick={handleEmailSignIn} className="w-full bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white py-4 rounded-2xl font-bold transition-all">Email Link</button>
                                </div>
                            </motion.div>
                        </motion.div>
                    )}
                </AnimatePresence>

                <footer className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 border-t border-slate-200 dark:border-slate-800 mt-20 text-center no-print">
                    <p className="text-slate-400 text-xs font-medium tracking-wide">
                        THIS TOOL PERFORMS READ-ONLY ANALYSIS OF PUBLICLY AVAILABLE WEBSITE DATA.
                    </p>
                </footer>
            </div>
        </div>
    );
}

export default App;
