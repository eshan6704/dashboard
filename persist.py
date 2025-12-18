import os
import json
import pickle
import pandas as pd
from datetime import datetime, timedelta
from typing import Any

# ==============================
# Configuration
# ==============================
BASE_DIR = "./data/store"
os.makedirs(BASE_DIR, exist_ok=True)

# TTL validity map (centralized)
VALIDITY_MAP = {
    "result": {"days": 7},
    "qresult": {"days": 7},
    "bhav": {"days": 1},
    "intraday": {"minutes": 15},
    "eq": {"hours": 1},
    "daily": {"days": 1},
}

# ==============================
# Helper functions
# ==============================
def _ts():
    return datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

def _path(filename: str):
    return os.path.join(BASE_DIR, filename)

def _list_files():
    return os.listdir(BASE_DIR)

def _latest(prefix: str, ext: str):
    """Return latest file with prefix + ext"""
    files = [
        f for f in _list_files()
        if f.startswith(prefix + "_") and f.endswith("." + ext)
    ]
    return max(files) if files else None

# ==============================
# Save function
# ==============================
def save(name: str, data: Any, ftype: str) -> bool:
    ts = _ts()
    filename = f"{name}_{ts}.{ftype}"
    path = _path(filename)
    try:
        if ftype == "csv":
            if not isinstance(data, pd.DataFrame):
                raise TypeError("CSV requires pandas DataFrame")
            data.to_csv(path, index=False)
        elif ftype == "json":
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        elif ftype == "html":
            with open(path, "w", encoding="utf-8") as f:
                f.write(str(data))
        elif ftype == "pkl":
            with open(path, "wb") as f:
                pickle.dump(data, f)
        else:
            raise ValueError(f"Unsupported file type: {ftype}")
        return True
    except Exception:
        return False

# ==============================
# Load function
# ==============================
def load(name: str, ftype: str):
    """
    Load file by:
      1) full filename (name_YYYY_MM_DD_HH_MM_SS.ext)
      2) base name + ftype (latest)
    Returns False if file not present
    """
    filename = _latest(name, ftype) if "." not in name else name
    path = _path(filename)
    if not os.path.exists(path):
        return False
    try:
        if filename.endswith(".csv"):
            return pd.read_csv(path)
        if filename.endswith(".json"):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        if filename.endswith(".html"):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        if filename.endswith(".pkl"):
            with open(path, "rb") as f:
                return pickle.load(f)
        return False
    except Exception:
        return False

# ==============================
# Exists with TTL
# ==============================
def exists(name: str, ftype: str) -> bool:
    """
    Check if file exists and is within TTL defined in VALIDITY_MAP
    Returns True/False
    """
    filename = _latest(name, ftype)
    if not filename:
        return False

    path = _path(filename)
    if not os.path.exists(path):
        return False

    mtime = datetime.fromtimestamp(os.path.getmtime(path))
    func_name = name.split("_")[0]
    validity = VALIDITY_MAP.get(func_name)
    if not validity:
        return True  # no TTL → always valid

    now = datetime.now()
    if "minutes" in validity:
        return (now - mtime) <= timedelta(minutes=validity["minutes"])
    if "hours" in validity:
        return (now - mtime) <= timedelta(hours=validity["hours"])
    if "days" in validity:
        return (now - mtime) <= timedelta(days=validity["days"])

    return True

# ==============================
# Utilities
# ==============================
def list_files(name=None, ftype=None):
    files = sorted(_list_files())
    if name:
        files = [f for f in files if f.startswith(name + "_")]
    if ftype:
        files = [f for f in files if f.endswith("." + ftype)]
    return files
'''
import pandas as pd
from hf_persistence import save, load, exists

# Save DataFrame
df = pd.DataFrame({"A":[1,2], "B":[3,4]})
save("intraday_RELIANCE", df, "csv")

# Check existence with TTL
if exists("intraday_RELIANCE", "csv"):
    df_cached = load("intraday_RELIANCE", "csv")

# Save HTML
save("intraday_RELIANCE", "<h1>Hello</h1>", "html")
if exists("intraday_RELIANCE", "html"):
    html_cached = load("intraday_RELIANCE", "html")
'''