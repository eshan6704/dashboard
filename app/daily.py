# daily.py
import yfinance as yf
import pandas as pd
from datetime import datetime as dt
import traceback

from .svg_charts import price_volume_chart, rsi_chart, macd_chart

def fetch_daily(symbol, date_end, date_start):
    try:
        # -------------------------
        # Convert date
        # -------------------------
        start = dt.strptime(date_start,"%d-%m-%Y").strftime("%Y-%m-%d")
        end   = dt.strptime(date_end,"%d-%m-%Y").strftime("%Y-%m-%d")

        # -------------------------
        # Fetch data
        # -------------------------
        df = yf.download(symbol+".NS",start=start,end=end)

        if isinstance(df.columns,pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.reset_index()
        for c in ["Open","High","Low","Close","Volume"]:
            df[c] = pd.to_numeric(df[c],errors="coerce")

        df = df.dropna(subset=["Date","Open","High","Low","Close","Volume"])
        if df.empty:
            return f"<h3>No valid data for {symbol}.</h3>"

        df["DateStr"] = df["Date"].dt.strftime("%d-%b-%Y")

        # ------------------------- Indicators -------------------------
        df["MA20"] = df["Close"].rolling(20).mean()
        df["MA50"] = df["Close"].rolling(50).mean()

        delta = df["Close"].diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = -delta.clip(upper=0).rolling(14).mean()
        rs = gain/loss
        df["RSI"] = 100-(100/(1+rs))

        ema12 = df["Close"].ewm(span=12).mean()
        ema26 = df["Close"].ewm(span=26).mean()
        df["MACD"] = ema12-ema26
        df["MACD_SIGNAL"] = df["MACD"].ewm(span=9).mean()

        # ------------------------- Limit view -------------------------
        view = df.tail(120)
        if view.empty:
            return f"<h3>No data to render charts for {symbol}.</h3>"

        # ------------------------- Insights -------------------------
        lo=view["Low"].min()
        hi=view["High"].max()
        close=view.iloc[-1]["Close"]

        insights={
            "Date Range": f"{view.iloc[0]['DateStr']} → {view.iloc[-1]['DateStr']}",
            "Price Range": f"{lo:.2f} – {hi:.2f}",
            "Current Price": f"{close:.2f}",
            "Recovery from Low": f"{(close-lo)/lo*100:.2f} %",
            "Drawdown from High": f"{(hi-close)/hi*100:.2f} %",
            "Target to High": f"{(hi-close)/close*100:.2f} %",
            "Trend": "Bullish" if close>view.iloc[-1]["MA50"] else "Bearish",
            "MA Status": "MA20 > MA50" if view.iloc[-1]["MA20"]>view.iloc[-1]["MA50"] else "MA20 < MA50",
            "Avg Volume (20D)": f"{int(view['Volume'].tail(20).mean())}"
        }

        insight_rows = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k,v in insights.items())

        # ------------------------- Charts -------------------------
        chart_price = price_volume_chart(view, f"{symbol} – Price & Volume")
        chart_rsi   = rsi_chart(view)
        chart_macd  = macd_chart(view)

        # ------------------------- Historical Table -------------------------
        rows=""
        for r in view.tail(100).itertuples():
            rows+=f"""
<tr>
<td>{r.DateStr}</td><td>{r.Open:.2f}</td><td>{r.High:.2f}</td>
<td>{r.Low:.2f}</td><td>{r.Close:.2f}</td><td>{int(r.Volume)}</td>
</tr>"""

        # ------------------------- HTML -------------------------
        html=f"""
<div style="font-family:Arial;background:white;color:#111;padding:10px">

<h2>{symbol} – Pro Daily Dashboard</h2>

<h3>Key Insights</h3>
<table border="1" cellpadding="6" style="border-collapse:collapse;font-size:13px">
{insight_rows}
</table>

<h3>Price Action</h3>
{chart_price}

<h3>RSI (14)</h3>
{chart_rsi}

<h3>MACD</h3>
{chart_macd}

<h3>Historical Data (Last 100 Days)</h3>
<table border="1" cellpadding="6" width="100%" style="border-collapse:collapse;font-size:13px">
<tr style="background:#f2f2f2"><th>Date</th><th>Open</th><th>High</th><th>Low</th><th>Close</th><th>Volume</th></tr>
{rows}
</table>

</div>
"""
        return html

    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>"
