# utils/serialize.py
from datetime import datetime, date
from decimal import Decimal
from typing import Any

import numpy as np
import pandas as pd

__all__ = ["to_native", "as_json_ready"]

def to_native(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {to_native(k): to_native(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [to_native(x) for x in obj]
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    if obj is pd.NaT:
        return None
    if isinstance(obj, pd.Series):
        return to_native(obj.to_dict())
    if isinstance(obj, pd.DataFrame):
        return [to_native(r) for r in obj.to_dict(orient="records")]
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    return obj

def as_json_ready(fn):
    def wrapper(*args, **kwargs):
        return to_native(fn(*args, **kwargs))
    return wrapper
