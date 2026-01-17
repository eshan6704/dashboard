# chart_builder.py
import io
import matplotlib.pyplot as plt

DPI = 150


def price_volume(df, symbol):
    """
    Returns:
      base_name, image_bytes, ext
    """
    plt.figure(figsize=(14, 6))
    plt.plot(df["Date"], df["Close"], label="Close", linewidth=2)

    vol_scaled = df["Volume"] / df["Volume"].max() * df["Close"].max()
    plt.bar(df["Date"], vol_scaled, alpha=0.25, label="Volume")

    plt.title(f"{symbol} Price & Volume")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=DPI, bbox_inches="tight")
    plt.close()

    buf.seek(0)

    base = f"@stock@daily@{symbol}@price"
    return base, buf.read(), "png"


def moving_avg(df, symbol):
    plt.figure(figsize=(14, 6))
    plt.plot(df["Date"], df["Close"], label="Close", linewidth=2)
    plt.plot(df["Date"], df["MA20"], label="MA20")
    plt.plot(df["Date"], df["MA50"], label="MA50")

    plt.title(f"{symbol} Moving Averages")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=DPI, bbox_inches="tight")
    plt.close()

    buf.seek(0)

    base = f"@stock@daily@{symbol}@ma"
    return base, buf.read(), "png"