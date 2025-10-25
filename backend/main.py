from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import health, search

app = FastAPI(title="Embedding Search API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(search.router, tags=["search"])

@app.get("/")
async def root():
    return {"message": "Embedding Search API", "docs": "/docs"}

@app.on_event("shutdown")
async def shutdown():
    await search.shutdown()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
