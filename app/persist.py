import os
import json
import pickle
import pandas as pd
from datetime import datetime
from typing import Any

# ==============================
# Configuration
# ==============================
BASE_DIR = "./data/store"
os.makedirs(BASE_DIR, exist_ok=True)

IMAGE_TYPES = {"png", "jpg", "jpeg"}

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
# Save
# ==============================
def save(name: str, data: Any, ftype: str, timestamped=True) -> bool:
    """
    name: base filename without extension
    ftype: html, json, csv, pkl, png, jpg, jpeg
    timestamped: False for stable assets like images
    """
    try:
        if ftype in IMAGE_TYPES:
            filename = f"{name}.{ftype}"
        else:
            ts = _ts() if timestamped else ""
            filename = f"{name}_{ts}.{ftype}" if ts else f"{name}.{ftype}"

        path = _path(filename)

        if ftype == "csv":
            if not isinstance(data, pd.DataFrame):
                raise ValueError("CSV requires pandas DataFrame")
            data.to_csv(path, index=False)

        elif ftype == "json":
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

        elif ftype == "html":
            with open(path, "w", encoding="utf-8") as f:
                f.write(str(data))

        elif ftype in IMAGE_TYPES:
            # data can be bytes or a file path
            if isinstance(data, (bytes, bytearray)):
                with open(path, "wb") as f:
                    f.write(data)
            elif isinstance(data, str) and os.path.exists(data):
                with open(data, "rb") as src, open(path, "wb") as dst:
                    dst.write(src.read())
            else:
                raise ValueError("Image data must be bytes or file path")

        elif ftype == "pkl":
            with open(path, "wb") as f:
                pickle.dump(data, f)

        else:
            raise ValueError(f"Unsupported file type: {ftype}")

        print(f"[SAVE OK] {filename}")
        return True

    except Exception as e:
        print(f"[SAVE FAILED] {name}.{ftype} → {e}")
        return False

# ==============================
# Load
# ==============================
def load(name: str, ftype: str):
    filename = name if "." in name else _latest(name, ftype)
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

        if filename.endswith(tuple(IMAGE_TYPES)):
            with open(path, "rb") as f:
                return f.read()

        if filename.endswith(".pkl"):
            with open(path, "rb") as f:
                return pickle.load(f)

    except Exception as e:
        print(f"[LOAD FAILED] {filename} → {e}")
        return False

# ==============================
# Exists (NO TTL)
# ==============================
def exists(name: str, ftype: str) -> bool:
    if ftype in IMAGE_TYPES:
        return os.path.exists(_path(f"{name}.{ftype}"))

    filename = _latest(name, ftype)
    if not filename:
        return False

    return os.path.exists(_path(filename))

# ==============================
# List
# ==============================
def list_files(name=None, ftype=None):
    files = sorted(_list_files())
    if name:
        files = [f for f in files if f.startswith(name)]
    if ftype:
        files = [f for f in files if f.endswith("." + ftype)]
    return files