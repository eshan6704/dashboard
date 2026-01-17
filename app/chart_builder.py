# chart_builder.py

import io
import matplotlib.pyplot as plt

# ============================================================
# CONFIG
# ============================================================
IMAGE_FORMAT = "jpeg"
IMAGE_EXT = "jpg"
DPI = 140
JPEG_QUALITY = 80


# ============================================================
# INTERNAL HELPER
# ============================================================
def _save_fig():
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(
        buf,
        format=IMAGE_FORMAT,
        dpi=DPI,
        bbox_inches="tight",
        quality=JPEG_QUALITY
    )
    plt.close()
    buf.seek(0)
    return buf.getvalue()


# ============================================================
# PUBLIC CHART BUILDERS
# ============================================================
def price_volume(df, symbol):
    """
    Price + Volume chart
    suffix: price_volume
    """
    plt.figure(figsize=(14, 6))

    plt.plot(df["Date"], df["Close"], label="Close", linewidth=2)

    vol_scaled = df["Volume"] / df["Volume"].max() * df["Close"].max()
    plt.bar(df["Date"], vol_scaled, alpha=0.25, label="Volume")

    plt.title(f"{symbol} Price & Volume")
    plt.legend()
    plt.grid(True)

    return _save_fig()


def moving_average(df, symbol):
    """
    Moving Average chart
    suffix: ma
    """
    plt.figure(figsize=(14, 6))

    plt.plot(df["Date"], df["Close"], label="Close", linewidth=2)
    plt.plot(df["Date"], df["MA20"], label="MA20")
    plt.plot(df["Date"], df["MA50"], label="MA50")

    plt.title(f"{symbol} Moving Averages")
    plt.legend()
    plt.grid(True)

    return _save_fig()