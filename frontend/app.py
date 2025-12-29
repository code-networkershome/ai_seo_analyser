import streamlit as st
import httpx
import json

# Set page configuration for a premium look
st.set_page_config(
    page_title="AI SEO + Security Analyzer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main {
        background-color: #0f172a;
        color: #f8fafc;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #3b82f6;
        color: white;
        font-weight: bold;
    }
    .status-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #1e293b;
        margin-bottom: 15px;
        border: 1px solid #334155;
    }
    .issue-high { border-left: 5px solid #ef4444; }
    .issue-medium { border-left: 5px solid #f59e0b; }
    .issue-low { border-left: 5px solid #10b981; }
</style>
""", unsafe_allow_html=True)

# App Title & Header
st.title("🛡️ AI-based SEO + Security Analyzer")
st.markdown("Enter your company's URL below to get a deep dive into SEO performance and security trust signals.")

# Sidebar for configuration or info
with st.sidebar:
    st.header("About this Tool")
    st.info("""
    This tool uses **Firecrawl** to scrape your site, **Groq + Llama 3** to explain issues, and **FastAPI** as the engine.
    
    It's designed for non-technical website owners to understand their digital presence.
    """)
    st.divider()
    st.write("Built with ❤️ for beginners.")

# URL Input Section
url = st.text_input("Enter Company Website URL:", placeholder="https://example.com")

if st.button("🚀 Run Analysis"):
    if not url:
        st.error("Please enter a valid URL first!")
    else:
        with st.status("🔍 Analyzing website structure...", expanded=True) as status:
            try:
                # We call our FastAPI backend
                # Make sure the backend is running on http://localhost:8000
                backend_url = "http://localhost:8000/analyze"
                
                status.write("🕸️ Crawling pages with Firecrawl...")
                response = httpx.post(backend_url, json={"url": url}, timeout=180.0)
                
                if response.status_code == 200:
                    data = response.json()
                    status.update(label="✅ Analysis complete!", state="complete", expanded=False)
                    
                    # Display Results in Tabs
                    tab1, tab2, tab3, tab4 = st.tabs(["📊 SEO Insights", "🛡️ Security & Trust", "🤖 AEO Optimization", "🛠️ Quick Fixes"])
                    
                    with tab1:
                        st.header("Search Engine Optimization")
                        if not data.get("seo_issues"):
                            st.success("Perfect! No major SEO issues found.")
                        else:
                            for issue in data["seo_issues"]:
                                severity = issue["severity"]
                                st.markdown(f"""
                                <div class="status-card issue-{severity.lower()}">
                                    <h3>{issue['issue']} ({severity})</h3>
                                    <p>{issue['details']}</p>
                                </div>
                                """, unsafe_allow_html=True)

                    with tab2:
                        st.header("Security & Trust Signals")
                        if not data.get("security_issues"):
                            st.success("Excellent! Your site follows basic safety standards.")
                        else:
                            for issue in data["security_issues"]:
                                severity = issue["severity"]
                                st.markdown(f"""
                                <div class="status-card issue-{severity.lower()}">
                                    <h3>{issue['issue']} ({severity})</h3>
                                    <p>{issue['details']}</p>
                                </div>
                                """, unsafe_allow_html=True)

                    with tab3:
                        st.header("Answer Engine Optimization (AEO)")
                        st.markdown("Optimization for AI Search Engines like ChatGPT, Perplexity, and Gemini.")
                        if not data.get("aeo_issues"):
                            st.success("Perfect! Your content is optimized for AI answers.")
                        else:
                            for issue in data["aeo_issues"]:
                                severity = issue["severity"]
                                st.markdown(f"""
                                <div class="status-card issue-{severity.lower()}">
                                    <h3>{issue['issue']} ({severity})</h3>
                                    <p>{issue['details']}</p>
                                </div>
                                """, unsafe_allow_html=True)

                    with tab4:
                        st.header("Recommended Roadmap")
                        if data.get("quick_fixes"):
                            for fix in data["quick_fixes"]:
                                st.info(fix)
                        else:
                            st.write("No fixes needed at this time.")
                
                else:
                    st.error(f"Error from Backend: {response.text}")
                    status.update(label="❌ Failed", state="error")
            
            except Exception as e:
                st.error(f"Connection Error: {e}")
                st.info("Is your FastAPI backend running? Run 'python main.py' in the backend folder.")
                status.update(label="❌ Connection Failed", state="error")

st.divider()
st.caption("Disclaimer: This tool provides surface-level analysis and does not replace deep technical audits.")
