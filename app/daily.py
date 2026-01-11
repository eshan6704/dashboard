# daily.py
import yfinance as yf
import pandas as pd
from datetime import datetime as dt
import traceback
from . import persist
from .common import wrap_html, format_large_number

# Plotly
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# ===========================================================
# RAW DAILY FETCHER
# ===========================================================
def daily(symbol, date_end, date_start):
    print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] yf called for {symbol}")
    
    start = dt.strptime(date_start, "%d-%m-%Y").strftime("%Y-%m-%d")
    end = dt.strptime(date_end, "%d-%m-%Y").strftime("%Y-%m-%d")
    
    df = yf.download(symbol + ".NS", start=start, end=end)
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.columns.name = None
    df.index.name = None
    
    return df

# ===========================================================
# TECHNICAL INDICATORS
# ===========================================================
def add_indicators(df):
    df["SMA10"] = df["Close"].rolling(10).mean()
    df["SMA50"] = df["Close"].rolling(50).mean()
    df["SMA200"] = df["Close"].rolling(200).mean()
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    delta = df["Close"].diff()
    gain = (delta.where(delta>0,0)).rolling(14).mean()
    loss = (-delta.where(delta<0,0)).rolling(14).mean()
    rs = gain/loss
    df["RSI14"] = 100 - (100/(1+rs))
    df["Change %"] = ((df["Close"] - df["Open"])/df["Open"]*100).round(2)
    return df

# ===========================================================
# SPARKLINE & MINI CANDLE
# ===========================================================
def sparkline(values, height=20, color="#1a4f8a"):
    if len(values) == 0: return ""
    max_val = max(values) if max(values)!=0 else 1
    bars = "".join([f'<div style="display:inline-block;width:3px;height:{int(v/max_val*height)}px;margin-right:1px;background:{color};"></div>' for v in values])
    return f'<div style="display:flex; align-items:flex-end;">{bars}</div>'

def volume_bar(values, height=20, color="#5584d6"):
    if len(values) == 0: return ""
    max_val = max(values) if max(values)!=0 else 1
    bars = "".join([f'<div style="display:inline-block;width:3px;height:{int(v/max_val*height)}px;margin-right:1px;background:{color};"></div>' for v in values])
    return f'<div style="display:flex; align-items:flex-end;">{bars}</div>'

# ===========================================================
# PLOTLY CHART GENERATOR
# ===========================================================
def plotly_dashboard(df, symbol):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.05, row_heights=[0.7,0.3],
                        subplot_titles=[f"{symbol} OHLC + SMA/EMA", "Volume"])
    
    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], 
        name="OHLC"), row=1, col=1)
    
    # Moving averages
    for col, name in [("SMA10","SMA10"),("SMA50","SMA50"),("SMA200","SMA200"),("EMA20","EMA20")]:
        fig.add_trace(go.Scatter(
            x=df.index, y=df[col], mode="lines", line=dict(width=1.5), name=name), row=1, col=1)
    
    # Volume bars
    fig.add_trace(go.Bar(
        x=df.index, y=df["Volume"], marker_color="#5584d6", name="Volume"), row=2, col=1)
    
    fig.update_layout(height=700, showlegend=True, margin=dict(t=50,b=50), template="plotly_white")
    
    # Return div as HTML
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

# ===========================================================
# DASHBOARD GENERATOR
# ===========================================================
def fetch_daily(symbol, date_end, date_start, spark_days=10):
    key = f"daily_{symbol}"
    if persist.exists(key, "html"):
        cached = persist.load(key, "html")
        if cached:
            return cached

    try:
        df = daily(symbol, date_end, date_start)
        if df.empty:
            return wrap_html(f"<h1>No daily data for {symbol}</h1>")

        if not isinstance(df.index, pd.RangeIndex):
            df.reset_index(inplace=True)
        
        # Numeric conversion
        for col in ["Open","High","Low","Close","Adj Close","Volume"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=["Open","High","Low","Close","Volume"]).reset_index(drop=True)

        # Format date
        df["Date"] = pd.to_datetime(df.index if "Date" not in df.columns else df["Date"], errors='coerce')
        df = df.dropna(subset=["Date"]).reset_index(drop=True)
        df["Date"] = df["Date"].dt.strftime("%d-%b-%Y")
        
        # Add indicators
        df = add_indicators(df)

        # Summary
        summary_html = f"""
        <div style="margin-bottom:10px; font-family:Arial,sans-serif;">
            <h3>{symbol} Summary</h3>
            <table border="1" style="border-collapse:collapse; width:400px;">
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>Start Date</td><td>{df['Date'].iloc[0]}</td></tr>
                <tr><td>End Date</td><td>{df['Date'].iloc[-1]}</td></tr>
                <tr><td>Min Close</td><td>{format_large_number(df['Close'].min())}</td></tr>
                <tr><td>Max Close</td><td>{format_large_number(df['Close'].max())}</td></tr>
                <tr><td>Mean Close</td><td>{format_large_number(df['Close'].mean())}</td></tr>
                <tr><td>Total Volume</td><td>{format_large_number(df['Volume'].sum())}</td></tr>
                <tr><td>Avg Daily Change %</td><td>{df['Change %'].mean():.2f}%</td></tr>
                <tr><td>Latest Close</td><td>{df['Close'].iloc[-1]}</td></tr>
                <tr><td>Prev Close</td><td>{df['Close'].iloc[-2] if len(df)>1 else df['Close'].iloc[-1]}</td></tr>
            </table>
        </div>
        """

        # Table with sparkline, volume, mini candle
        html_table = f"""
        <div style="max-height:400px; overflow:auto; font-family:Arial,sans-serif;">
        <table border="1" style="border-collapse:collapse; width:100%;">
            <thead style="position:sticky; top:0; background:#1a4f8a; color:white;">
                <tr>
                    <th>Date</th><th>Open</th><th>High</th><th>Low</th><th>Close</th><th>Adj Close</th>
                    <th>Volume</th><th>Change %</th><th>Close Trend</th><th>Vol Trend</th><th>Mini Candle</th>
                </tr>
            </thead>
            <tbody>
        """

        for idx, r in df.iterrows():
            row_color = "#e8f5e9" if idx%2==0 else "#f5f5f5"
            change_color = "green" if r["Change %"]>0 else "red" if r["Change %"]<0 else "black"
            start_idx = max(0, idx-spark_days+1)
            close_trend = sparkline(df["Close"].iloc[start_idx:idx+1].tolist())
            vol_trend = volume_bar(df["Volume"].iloc[start_idx:idx+1].tolist())
            mini_c = sparkline([r["Open"], r["High"], r["Low"], r["Close"]], height=20, color="#1a4f8a")

            html_table += f"""
                <tr style='background:{row_color};'>
                    <td>{r['Date']}</td>
                    <td>{r['Open']}</td>
                    <td>{r['High']}</td>
                    <td>{r['Low']}</td>
                    <td>{r['Close']}</td>
                    <td>{r.get('Adj Close','')}</td>
                    <td>{r['Volume']}</td>
                    <td style='color:{change_color}; font-weight:600;'>{r['Change %']}%</td>
                    <td>{close_trend}</td>
                    <td>{vol_trend}</td>
                    <td>{mini_c}</td>
                </tr>
            """
        html_table += "</tbody></table></div>"

        # Plotly chart
        chart_html = plotly_dashboard(df, symbol)

        # Combine full HTML
        full_html = summary_html + html_table + chart_html
        persist.save(key, full_html, "html")
        return full_html

    except Exception as e:
        return wrap_html(f"<h1>Error fetch_daily: {e}</h1><pre>{traceback.format_exc()}</pre>")
