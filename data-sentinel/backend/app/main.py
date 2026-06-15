from fastapi import FastAPI
from backend.app.api.routes import router

app = FastAPI(
    title="Data Sentinel",
    description="Data quality and observability platform",
    version="0.1.0"
)

app.include_router(router)


@app.get("/")
def root():
    return {"message": "Data Sentinel is running"}