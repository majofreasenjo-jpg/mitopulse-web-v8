from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.verify import router as verify_router

app = FastAPI(
    title="MitoPulse Verify API",
    description="Human Presence Verification Infrastructure (B2B SaaS)",
    version="1.0.0"
)

# CORS Configuration for SaaS API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, this would be restricted to registered Tenants
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(verify_router, prefix="/v1", tags=["Verification"])

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "MitoPulse Verify Gateway"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
