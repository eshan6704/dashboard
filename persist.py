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
def save(name: str, data: Any, ftype: str = "csv") -> str | bool:
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
            raise ValueError("Unsupported file type")

        return filename

    except Exception:
        return False

# ==============================
# LOAD (STRICT)
# ==============================
def load(name: str, ftype: str | None = None):
    """
    Allowed:
      load("nifty_YYYY_MM_DD_HH_MM_SS.csv")
      load("nifty", "csv")
    """

    # Full filename
    if "." in name:
        filename = name

    # Base name + type
    else:
        if not ftype:
            return False
        filename = _latest(name, ftype)
        if not filename:
            return False

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
# EXISTS (NEW FUNCTION)
# ==============================
def exists(name: str, ftype: str | None = None) -> bool:
    """
    True  -> file exists
    False -> file not present

    Allowed:
      exists("nifty_YYYY_MM_DD_HH_MM_SS.csv")
      exists("nifty", "csv")
    """

    # Full filename
    if "." in name:
        return os.path.exists(_path(name))

    # Base name + type
    if not ftype:
        return False

    return _latest(name, ftype) is not None

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
#save("nifty", df, "csv")

# CHECK existence (NO load)
#if exists("nifty", "csv"):
    #df = load("nifty", "csv")

# CHECK specific file
#if exists("nifty_2025_12_18_10_30_00.csv"):
    #df_old = load("nifty_2025_12_18_10_30_00.csv")
