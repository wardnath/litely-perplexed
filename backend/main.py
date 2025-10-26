from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from routes import health, search

app = FastAPI(title="Litely Perplexed API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(health.router, tags=["health"])
app.include_router(search.router, tags=["search"])

# Mount static frontend files (if they exist)
static_dir = Path("/app/public")
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
else:
    @app.get("/")
    async def root():
        return {"message": "Litely Perplexed API", "docs": "/docs"}

@app.on_event("shutdown")
async def shutdown():
    await search.shutdown()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
