from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routes import api_router

app = FastAPI(title="Dad's BP Tracker API")



# Setup CORS for the Vite Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:5173", "http://127.0.0.1:5173", "https://bloodtestapp-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Backend for Dad's BP Tracker is running"}

app.include_router(api_router, prefix="/api")

# app/main.py

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": "2026-03-03T23:30:00Z", # 這裡可隨便寫
        "version": "1.0.0"
    }

