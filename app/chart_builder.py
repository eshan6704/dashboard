import io
import matplotlib.pyplot as plt


def build_price_volume(df, symbol):
    """
    Builds price + volume chart
    RETURNS: png image bytes (NOT saving here)
    """

    buf = io.BytesIO()

    plt.figure(figsize=(14, 6))

    # Price
    plt.plot(df["Date"], df["Close"], label="Close", linewidth=2)

    # Volume (scaled)
    vol_scaled = df["Volume"] / df["Volume"].max() * df["Close"].max()
    plt.bar(df["Date"], vol_scaled, alpha=0.3, label="Volume")

    plt.title(f"{symbol} Price & Volume")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    # IMPORTANT: PNG ONLY
    plt.savefig(buf, format="png", dpi=150)
    plt.close()

    buf.seek(0)
    return buf.getvalue()


def build_moving_avg(df, symbol):
    """
    Optional: only if daily.py calls this
    """

    buf = io.BytesIO()

    plt.figure(figsize=(14, 6))
    plt.plot(df["Date"], df["Close"], label="Close", linewidth=2)
    plt.plot(df["Date"], df["MA20"], label="MA20")
    plt.plot(df["Date"], df["MA50"], label="MA50")

    plt.title(f"{symbol} Moving Averages")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plt.savefig(buf, format="png", dpi=150)
    plt.close()

    buf.seek(0)
    return buf.getvalue()