from fastapi import FastAPI
from app.api.analyze import router as analyze_router
import uvicorn

# Create the FastAPI app instance
app = FastAPI(
    title="AI SEO + Security Analyzer",
    description="A production-grade tool to analyze websites for SEO and Security issues.",
    version="1.0.0"
)

# Include our /analyze route
app.include_router(analyze_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI SEO + Security Analyzer API. Use /analyze (POST) to start."}

if __name__ == "__main__":
    # This part runs the server when you execute 'python main.py'
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
