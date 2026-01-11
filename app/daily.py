# daily.py
import yfinance as yf
import pandas as pd
from datetime import datetime as dt
import traceback
from . import persist
from .common import wrap_html
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from plotly.subplots import make_subplots

# =========================
# DAILY DATA FETCH
# =========================
def daily(symbol, date_end, date_start):
    start = dt.strptime(date_start, "%d-%m-%Y").strftime("%Y-%m-%d")
    end = dt.strptime(date_end, "%d-%m-%Y").strftime("%Y-%m-%d")
    df = yf.download(symbol + ".NS", start=start, end=end)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.columns.name = None
    df.index.name = "Date"
    return df

# =========================
# DASHBOARD
# =========================
def fetch_daily(symbol, date_end, date_start):
    key = f"daily_{symbol}"
    if persist.exists(key, "html"):
        cached = persist.load(key, "html")
        if cached:
            return cached

    try:
        df = daily(symbol, date_end, date_start)
        if df.empty:
            return wrap_html(f"<h1>No daily data for {symbol}</h1>")

        # Ensure numeric columns
        for col in ["Open","High","Low","Close","Volume"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        df = df.dropna(subset=["Open","High","Low","Close","Volume"]).reset_index()
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
        df = df.dropna(subset=["Date"]).reset_index(drop=True)
        df["Date"] = df["Date"].dt.strftime("%d-%b-%Y")
        df["Change %"] = ((df["Close"] - df["Open"]) / df["Open"] * 100).round(2)

        # -------------------------
        # HTML Table
        # -------------------------
        html_table = '<div style="max-height:300px; overflow:auto; font-family:Arial,sans-serif; margin-bottom:20px;">'
        html_table += '<table border="1" style="border-collapse:collapse; width:100%;">'
        html_table += '''
            <thead style="
                position:sticky;
                top:0;
                background: linear-gradient(to right,#1a4f8a,#4a7ac7);
                color:white;
                font-weight:bold;
                text-align:center;">
        '''
        html_table += '<tr><th>Date</th><th>Open</th><th>High</th><th>Low</th>'
        html_table += '<th>Close</th><th>Volume</th><th>Change %</th></tr></thead><tbody>'
        for idx, r in df.iterrows():
            row_color = "#e8f5e9" if idx % 2 == 0 else "#f5f5f5"
            change_color = "green" if r["Change %"] > 0 else "red" if r["Change %"] < 0 else "black"
            html_table += f'<tr style="background:{row_color};">'
            html_table += f'<td>{r["Date"]}</td>'
            html_table += f'<td>{r["Open"]}</td>'
            html_table += f'<td>{r["High"]}</td>'
            html_table += f'<td>{r["Low"]}</td>'
            html_table += f'<td>{r["Close"]}</td>'
            html_table += f'<td>{r["Volume"]}</td>'
            html_table += f'<td style="color:{change_color}; font-weight:600;">{r["Change %"]}%</td>'
            html_table += '</tr>'
        html_table += '</tbody></table></div>'

        # -------------------------
        # COMBINED PLOTLY FIGURE
        # -------------------------
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            row_heights=[0.5, 0.25, 0.25],
            vertical_spacing=0.05,
            subplot_titles=("Candlestick & Volume", "MA20/MA50", "Daily % Change")
        )

        # Candlestick
        fig.add_trace(go.Candlestick(
            x=df['Date'], open=df['Open'], high=df['High'],
            low=df['Low'], close=df['Close'], name='Price',
            increasing_line_color='green', decreasing_line_color='red'
        ), row=1, col=1)

        # Volume as bar
        fig.add_trace(go.Bar(
            x=df['Date'], y=df['Volume'], name='Volume',
            marker_color='blue', opacity=0.3
        ), row=1, col=1)

        # MA20 & MA50
        df['MA20'] = df['Close'].rolling(20).mean()
        df['MA50'] = df['Close'].rolling(50).mean()
        fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Close'), row=2, col=1)
        fig.add_trace(go.Scatter(x=df['Date'], y=df['MA20'], mode='lines', name='MA20'), row=2, col=1)
        fig.add_trace(go.Scatter(x=df['Date'], y=df['MA50'], mode='lines', name='MA50'), row=2, col=1)

        # Daily % change
        fig.add_trace(go.Bar(
            x=df['Date'], y=df['Change %'], name='Change %',
            marker_color=df['Change %'].apply(lambda x: 'green' if x>0 else 'red')
        ), row=3, col=1)

        fig.update_layout(height=900, showlegend=True, xaxis_rangeslider_visible=False)

        plot_html = pio.to_html(fig, full_html=False, include_plotlyjs='cdn')

        # -------------------------
        # COMBINE TABLE + CHART
        # -------------------------
        full_html = f'<div id="daily_dashboard">{html_table}{plot_html}</div>'
        persist.save(key, full_html, "html")
        return full_html

    except Exception as e:
        return wrap_html(f"<h1>Error fetch_daily: {e}</h1><pre>{traceback.format_exc()}</pre>")
