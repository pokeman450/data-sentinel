from sqlalchemy import Column, Integer, String, Float, JSON, Text
from backend.app.core.db import Base


class DatasetReport(Base):
    __tablename__ = "dataset_reports"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String, index=True)

    rows = Column(Integer)
    columns = Column(Integer)
    memory_usage_mb = Column(Float)

    report_json = Column(JSON)

    ai_insight = Column(Text, nullable=True)

    # NEW: AI job tracking fields
    ai_status = Column(String, default="pending")  # pending | processing | done | failed
    ai_error = Column(Text, nullable=True)