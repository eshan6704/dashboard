import os
import json
import pickle
import pandas as pd
from typing import Any
from datetime import datetime

# ==============================
# HF Persistent Base Directory
# ==============================
BASE_DIR = "/data/store"
os.makedirs(BASE_DIR, exist_ok=True)

# ==============================
# Helpers
# ==============================
def _ts():
    return datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

def _path(name):
    return os.path.join(BASE_DIR, name)

def _list_files():
    return os.listdir(BASE_DIR)

def _latest(prefix, ext):
    files = [
        f for f in _list_files()
        if f.startswith(prefix + "_") and f.endswith("." + ext)
    ]
    return max(files) if files else None

# ==============================
# SAVE
# ==============================
def save(name: str, data: Any, ftype: str = "csv") -> str:
    ts = _ts()
    filename = f"{name}_{ts}.{ftype}"
    path = _path(filename)

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

    return filename

# ==============================
# LOAD (STRICT)
# ==============================
def load(name: str, ftype: str | None = None):
    """
    Allowed:
      load("nifty_YYYY_MM_DD_HH_MM_SS.csv")
      load("nifty", "csv")
    """

    # Case 1: full filename
    if "." in name:
        path = _path(name)
        if not os.path.exists(path):
            return None
        filename = name

    # Case 2: base name + type
    else:
        if not ftype:
            raise ValueError("File type must be provided when filename is not full")
        filename = _latest(name, ftype)
        if not filename:
            return None
        path = _path(filename)

    # Load by extension
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

    raise ValueError(f"Unsupported file type: {filename}")

# ==============================
# UTILITIES
# ==============================
def list_files(name=None, ftype=None):
    files = sorted(_list_files())
    if name:
        files = [f for f in files if f.startswith(name + "_")]
    if ftype:
        files = [f for f in files if f.endswith("." + ftype)]
    return files


# SAVE
#save("nifty", df, ftype="csv")

# LOAD latest
#df_latest = load("nifty", "csv")

# LOAD specific version
#df_old = load("nifty_2025_12_18_10_30_00.csv")
