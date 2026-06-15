from pydantic import BaseModel
from typing import Dict, Any, List, Optional


class ColumnIssue(BaseModel):
    status: str
    reason: str
    missing_rate: Optional[float] = None


class DataQualityReport(BaseModel):
    filename: str
    rows: int
    columns: int
    missing_values: Dict[str, int]
    duplicate_rows: int
    column_types: Dict[str, str]
    memory_usage_mb: float

    column_health: Dict[str, ColumnIssue] = {}