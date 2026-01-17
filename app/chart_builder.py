# chart_builder.py
import matplotlib.pyplot as plt
import io
from PIL import Image
from pathlib import Path
from datetime import datetime

# Base folder for persistent storage
FILES_DIR = Path("/data/files")
FILES_DIR.mkdir(parents=True, exist_ok=True)

# =========================================================
# Helper to save figure as JPEG using Pillow
# =========================================================
def _save_fig(buf: io.BytesIO, filename: str, quality=85) -> str:
    """
    Save matplotlib figure buffer as JPEG via Pillow.
    Returns full path of saved file.
    """
    buf.seek(0)
    img = Image.open(buf)
    img = img.convert("RGB")  # JPEG requires RGB
    file_path = FILES_DIR / filename
    img.save(file_path, format="JPEG", quality=quality)
    return str(file_path)

# =========================================================
# Price + Volume chart
# =========================================================
def price_volume(df, symbol: str) -> str:
    """
    Generates Price & Volume chart and saves JPEG.
    Returns filename.
    """
    buf = io.BytesIO()
    plt.figure(figsize=(14,6))
    plt.plot(df["Date"], df["Close"], label="Close", linewidth=2)
    vol_scaled = df["Volume"] / df["Volume"].max() * df["Close"].max()
    plt.bar(df["Date"], vol_scaled, alpha=0.25, label="Volume")
    plt.title(f"{symbol} Price & Volume")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(buf, format="png", dpi=150)  # save as PNG first
    plt.close()

    # Generate filename
    filename = f"@stock@daily@{symbol}@price.jpg"
    return _save_fig(buf, filename)

# =========================================================
# Moving Average chart
# =========================================================
def moving_average(df, symbol: str) -> str:
    """
    Generates MA20 + MA50 chart and saves JPEG.
    Returns filename.
    """
    buf = io.BytesIO()
    plt.figure(figsize=(14,6))
    plt.plot(df["Date"], df["Close"], label="Close", linewidth=2)
    plt.plot(df["Date"], df["MA20"], label="MA20")
    plt.plot(df["Date"], df["MA50"], label="MA50")
    plt.title(f"{symbol} Moving Averages")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(buf, format="png", dpi=150)
    plt.close()

    filename = f"@stock@daily@{symbol}@ma.jpg"
    return _save_fig(buf, filename)