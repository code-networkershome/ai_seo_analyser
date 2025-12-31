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
    impact?: string;
    fix?: string;
}

interface ReportData {
    seo_issues: Issue[];
    security_issues: Issue[];
    aeo_issues: Issue[];
    quick_fixes: string[];
    seo_score: number;
    security_score: number;
    aeo_score: number;
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
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [authMode, setAuthMode] = useState<'signin' | 'signup'>('signin');
    const [authLoading, setAuthLoading] = useState(false);
    const [toast, setToast] = useState<{ message: string, type: 'success' | 'error' | 'info' } | null>(null);

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

            // Get auth token if user is logged in
            const { data: { session } } = await supabase.auth.getSession();
            const headers: Record<string, string> = { 'Content-Type': 'application/json' };
            if (session?.access_token) {
                headers['Authorization'] = `Bearer ${session.access_token}`;
            }

            const response = await fetch(`${apiUrl}/analyze`, {
                method: 'POST',
                headers,
                body: JSON.stringify({ url }),
            });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Server Error (${response.status})`);
            }
            const data = await response.json();
            console.log("Audit Report Received:", data);
            console.log("SCORES >>>", {
                seo_score: data.seo_score,
                security_score: data.security_score,
                aeo_score: data.aeo_score
            });
            setReport(data);
            setToast({ message: "Analysis complete!", type: 'success' });
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setLoading(false);
        }
    };

    const handleAuth = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!supabase) return;
        if (!email || !password) {
            alert("Please enter both email and password.");
            return;
        }

        setAuthLoading(true);
        try {
            if (authMode === 'signup') {
                const { error } = await supabase.auth.signUp({
                    email,
                    password,
                    options: {
                        emailRedirectTo: window.location.origin
                    }
                });
                if (error) throw error;
                setToast({ message: "Success! Account created. Sign in to continue.", type: 'success' });
                setAuthMode('signin');
            } else {
                const { error } = await supabase.auth.signInWithPassword({ email, password });
                if (error) throw error;
                setShowAuth(false);
                setToast({ message: "Welcome back!", type: 'success' });
            }
        } catch (err: any) {
            setToast({ message: "Auth Error: " + err.message, type: 'error' });
        } finally {
            setAuthLoading(false);
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
                <nav className={`border-b ${isDark ? 'border-slate-800 bg-slate-900/50' : 'border-slate-200 bg-white/90'} backdrop-blur-xl sticky top-0 z-50 no-print transition-colors`}>
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
                            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8 no-print">
                                <div className="glass p-6 rounded-2xl text-center">
                                    <div className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase mb-1">SEO Score</div>
                                    <div className={`text-3xl font-black ${(Number(report.seo_score) || 0) > 80 ? 'text-emerald-500' : (Number(report.seo_score) || 0) > 50 ? 'text-orange-500' : 'text-red-500'}`}>
                                        {Math.round(Number(report.seo_score) || 0)}
                                    </div>
                                </div>
                                <div className="glass p-6 rounded-2xl text-center">
                                    <div className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase mb-1">Security Score</div>
                                    <div className={`text-3xl font-black ${(Number(report.security_score) || 0) > 80 ? 'text-emerald-500' : (Number(report.security_score) || 0) > 50 ? 'text-orange-500' : 'text-red-500'}`}>
                                        {Math.round(Number(report.security_score) || 0)}
                                    </div>
                                </div>
                                <div className="glass p-6 rounded-2xl text-center">
                                    <div className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase mb-1">AEO Score</div>
                                    <div className="text-3xl font-black text-blue-600 dark:text-blue-400">
                                        {Math.round(Number(report.aeo_score) || 0)}
                                    </div>
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

                            {/* Interactive Tabs (Screen Only) */}
                            <div className="glass rounded-3xl overflow-hidden border border-slate-200 dark:border-slate-800 no-print">
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
                                                    <div key={i} className={`p-6 rounded-2xl border-l-4 glass ${getSeverityColor(issue.severity)}`}>
                                                        <div className="flex justify-between items-start mb-2">
                                                            <h3 className="font-bold text-lg">{issue.issue}</h3>
                                                            <span className="text-[10px] font-black uppercase tracking-widest px-2 py-1 rounded bg-black/5 dark:bg-white/5">{issue.severity}</span>
                                                        </div>
                                                        <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed mb-4">{issue.details}</p>

                                                        <div className="mt-4 pt-4 border-t border-black/5 dark:border-white/5 text-xs">
                                                            <p className="font-bold text-slate-900 dark:text-white mb-1 uppercase tracking-tighter opacity-50">Business Impact</p>
                                                            <p className="text-slate-600 dark:text-slate-400">{issue.impact || "This issue may impact how search engines understand your site's content and hierarchy."}</p>
                                                        </div>
                                                        <div className="mt-3 text-xs">
                                                            <p className="font-bold text-emerald-600 dark:text-emerald-400 mb-1 uppercase tracking-tighter">Recommended Fix</p>
                                                            <code className="block bg-black/5 dark:bg-white/5 p-2 rounded text-slate-800 dark:text-slate-200">{issue.fix || "Refer to the details above to resolve this technical SEO conflict."}</code>
                                                        </div>
                                                    </div>
                                                ))
                                        )}
                                        {activeTab === 'security' && (
                                            report.security_issues.length === 0 ? <p className="text-emerald-600 font-bold">✓ No critical security risks detected.</p> :
                                                report.security_issues.map((issue, i) => (
                                                    <div key={i} className={`p-6 rounded-2xl border-l-4 glass ${getSeverityColor(issue.severity)}`}>
                                                        <div className="flex justify-between items-start mb-2">
                                                            <h3 className="font-bold text-lg">{issue.issue}</h3>
                                                            <span className="text-[10px] font-black uppercase tracking-widest px-2 py-1 rounded bg-black/5 dark:bg-white/5">{issue.severity}</span>
                                                        </div>
                                                        <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed mb-4">{issue.details}</p>

                                                        <div className="mt-4 pt-4 border-t border-black/5 dark:border-white/5 text-xs">
                                                            <p className="font-bold text-slate-900 dark:text-white mb-1 uppercase tracking-tighter opacity-50">Security Impact</p>
                                                            <p className="text-slate-600 dark:text-slate-400">{issue.impact || "Exposed system signatures or insecure headers can be exploited by malicious actors."}</p>
                                                        </div>
                                                        <div className="mt-3 text-xs">
                                                            <p className="font-bold text-red-600 dark:text-red-400 mb-1 uppercase tracking-tighter">Required Fix</p>
                                                            <code className="block bg-black/5 dark:bg-white/5 p-2 rounded text-slate-800 dark:text-slate-200">{issue.fix || "Follow security best practices to hide configuration details or enforce HTTPS."}</code>
                                                        </div>
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
                                                    <div key={i} className={`p-6 rounded-2xl border-l-4 glass ${getSeverityColor(issue.severity)}`}>
                                                        <div className="flex justify-between items-start mb-2">
                                                            <h3 className="font-bold text-lg">{issue.issue}</h3>
                                                            <span className="text-[10px] font-black uppercase tracking-widest px-2 py-1 rounded bg-black/5 dark:bg-white/5">{issue.severity}</span>
                                                        </div>
                                                        <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed mb-4">{issue.details}</p>

                                                        <div className="mt-4 pt-4 border-t border-black/5 dark:border-white/5 text-xs">
                                                            <p className="font-bold text-slate-900 dark:text-white mb-1 uppercase tracking-tighter opacity-50">AI Visibility Impact</p>
                                                            <p className="text-slate-600 dark:text-slate-400">{issue.impact || "Non-standard structure can prevent AI models from accurately synthesizing your content."}</p>
                                                        </div>
                                                        <div className="mt-3 text-xs">
                                                            <p className="font-bold text-blue-600 dark:text-blue-400 mb-1 uppercase tracking-tighter">AEO Fix</p>
                                                            <code className="block bg-black/5 dark:bg-white/5 p-2 rounded text-slate-800 dark:text-slate-200">{issue.fix || "Use semantic HTML and FAQ schema to improve AI crawlability."}</code>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>

                            {/* Improvement Roadmap (Screen only - will be duplicated for print) */}
                            <div className="mt-8 bg-white dark:bg-slate-950 p-8 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-xl no-print">
                                <h3 className="text-xl font-bold mb-6 text-slate-900 dark:text-white flex items-center gap-2">
                                    <CheckCircle className="text-emerald-500" /> Improvement Roadmap
                                </h3>
                                <div className="grid gap-4">
                                    {report.quick_fixes.map((fix, i) => (
                                        <div key={i} className="flex items-center gap-4 bg-slate-100 dark:bg-slate-800/50 p-4 rounded-xl border border-slate-200 dark:border-white/5">
                                            <span className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-xs shrink-0">{i + 1}</span>
                                            <p className="text-slate-700 dark:text-slate-300 text-sm">{fix}</p>
                                        </div>
                                    ))}
                                    <button onClick={copyReportToClipboard} className="text-slate-500 hover:text-slate-900 dark:hover:text-white transition-colors text-xs mt-4">Copy JSON Report</button>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* 📄 ELABORATE PRINT-ONLY REPORT 📄 */}
                    {report && (
                        <div className="hidden print:block print:text-black mt-0">
                            <div className="text-center mb-10 border-b-2 border-slate-900 pb-8">
                                <h1 className="text-4xl font-black uppercase mb-2">SEO & AI Readiness Audit</h1>
                                <p className="text-slate-600 font-bold uppercase tracking-widest text-sm">{url}</p>
                                <p className="text-slate-400 text-xs mt-2 italic">Report Generated on {new Date().toLocaleDateString()}</p>
                            </div>

                            <div className="grid grid-cols-4 gap-4 mb-10">
                                <div className="border-2 border-slate-900 p-4 rounded-xl text-center">
                                    <p className="text-xs font-bold uppercase mb-1">SEO Score</p>
                                    <p className="text-2xl font-black">{Math.round(Number(report.seo_score) || 0)}</p>
                                </div>
                                <div className="border-2 border-slate-900 p-4 rounded-xl text-center">
                                    <p className="text-xs font-bold uppercase mb-1">Security Score</p>
                                    <p className="text-2xl font-black">{Math.round(Number(report.security_score) || 0)}</p>
                                </div>
                                <div className="border-2 border-slate-900 p-4 rounded-xl text-center">
                                    <p className="text-xs font-bold uppercase mb-1">AEO Score</p>
                                    <p className="text-2xl font-black">{Math.round(Number(report.aeo_score) || 0)}</p>
                                </div>
                            </div>

                            <section className="mb-10">
                                <h2 className="text-2xl font-black uppercase mb-6 bg-slate-900 text-white px-4 py-2 rounded">1. Search Engine Optimization</h2>
                                {report.seo_issues.length === 0 ? <p className="font-bold">✓ No SEO issues detected.</p> :
                                    <div className="space-y-6">
                                        {report.seo_issues.map((issue, i) => (
                                            <div key={i} className="border-b border-slate-200 pb-6">
                                                <h3 className="font-black text-lg mb-1">{issue.issue} <span className="text-xs font-medium px-2 py-0.5 border rounded uppercase ml-2 text-slate-500">{issue.severity}</span></h3>
                                                <p className="text-slate-700 leading-relaxed text-sm mb-2">{issue.details}</p>
                                                <p className="text-xs text-slate-500 mb-2"><strong className="text-black uppercase text-[10px]">Impact:</strong> {issue.impact || "This issue may affect your search engine visibility and rankings."}</p>
                                                <p className="text-[11px] bg-slate-100 p-2 rounded border border-slate-200 font-mono"><strong className="text-black uppercase text-[9px] block mb-1">Recommended Fix:</strong> {issue.fix || "Review the issue details above and implement the suggested changes."}</p>
                                            </div>
                                        ))}
                                    </div>
                                }
                            </section>

                            <section className="mb-10 page-break-before">
                                <h2 className="text-2xl font-black uppercase mb-6 bg-slate-900 text-white px-4 py-2 rounded">2. Security Analysis</h2>
                                {report.security_issues.length === 0 ? <p className="font-bold">✓ No security risks detected.</p> :
                                    <div className="space-y-6">
                                        {report.security_issues.map((issue, i) => (
                                            <div key={i} className="border-b border-slate-200 pb-6">
                                                <h3 className="font-black text-lg mb-1">{issue.issue} <span className="text-xs font-medium px-2 py-0.5 border rounded uppercase ml-2 text-slate-500">{issue.severity}</span></h3>
                                                <p className="text-slate-700 leading-relaxed text-sm mb-2">{issue.details}</p>
                                                <p className="text-xs text-slate-500 mb-2"><strong className="text-black uppercase text-[10px]">Security Risk:</strong> {issue.impact || "This vulnerability may expose your site to potential attacks."}</p>
                                                <p className="text-[11px] bg-slate-100 p-2 rounded border border-slate-200 font-mono"><strong className="text-black uppercase text-[9px] block mb-1">Solution:</strong> {issue.fix || "Follow security best practices to mitigate this risk."}</p>
                                            </div>
                                        ))}
                                    </div>
                                }
                            </section>

                            <section className="mb-10">
                                <h2 className="text-2xl font-black uppercase mb-6 bg-slate-900 text-white px-4 py-2 rounded">3. AI Readiness (AEO)</h2>
                                <div className="mb-6 p-4 border-2 border-blue-600 rounded-xl">
                                    <p className="text-slate-700 text-sm font-bold">Audit reveals that the content structure is compatible with LLM agents (ChatGPT, Gemini, Perplexity).</p>
                                </div>
                                <div className="space-y-6">
                                    {report.aeo_issues.map((issue, i) => (
                                        <div key={i} className="border-b border-slate-200 pb-6">
                                            <h3 className="font-black text-lg mb-1">{issue.issue} <span className="text-xs font-medium px-2 py-0.5 border rounded uppercase ml-2 text-slate-500">{issue.severity}</span></h3>
                                            <p className="text-slate-700 leading-relaxed text-sm mb-2">{issue.details}</p>
                                            <p className="text-xs text-slate-500 mb-2"><strong className="text-black uppercase text-[10px]">AI Model Impact:</strong> {issue.impact || "This may reduce your visibility in AI-powered search results."}</p>
                                            <p className="text-[11px] bg-slate-100 p-2 rounded border border-slate-200 font-mono"><strong className="text-black uppercase text-[9px] block mb-1">Optimization:</strong> {issue.fix || "Use semantic HTML and structured data to improve AI crawlability."}</p>
                                        </div>
                                    ))}
                                </div>
                            </section>

                            <section className="mb-10">
                                <h2 className="text-2xl font-black uppercase mb-6 bg-emerald-600 text-white px-4 py-2 rounded">Improvement Roadmap</h2>
                                <div className="grid gap-3">
                                    {report.quick_fixes.map((fix, i) => (
                                        <div key={i} className="flex gap-4 p-4 border border-slate-200 rounded-xl items-start">
                                            <span className="font-black text-emerald-600 text-xl font-mono">0{i + 1}</span>
                                            <p className="text-sm font-medium leading-relaxed">{fix}</p>
                                        </div>
                                    ))}
                                </div>
                            </section>

                            <div className="mt-20 pt-10 border-t border-slate-900 text-center">
                                <p className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">AI SEO Analyzer © 2025 • Confidential Performance Audit</p>
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
                            <motion.div initial={{ y: 20 }} animate={{ y: 0 }} className="bg-white dark:bg-slate-900 rounded-3xl p-10 max-w-sm w-full shadow-2xl relative">
                                <button onClick={() => setShowAuth(false)} className="absolute top-6 right-6 text-slate-400 hover:text-red-500 transition-colors"><X /></button>
                                <div className="bg-blue-600/10 w-20 h-20 rounded-3xl flex items-center justify-center mx-auto mb-8">
                                    <Shield className="w-10 h-10 text-blue-600" />
                                </div>
                                <h3 className="text-2xl font-black text-slate-900 dark:text-white mb-2">
                                    {authMode === 'signin' ? 'Welcome Back' : 'Create Account'}
                                </h3>
                                <p className="text-slate-500 dark:text-slate-400 text-sm mb-10 italic">
                                    {authMode === 'signin' ? 'Sign in to sync your audits' : 'Start tracking your SEO progress'}
                                </p>
                                <form onSubmit={handleAuth} className="space-y-4">
                                    <div className="text-left">
                                        <label className="text-xs font-bold uppercase text-slate-500 mb-1 block ml-1">Email Address</label>
                                        <input
                                            type="email"
                                            value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                            placeholder="you@example.com"
                                            className="w-full bg-slate-100 dark:bg-slate-800 border-none rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                                            required
                                        />
                                    </div>
                                    <div className="text-left">
                                        <label className="text-xs font-bold uppercase text-slate-500 mb-1 block ml-1">Password</label>
                                        <input
                                            type="password"
                                            value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                            placeholder="••••••••"
                                            className="w-full bg-slate-100 dark:bg-slate-800 border-none rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                                            required
                                        />
                                    </div>
                                    <button
                                        type="submit"
                                        disabled={authLoading}
                                        className="w-full bg-blue-600 hover:bg-blue-500 text-white py-4 rounded-2xl font-bold transition-all hover:scale-[1.02] shadow-xl disabled:opacity-50"
                                    >
                                        {authLoading ? 'Processing...' : (authMode === 'signin' ? 'Sign In' : 'Sign Up')}
                                    </button>
                                </form>
                                <div className="mt-8 pt-6 border-t border-slate-200 dark:border-slate-800">
                                    <p className="text-slate-500 dark:text-slate-400 text-sm">
                                        {authMode === 'signin' ? "Don't have an account?" : "Already have an account?"}{' '}
                                        <button
                                            onClick={() => setAuthMode(authMode === 'signin' ? 'signup' : 'signin')}
                                            className="text-blue-600 dark:text-blue-400 font-bold hover:underline"
                                        >
                                            {authMode === 'signin' ? 'Sign Up' : 'Sign In'}
                                        </button>
                                    </p>
                                </div>
                            </motion.div>
                        </motion.div>
                    )}
                    {toast && (
                        <motion.div
                            initial={{ opacity: 0, y: 50 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: 50 }}
                            onAnimationComplete={() => setTimeout(() => setToast(null), 3000)}
                            className={`fixed bottom-8 left-1/2 -translate-x-1/2 z-[200] px-6 py-3 rounded-2xl shadow-2xl font-bold text-sm ${toast.type === 'error' ? 'bg-red-600 text-white' :
                                toast.type === 'success' ? 'bg-emerald-600 text-white' :
                                    'bg-blue-600 text-white'
                                }`}
                        >
                            {toast.message}
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
