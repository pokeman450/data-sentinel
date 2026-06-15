from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
import io

from backend.app.services.health import health_check
from backend.app.services.profiler import generate_report
from backend.app.core.db import SessionLocal
from backend.app.models.report import DatasetReport

router = APIRouter()


@router.get("/health")
def health():
    return health_check()


@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files allowed")

    contents = await file.read()

    try:
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV: {str(e)}")

    # 1. Generate profiling report
    report = generate_report(df)

    # 2. Save to database
    db = SessionLocal()

    record = DatasetReport(
        filename=file.filename,
        rows=report["rows"],
        columns=report["columns"],
        memory_usage_mb=report["memory_usage_mb"],
        report_json=report
    )

    db.add(record)
    db.commit()
    db.refresh(record)
    db.close()

    # 3. Return response
    return {
        "id": record.id,
        "filename": file.filename,
        "report": report
    }

@router.get("/reports")
def get_reports():
    db = SessionLocal()
    records = db.query(DatasetReport).all()
    db.close()

    return records