import pandas as pd
import numpy as np


def generate_report(df: pd.DataFrame):
    total_rows = len(df)

    missing = df.isnull().sum().to_dict()
    duplicates = int(df.duplicated().sum())
    column_types = {col: str(dtype) for col, dtype in df.dtypes.items()}
    memory_mb = float(df.memory_usage(deep=True).sum() / (1024 * 1024))

    column_health = {}

    for col in df.columns:
        missing_count = missing[col]
        missing_rate = missing_count / total_rows if total_rows > 0 else 0

        if "Unnamed" in col:
            column_health[col] = {
                "status": "bad",
                "reason": "unnamed_column",
                "missing_rate": float(missing_rate)
            }

        elif missing_rate == 1.0:
            column_health[col] = {
                "status": "bad",
                "reason": "fully_null_column",
                "missing_rate": float(missing_rate)
            }

        elif missing_rate > 0.3:
            column_health[col] = {
                "status": "warning",
                "reason": "high_missing_rate",
                "missing_rate": float(missing_rate)
            }

        else:
            column_health[col] = {
                "status": "good",
                "reason": "healthy_column",
                "missing_rate": float(missing_rate)
            }

    return {
        "rows": int(total_rows),
        "columns": int(len(df.columns)),
        "missing_values": missing,
        "duplicate_rows": int(duplicates),
        "column_types": column_types,
        "memory_usage_mb": float(round(memory_mb, 2)),
        "column_health": column_health
    }