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

# TTL validity map
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
# Save function
# ==============================
def save(name: str, data: Any, ftype: str) -> bool:
    ts = _ts()
    filename = f"{name}_{ts}.{ftype}"
    path = _path(filename)
    try:
        if ftype == "csv":
            if not isinstance(data, pd.DataFrame):
                print(f"[SAVE FAILED] CSV requires pandas DataFrame for {filename}")
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
            print(f"[SAVE FAILED] Unsupported file type: {ftype} for {filename}")
            return False
        print(f"[SAVE OK] {filename}")
        return True
    except Exception as e:
        print(f"[SAVE FAILED] {filename} - Exception: {e}")
        return False

# ==============================
# Load function
# ==============================
def load(name: str, ftype: str):
    filename = _latest(name, ftype) if "." not in name else name
    path = _path(filename)
    if not os.path.exists(path):
        print(f"[LOAD FAILED] File does not exist: {filename}")
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
            print(f"[LOAD FAILED] Unsupported file type: {filename}")
            return False
        print(f"[LOAD OK] {filename}")
        return df
    except Exception as e:
        print(f"[LOAD FAILED] {filename} - Exception: {e}")
        return False

# ==============================
# Exists with TTL
# ==============================
def exists(name: str, ftype: str) -> bool:
    filename = _latest(name, ftype)
    if not filename:
        print(f"[EXISTS] No file found for {name}.{ftype}")
        return False

    path = _path(filename)
    if not os.path.exists(path):
        print(f"[EXISTS] File not present: {filename}")
        return False

    mtime = datetime.fromtimestamp(os.path.getmtime(path))
    func_name = name.split("_")[0]
    validity = VALIDITY_MAP.get(func_name)
    if not validity:
        print(f"[EXISTS] File exists with no TTL: {filename}")
        return True

    now = datetime.now()
    is_valid = True
    if "minutes" in validity:
        is_valid = (now - mtime) <= timedelta(minutes=validity["minutes"])
    elif "hours" in validity:
        is_valid = (now - mtime) <= timedelta(hours=validity["hours"])
    elif "days" in validity:
        is_valid = (now - mtime) <= timedelta(days=validity["days"])

    if is_valid:
        print(f"[EXISTS] File exists and valid: {filename}")
    else:
        print(f"[EXISTS] File expired: {filename}")

    return is_valid

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
