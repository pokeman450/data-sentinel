import pandas as pd


def detect_schema_drift(df_old: pd.DataFrame, df_new: pd.DataFrame):
    old_cols = set(df_old.columns)
    new_cols = set(df_new.columns)

    return {
        "added_columns": list(new_cols - old_cols),
        "removed_columns": list(old_cols - new_cols),
        "common_columns": list(old_cols & new_cols)
    }


def detect_type_drift(df_old: pd.DataFrame, df_new: pd.DataFrame):
    drift = {}

    common_cols = set(df_old.columns) & set(df_new.columns)

    for col in common_cols:
        old_type = str(df_old[col].dtype)
        new_type = str(df_new[col].dtype)

        if old_type != new_type:
            drift[col] = {
                "old_type": old_type,
                "new_type": new_type
            }

    return drift


def detect_basic_distribution_drift(df_old: pd.DataFrame, df_new: pd.DataFrame):
    """
    Lightweight drift detection using summary stats.
    (No ML needed yet — perfect for portfolio stage)
    """

    drift = {}

    common_cols = set(df_old.columns) & set(df_new.columns)

    for col in common_cols:
        if pd.api.types.is_numeric_dtype(df_old[col]) and pd.api.types.is_numeric_dtype(df_new[col]):

            old_mean = df_old[col].mean()
            new_mean = df_new[col].mean()

            old_std = df_old[col].std()
            new_std = df_new[col].std()

            drift[col] = {
                "old_mean": float(old_mean) if pd.notna(old_mean) else None,
                "new_mean": float(new_mean) if pd.notna(new_mean) else None,
                "mean_shift": float(new_mean - old_mean) if pd.notna(old_mean) and pd.notna(new_mean) else None,
                "old_std": float(old_std) if pd.notna(old_std) else None,
                "new_std": float(new_std) if pd.notna(new_std) else None,
            }

    return drift


def generate_drift_report(df_old: pd.DataFrame, df_new: pd.DataFrame):
    schema = detect_schema_drift(df_old, df_new)
    type_drift = detect_type_drift(df_old, df_new)
    distribution = detect_basic_distribution_drift(df_old, df_new)

    return {
        "schema_drift": schema,
        "type_drift": type_drift,
        "distribution_drift": distribution,
        "old_rows": len(df_old),
        "new_rows": len(df_new),
        "row_change": len(df_new) - len(df_old)
    }
