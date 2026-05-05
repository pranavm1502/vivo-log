from fastapi import FastAPI

from app.routers import analytics, colony, export, seed, studies

app = FastAPI(
    title="Vivo-Log API",
    description="Preclinical In-Vivo Study and Mouse Colony Tracking",
    version="0.1.0",
)

app.include_router(colony.router, prefix="/api/v1/colony", tags=["Colony"])
app.include_router(studies.router, prefix="/api/v1/studies", tags=["Studies"])
app.include_router(export.router, prefix="/api/v1/export", tags=["Export"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(seed.router, prefix="/api/v1/seed", tags=["Seed"])


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
