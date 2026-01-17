# chart_builder.py
import io
import matplotlib.pyplot as plt
from typing import Tuple
from . import persist

IMAGE_FORMAT = "jpeg"  # save as JPEG for smaller size
DPI = 150

def price_volume(df, symbol) -> Tuple[str, bytes]:
    """
    Generates Price & Volume chart for a DataFrame.
    Returns: (filename, bytes)
    """
    buf = io.BytesIO()
    plt.figure(figsize=(14, 6))
    plt.plot(df["Date"], df["Close"], label="Close", linewidth=2)

    # Scale volume to match price scale
    vol_scaled = df["Volume"] / df["Volume"].max() * df["Close"].max()
    plt.bar(df["Date"], vol_scaled, alpha=0.25, label="Volume")

    plt.title(f"{symbol} Price & Volume")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(buf, format=IMAGE_FORMAT, dpi=DPI, bbox_inches="tight")
    plt.close()
    buf.seek(0)

    # Universal filename
    filename = f"@stock@daily@{symbol}@price.{IMAGE_FORMAT}"
    return filename, buf.read()


def moving_avg(df, symbol) -> Tuple[str, bytes]:
    """
    Generates Moving Average chart for a DataFrame.
    Returns: (filename, bytes)
    """
    buf = io.BytesIO()
    plt.figure(figsize=(14, 6))
    plt.plot(df["Date"], df["Close"], label="Close", linewidth=2)
    plt.plot(df["Date"], df["MA20"], label="MA20")
    plt.plot(df["Date"], df["MA50"], label="MA50")

    plt.title(f"{symbol} Moving Averages")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(buf, format=IMAGE_FORMAT, dpi=DPI, bbox_inches="tight")
    plt.close()
    buf.seek(0)

    filename = f"@stock@daily@{symbol}@ma.{IMAGE_FORMAT}"
    return filename, buf.read()