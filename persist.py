import os
import json
import pickle
import pandas as pd
from datetime import datetime, timedelta
from typing import Any
import yfinance as yf

# ==============================
# Configuration
# ==============================
BASE_DIR = "./data/store"
os.makedirs(BASE_DIR, exist_ok=True)

# TTL validity map (per parent type)
VALIDITY_MAP = {
    "result": {"days": 7},
    "qresult": {"days": 7},
    "bhav": {"days": 1},
    "intraday": {"minutes": 15},
    "eq": {"hours": 1},
    "daily": {"days": 1},
}

# ==============================
# Helpers
# ==============================
def _ts():
    return datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

def _path(filename: str):
    return os.path.join(BASE_DIR, filename)

def _list_files():
    return os.listdir(BASE_DIR)

def _latest(prefix: str, ext: str):
    files = [
        f for f in _list_files()
        if f.startswith(prefix + "_") and f.endswith("." + ext)
    ]
    return max(files) if files else None

# ==============================
# Save / Load / Exists
# ==============================
def save(name: str, data: Any, ftype: str) -> bool:
    ts = _ts()
    filename = f"{name}_{ts}.{ftype}"
    path = _path(filename)
    try:
        if ftype == "csv":
            if not isinstance(data, pd.DataFrame):
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [SAVE FAILED] CSV requires pandas DataFrame for {filename}")
                return False
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
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [SAVE FAILED] Unsupported file type: {ftype} for {filename}")
            return False
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [SAVE OK] {filename}")
        return True
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [SAVE FAILED] {filename} - Exception: {e}")
        return False

def load(name: str, ftype: str):
    filename = _latest(name, ftype) if "." not in name else name
    path = _path(filename)
    if not os.path.exists(path):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [LOAD FAILED] File does not exist: {filename}")
        return False
    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(path)
        elif filename.endswith(".json"):
            with open(path, "r", encoding="utf-8") as f:
                df = json.load(f)
        elif filename.endswith(".html"):
            with open(path, "r", encoding="utf-8") as f:
                df = f.read()
        elif filename.endswith(".pkl"):
            with open(path, "rb") as f:
                df = pickle.load(f)
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [LOAD FAILED] Unsupported file type: {filename}")
            return False
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [LOAD OK] {filename}")
        return df
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [LOAD FAILED] {filename} - Exception: {e}")
        return False

def exists(name: str, ftype: str) -> bool:
    """
    Checks if a file exists AND is valid within TTL based on parent type + symbol.
    Example:
      name = INTRADAY_RELIANCE
      matches any file starting with INTRADAY_RELIANCE_YYYY_MM_DD_HH_MM_SS.csv
      TTL applied according to parent type (INTRADAY -> 15 minutes)
    """
    filename = _latest(name, ftype)
    if not filename:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [EXISTS] No file found for {name}.{ftype}")
        return False

    path = _path(filename)
    if not os.path.exists(path):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [EXISTS] File not present: {filename}")
        return False

    parent_func = name.split("_")[0].lower()  # INTRADAY, RESULT, etc.
    validity = VALIDITY_MAP.get(parent_func)
    if not validity:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [EXISTS] File exists with no TTL: {filename}")
        return True

    mtime = datetime.fromtimestamp(os.path.getmtime(path))
    now = datetime.now()
    is_valid = True
    if "minutes" in validity:
        is_valid = (now - mtime) <= timedelta(minutes=validity["minutes"])
    elif "hours" in validity:
        is_valid = (now - mtime) <= timedelta(hours=validity["hours"])
    elif "days" in validity:
        is_valid = (now - mtime) <= timedelta(days=validity["days"])

    if is_valid:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [EXISTS] File exists and valid: {filename}")
    else:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [EXISTS] File expired: {filename}")

    return is_valid

def list_files(name=None, ftype=None):
    files = sorted(_list_files())
    if name:
        files = [f for f in files if f.startswith(name + "_")]
    if ftype:
        files = [f for f in files if f.endswith("." + ftype)]
    return files


