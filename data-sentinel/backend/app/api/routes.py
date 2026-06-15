from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
import pandas as pd
import io

from backend.app.services.health import health_check
from backend.app.services.profiler import generate_report
from backend.app.services.ai_insights import generate_ai_insight

from backend.app.core.db import SessionLocal
from backend.app.models.report import DatasetReport

from backend.app.core.cleaning import normalize_for_db
from backend.app.schemas.report import DatasetReportDTO

router = APIRouter()


# ----------------------------
# DB dependency
# ----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------------------
# Background AI worker (FIXED)
# ----------------------------
def run_ai_and_update(report: dict, filename: str, record_id: int):
    db = SessionLocal()

    try:
        record = db.query(DatasetReport).filter(DatasetReport.id == record_id).first()

        if not record:
            return

        record.ai_status = "processing"
        db.commit()

        try:
            ai_insight = generate_ai_insight(report, filename)

            record.ai_insight = ai_insight
            record.ai_status = "done"
            record.ai_error = None

        except Exception as e:
            record.ai_status = "failed"
            record.ai_error = str(e)

        db.commit()

    except Exception as e:
        # last fallback safety
        try:
            record = db.query(DatasetReport).filter(DatasetReport.id == record_id).first()
            if record:
                record.ai_status = "failed"
                record.ai_error = str(e)
                db.commit()
        except:
            pass

    finally:
        db.close()


# ----------------------------
# Health check
# ----------------------------
@router.get("/health")
def health():
    return health_check()


# ----------------------------
# Upload CSV + generate report
# ----------------------------
@router.post("/upload-csv")
async def upload_csv(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db=Depends(get_db)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files allowed")

    contents = await file.read()

    try:
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV: {str(e)}")

    # ----------------------------
    # 1. Generate report
    # ----------------------------
    report = generate_report(df)

    # ----------------------------
    # 2. Normalize for DB safety
    # ----------------------------
    report = normalize_for_db(report)

    # ----------------------------
    # 3. Validate schema
    # ----------------------------
    try:
        dto = DatasetReportDTO(**report)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Report validation failed: {str(e)}"
        )

    # ----------------------------
    # 4. Save to DB
    # ----------------------------
    record = DatasetReport(
        filename=file.filename,
        rows=dto.rows,
        columns=dto.columns,
        memory_usage_mb=dto.memory_usage_mb,
        report_json=report,
        ai_insight=None,
        ai_status="pending"
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    # ----------------------------
    # 5. Background AI
    # ----------------------------
    if background_tasks is not None:
        background_tasks.add_task(
            run_ai_and_update,
            report,
            file.filename,
            record.id
        )

    # ----------------------------
    # 6. Response
    # ----------------------------
    return {
        "id": record.id,
        "filename": file.filename,
        "report": report,
        "ai_status": record.ai_status,
        "ai_insight": None
    }


# ----------------------------
# Get all reports
# ----------------------------
@router.get("/reports")
def get_reports(db=Depends(get_db)):
    return db.query(DatasetReport).order_by(DatasetReport.id.desc()).all()


# ----------------------------
# Get single report
# ----------------------------
@router.get("/reports/{report_id}")
def get_report(report_id: int, db=Depends(get_db)):
    record = db.query(DatasetReport).filter(DatasetReport.id == report_id).first()

    if not record:
        raise HTTPException(status_code=404, detail="Report not found")

    return record


# ----------------------------
# AI status endpoint
# ----------------------------
@router.get("/reports/{report_id}/status")
def get_ai_status(report_id: int, db=Depends(get_db)):
    record = db.query(DatasetReport).filter(DatasetReport.id == report_id).first()

    if not record:
        raise HTTPException(status_code=404, detail="Report not found")

    return {
        "id": record.id,
        "ai_status": record.ai_status,
        "ai_error": record.ai_error,
        "ai_insight": record.ai_insight
    }