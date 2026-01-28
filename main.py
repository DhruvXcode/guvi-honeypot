
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import honeypot

app = FastAPI(
    title="Agentic Honey-Pot API",
    description="AI-powered scam detection and intelligence extraction API",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routes - endpoint at /honeypot (no prefix)
app.include_router(honeypot.router, tags=["Honeypot"])

@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring."""
    return {"status": "healthy", "service": "agentic-honeypot"}

@app.get("/")
async def root():
    return {
        "message": "Agentic Honey-Pot API is running",
        "docs": "/docs",
        "version": "1.0.0"
    }
