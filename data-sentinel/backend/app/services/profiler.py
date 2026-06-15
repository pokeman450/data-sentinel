import pandas as pd

# -----------------------------
# Severity mapping for scoring
# -----------------------------
SEVERITY_SCORE = {
    "good": 100,
    "warning": 60,
    "bad": 0
}


def generate_report(df: pd.DataFrame):
    total_rows = len(df)

    # -----------------------------
    # Basic dataset stats
    # -----------------------------
    missing = df.isnull().sum().to_dict()
    duplicates = int(df.duplicated().sum())
    column_types = {col: str(dtype) for col, dtype in df.dtypes.items()}

    memory_mb = float(df.memory_usage(deep=True).sum() / (1024 * 1024))

    column_health = {}

    # -----------------------------
    # Column-level analysis
    # -----------------------------
    for col in df.columns:
        missing_count = missing[col]
        missing_rate = missing_count / total_rows if total_rows > 0 else 0

        # RULE 1: Schema issue (highest priority)
        if "Unnamed" in col:
            status = "bad"
            reason = "unnamed_column"

        # RULE 2: Fully empty column
        elif missing_rate == 1.0:
            status = "bad"
            reason = "fully_null_column"

        # RULE 3: High missingness
        elif missing_rate > 0.3:
            status = "warning"
            reason = "high_missing_rate"

        # RULE 4: Healthy column
        else:
            status = "good"
            reason = "healthy_column"

        column_health[col] = {
            "status": status,
            "reason": reason,
            "missing_rate": float(missing_rate)
        }

    # -----------------------------
    # Dataset health scoring
    # -----------------------------
    total_score = 0
    count = 0

    for meta in column_health.values():
        total_score += SEVERITY_SCORE[meta["status"]]
        count += 1

    dataset_score = total_score / count if count > 0 else 0

    # -----------------------------
    # Final report
    # -----------------------------
    return {
        "rows": int(total_rows),
        "columns": int(len(df.columns)),
        "missing_values": missing,
        "duplicate_rows": int(duplicates),
        "column_types": column_types,
        "memory_usage_mb": round(memory_mb, 2),

        # column intelligence
        "column_health": column_health,

        # dataset-level intelligence
        "dataset_health_score": round(dataset_score, 2)
    }