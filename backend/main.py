from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.analyze import router as analyze_router
import uvicorn

# Create the FastAPI app instance
app = FastAPI(
    title="AI SEO + Security Analyzer",
    description="A production-grade tool to analyze websites for SEO and Security issues.",
    version="1.0.0"
)

# Add CORS middleware to allow frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple In-Memory Rate Limiter
from collections import defaultdict
import time
from fastapi import Request, Response

rate_limit_store = defaultdict(list)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.method == "POST" and request.url.path == "/analyze":
        client_ip = request.client.host
        now = time.time()
        # Keep only timestamps from the last 3600 seconds (1 hour)
        rate_limit_store[client_ip] = [t for t in rate_limit_store[client_ip] if now - t < 3600]
        
        if len(rate_limit_store[client_ip]) >= 5: # SaaS Tier: 5 scans per hour
            return Response(content='{"detail": "Rate limit exceeded. Trial tier: 5 scans per hour. Please try again later."}', 
                            status_code=429, 
                            media_type="application/json")
        
        rate_limit_store[client_ip].append(now)
        
    response = await call_next(request)
    return response

# Include our /analyze route
app.include_router(analyze_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI SEO + Security Analyzer API. Use /analyze (POST) to start."}

if __name__ == "__main__":
    # This part runs the server when you execute 'python main.py'
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
