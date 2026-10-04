"""Small helpers shared by analysis, agents and UI (no Streamlit imports here)."""
from __future__ import annotations

import json
from typing import Any, Optional

import numpy as np


def to_native(obj: Any) -> Any:
    """Recursively convert numpy / pandas scalars so results are JSON-serialisable."""
    if isinstance(obj, dict):
        return {str(k): to_native(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_native(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return [to_native(v) for v in obj.tolist()]
    if isinstance(obj, (np.floating, float)):
        f = float(obj)
        return f if np.isfinite(f) else None
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    return obj


def to_json(obj: Any, indent: int = 2) -> str:
    return json.dumps(to_native(obj), indent=indent, default=str)


def fmt(v: Optional[float], digits: int = 4) -> str:
    if v is None:
        return "n/a"
    try:
        if not np.isfinite(v):
            return "n/a"
    except TypeError:
        return str(v)
    if v != 0 and abs(v) < 10 ** (-digits):
        return f"{v:.2e}"
    return f"{v:.{digits}g}"
