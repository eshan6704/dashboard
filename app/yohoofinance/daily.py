# daily.py
import yfinance as yf
import pandas as pd
from datetime import datetime as dt
import traceback

from app.svgchart import candlestick_chart, line_chart, rsi_chart, macd_chart

def fetch_daily(symbol,date_end,date_start):
    try:
        start=dt.strptime(date_start,"%d-%m-%Y").strftime("%Y-%m-%d")
        end=dt.strptime(date_end,"%d-%m-%Y").strftime("%Y-%m-%d")

        df=yf.download(symbol+".NS",start=start,end=end)
        if df.empty:
            return f"<h3>No data for {symbol}</h3>"

        if isinstance(df.columns,pd.MultiIndex):
            df.columns=df.columns.get_level_values(0)

        df=df.reset_index()
        for c in ["Open","High","Low","Close","Volume"]:
            df[c]=pd.to_numeric(df[c],errors="coerce")
        df=df.dropna(subset=["Date","Open","High","Low","Close","Volume"])
        if df.empty:
            return f"<h3>No valid numeric data for {symbol}</h3>"

        df["DateStr"]=df["Date"].dt.strftime("%d-%b-%Y")

        # Indicators
        df["MA20"]=df["Close"].rolling(20).mean()
        df["MA50"]=df["Close"].rolling(50).mean()
        delta=df["Close"].diff()
        gain=delta.clip(lower=0).rolling(14).mean()
        loss=-delta.clip(upper=0).rolling(14).mean()
        rs=gain/loss
        df["RSI"]=100-(100/(1+rs))
        ema12=df["Close"].ewm(span=12).mean()
        ema26=df["Close"].ewm(span=26).mean()
        df["MACD"]=ema12-ema26
        df["MACD_SIGNAL"]=df["MACD"].ewm(span=9).mean()
        df["ATR"] = df["High"] - df["Low"]  # Simple ATR daily
        df["Volatility"]=df["Close"].pct_change().rolling(14).std()*100

        view=df.tail(120)
        if view.empty:
            return f"<h3>No data to render charts for {symbol}</h3>"

        # Insights cards
        lo=view["Low"].min()
        hi=view["High"].max()
        close=view.iloc[-1]["Close"]
        high52 = df["High"].tail(252).max()
        low52 = df["Low"].tail(252).min()
        recovery = (close-lo)/lo*100
        drawdown = (hi-close)/hi*100
        target = (hi-close)/close*100
        trend = "Bullish" if close>view.iloc[-1]["MA50"] else "Bearish"
        avgvol = int(view["Volume"].tail(20).mean())
        atr = view["ATR"].tail(20).mean()
        vol = view["Volatility"].tail(20).mean()

        insights = {
            "Date Range": f"{view.iloc[0]['DateStr']} → {view.iloc[-1]['DateStr']}",
            "Price Range": f"{lo:.2f} – {hi:.2f}",
            "Current Price": f"{close:.2f}",
            "Recovery from Low": f"{recovery:.2f} %",
            "Drawdown from High": f"{drawdown:.2f} %",
            "Target to High": f"{target:.2f} %",
            "Trend": trend,
            "Avg Volume (20D)": f"{avgvol}",
            "52W High": f"{high52:.2f}",
            "% from 52W High": f"{(close-high52)/high52*100:.2f} %",
            "52W Low": f"{low52:.2f}",
            "% from 52W Low": f"{(close-low52)/low52*100:.2f} %",
            "ATR(20)": f"{atr:.2f}",
            "Volatility(14)": f"{vol:.2f} %"
        }

        cards_html = ""
        for k,v in insights.items():
            cards_html+=f'<div style="display:inline-block;border:1px solid #ccc;padding:10px;margin:5px;border-radius:5px;background:#f9f9f9;"><b>{k}</b><br>{v}</div>'

        # ----------------- Charts -----------------
        chart_main = candlestick_chart(view,f"{symbol} – Price & Volume")
        chart_rsi = rsi_chart(view)
        chart_macd = macd_chart(view)
        chart_weekly = line_chart(df.tail(52),column="Close",title="Weekly Trend (Last 52 Weeks)")
        chart_monthly = line_chart(df.tail(12),column="Close",title="Monthly Trend (Last 12 Months)")

        html=f"""
<div style="font-family:Arial;background:white;color:#111;padding:10px">

<h2>{symbol} – Professional Stock Dashboard</h2>

<h3>Key Insights</h3>
<div style="display:flex;flex-wrap:wrap">{cards_html}</div>

<h3>Main Price Chart</h3>
{chart_main}

<h3>Technical Indicators</h3>
{chart_rsi}
{chart_macd}

<h3>Other Timeframes</h3>
{chart_weekly}
{chart_monthly}

</div>
"""
        return html

    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>"
