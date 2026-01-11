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

# ===========================================================
# RAW DAILY FETCHER
# ===========================================================
def daily(symbol, date_end, date_start):
    """Fetch daily OHLCV from Yahoo Finance."""
    start = dt.strptime(date_start, "%d-%m-%Y").strftime("%Y-%m-%d")
    end = dt.strptime(date_end, "%d-%m-%Y").strftime("%Y-%m-%d")
    df = yf.download(symbol + ".NS", start=start, end=end)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.columns.name = None
    df.index.name = "Date"
    return df

# ===========================================================
# CANDLESTICK + VOLUME
# ===========================================================
def plot_candlestick(df, symbol):
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df['Date'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price',
        increasing_line_color='green',
        decreasing_line_color='red'
    ))

    fig.add_trace(go.Bar(
        x=df['Date'],
        y=df['Volume'],
        name='Volume',
        yaxis='y2',
        marker_color='blue',
        opacity=0.3
    ))

    fig.update_layout(
        title=f'{symbol} Daily Candlestick',
        xaxis_rangeslider_visible=False,
        yaxis=dict(title='Price'),
        yaxis2=dict(title='Volume', overlaying='y', side='right', showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return pio.to_html(fig, full_html=False, include_plotlyjs='cdn')

# ===========================================================
# ADDITIONAL ANALYSIS CHARTS
# ===========================================================
def plot_analysis_charts(df, symbol):
    charts = ""

    # OHLC line chart
    fig_line = px.line(df, x='Date', y=['Open','High','Low','Close'], title=f'{symbol} OHLC Line Chart')
    charts += pio.to_html(fig_line, full_html=False, include_plotlyjs=False)

    # 20 & 50-day moving averages
    df['MA20'] = df['Close'].rolling(20).mean()
    df['MA50'] = df['Close'].rolling(50).mean()
    fig_ma = px.line(df, x='Date', y=['Close','MA20','MA50'], title=f'{symbol} 20 & 50 Day Moving Avg')
    charts += pio.to_html(fig_ma, full_html=False, include_plotlyjs=False)

    # Daily % change
    df['Change %'] = ((df['Close'] - df['Open']) / df['Open'] * 100).round(2)
    fig_change = px.bar(df, x='Date', y='Change %', color='Change %', title=f'{symbol} Daily % Change',
                        color_continuous_scale=['red','green'])
    charts += pio.to_html(fig_change, full_html=False, include_plotlyjs=False)

    return charts

# ===========================================================
# DAILY DASHBOARD
# ===========================================================
def fetch_daily(symbol, date_end, date_start):
    """Return HTML table + candlestick + analysis charts."""
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

        # Drop rows with missing OHLCV
        df = df.dropna(subset=["Open","High","Low","Close","Volume"]).reset_index()

        # Format date
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
        df = df.dropna(subset=["Date"]).reset_index(drop=True)
        df["Date"] = df["Date"].dt.strftime("%d-%b-%Y")

        # Daily change %
        df["Change %"] = ((df["Close"] - df["Open"]) / df["Open"] * 100).round(2)

        # Build HTML table with improved header CSS
        html_table = '<div style="max-height:300px; overflow:auto; font-family:Arial,sans-serif; margin-bottom:20px;">'
        html_table += '<table border="1" style="border-collapse:collapse; width:100%;">'
        html_table += '''
            <thead style="
                position:sticky;
                top:0;
                background: linear-gradient(to right,#1a4f8a,#4a7ac7);
                color:white;
                font-weight:bold;
                text-align:center;
            ">
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

        # Candlestick chart
        candlestick_html = plot_candlestick(df, symbol)

        # Additional analysis charts
        analysis_html = plot_analysis_charts(df, symbol)

        # Combine all in dashboard
        full_html = f'<div id="daily_dashboard">{html_table}{candlestick_html}{analysis_html}</div>'

        persist.save(key, full_html, "html")
        return full_html

    except Exception as e:
        return wrap_html(f"<h1>Error fetch_daily: {e}</h1><pre>{traceback.format_exc()}</pre>")
