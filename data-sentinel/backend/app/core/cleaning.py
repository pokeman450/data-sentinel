import numpy as np

def normalize_for_db(report: dict):
    def clean(obj):
        if isinstance(obj, dict):
            return {k: clean(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [clean(v) for v in obj]
        if isinstance(obj, (np.integer, np.floating)):
            return obj.item()
        return obj

    return clean(report)