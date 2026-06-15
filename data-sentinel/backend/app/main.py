from fastapi import FastAPI
from backend.app.api.routes import router
from backend.app.core.db import Base, engine
from backend.app.models.report import DatasetReport

Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="Data Sentinel",
    description="Data quality and observability platform",
    version="0.1.0"
)

app.include_router(router)


@app.get("/")
def root():
    return {"message": "Data Sentinel is running"}