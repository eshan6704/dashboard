# chart_builder.py

import io
import matplotlib.pyplot as plt
from PIL import Image

# ============================================================
# CONFIG
# ============================================================
DPI = 150
JPEG_QUALITY = 85


# ============================================================
# INTERNAL HELPERS
# ============================================================
def _fig_to_jpeg_bytes(fig) -> bytes:
    """
    Render matplotlib figure → PNG buffer → JPEG (Pillow)
    """
    png_buf = io.BytesIO()
    fig.savefig(png_buf, format="png", dpi=DPI, bbox_inches="tight")
    plt.close(fig)

    png_buf.seek(0)
    img = Image.open(png_buf).convert("RGB")

    jpg_buf = io.BytesIO()
    img.save(
        jpg_buf,
        format="JPEG",
        quality=JPEG_QUALITY,
        optimize=True,
        progressive=True
    )
    return jpg_buf.getvalue()


# ============================================================
# PRICE + VOLUME
# ============================================================
def price_volume(df, symbol: str) -> bytes:
    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(df["Date"], df["Close"], label="Close", linewidth=2)

    vol_scaled = df["Volume"] / df["Volume"].max() * df["Close"].max()
    ax.bar(df["Date"], vol_scaled, alpha=0.25, label="Volume")

    ax.set_title(f"{symbol} Price & Volume")
    ax.legend()
    ax.grid(True)

    return _fig_to_jpeg_bytes(fig)


# ============================================================
# MOVING AVERAGES
# ============================================================
def moving_average(df, symbol: str) -> bytes:
    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(df["Date"], df["Close"], label="Close", linewidth=2)
    ax.plot(df["Date"], df["MA20"], label="MA20")
    ax.plot(df["Date"], df["MA50"], label="MA50")

    ax.set_title(f"{symbol} Moving Averages")
    ax.legend()
    ax.grid(True)

    return _fig_to_jpeg_bytes(fig)