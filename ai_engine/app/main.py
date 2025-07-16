from fastapi import FastAPI
from app.api.endpoints import query, ingestion

app = FastAPI(title="AI Engine Service")

app.include_router(query.router, prefix="/api/v1", tags=["Querying"])
app.include_router(ingestion.router, prefix="/api/v1", tags=["Ingestion"])

@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "ok", "message": "AI Engine is running"}