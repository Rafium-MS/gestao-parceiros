from fastapi import FastAPI
from .deps import lifespan
from .routers import partners, stores, brands

app = FastAPI(title="Gestão de Parceiros API")

@app.on_event("startup")
async def startup():
    await lifespan.startup()

@app.on_event("shutdown")
async def shutdown():
    await lifespan.shutdown()

app.include_router(partners.router, prefix="/partners", tags=["Partners"])
app.include_router(stores.router, prefix="/stores", tags=["Stores"])
app.include_router(brands.router, prefix="/brands", tags=["Brands"])

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
