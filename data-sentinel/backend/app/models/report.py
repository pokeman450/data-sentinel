from sqlalchemy import Column, Integer, String, Float, JSON
from backend.app.core.db import Base


class DatasetReport(Base):
    __tablename__ = "dataset_reports"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    rows = Column(Integer)
    columns = Column(Integer)
    memory_usage_mb = Column(Float)
    report_json = Column(JSON)