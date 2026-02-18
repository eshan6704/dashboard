# stock.py — compact, merged, single-file (collision-safe)

import traceback
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime as dt
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.common import *

# Cache for ticker objects to avoid repeated API calls
_ticker_cache = {}

def get_ticker(symbol):
    """Get cached ticker object"""
    key = symbol.upper()
    if key not in _ticker_cache:
        _ticker_cache[key] = yf.Ticker(symbol + ".NS")
    return _ticker_cache[key]

def yfinfo(symbol):
    return get_ticker(symbol).info


def qresult(symbol):
    return yf.Ticker(symbol + ".NS").quarterly_financials


def result(symbol):
    return yf.Ticker(symbol + ".NS").financials


def balance(symbol):
    return get_ticker(symbol).balance_sheet


def cashflow(symbol):
    return get_ticker(symbol).cashflow


def dividend(symbol):
    return get_ticker(symbol).dividends.to_frame("Dividend")


def split(symbol):
    return get_ticker(symbol).splits.to_frame("Split")


def intraday(symbol):
    print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] yf called for {symbol}")
    return yf.download(symbol + ".NS", period="1d", interval="5m", progress=False).round(2)



# ================================================================
#                         INTRADAY
# ================================================================

def fetch_intraday(symbol, indicators=None):
    key = f"intraday_{symbol}"

    try:
        df = intraday(symbol)
        if df is None or df is False or df.empty:
            return wrap_html(f"<h1>No intraday data for {symbol}</h1>")

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Calculate intraday metrics
        df_display = df.copy()
        df_display.reset_index(inplace=True)
        
        # Add computed columns
        if 'Close' in df_display.columns and 'Open' in df_display.columns:
            df_display['Change%'] = ((df_display['Close'] - df_display['Open']) / df_display['Open'] * 100).round(2)
        
        if 'High' in df_display.columns and 'Low' in df_display.columns:
            df_display['Range%'] = ((df_display['High'] - df_display['Low']) / df_display['Close'] * 100).round(2)
        
        # Style positive/negative changes
        def style_change(val):
            if pd.isna(val):
                return val
            color = '#16a34a' if val > 0 else '#dc2626' if val < 0 else '#6b7280'
            return f'<span style="color:{color};font-weight:600;">{val:+.2f}%</span>'
        
        # Build summary stats
        latest = df_display.iloc[-1] if not df_display.empty else None
        if latest is not None and 'Close' in latest:
            day_high = df_display['High'].max() if 'High' in df_display.columns else 'N/A'
            day_low = df_display['Low'].min() if 'Low' in df_display.columns else 'N/A'
            day_open = df_display['Open'].iloc[0] if 'Open' in df_display.columns else 'N/A'
            day_close = latest['Close']
            day_change = ((day_close - day_open) / day_open * 100) if day_open != 'N/A' else 0
            
            stats_html = f"""
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px;">
                <div style="background:linear-gradient(135deg,#0f172a,#1e293b);color:white;padding:15px;border-radius:8px;text-align:center;">
                    <div style="font-size:12px;color:#94a3b8;">Open</div>
                    <div style="font-size:18px;font-weight:700;">₹{day_open:,.2f}</div>
                </div>
                <div style="background:linear-gradient(135deg,#0f172a,#1e293b);color:white;padding:15px;border-radius:8px;text-align:center;">
                    <div style="font-size:12px;color:#94a3b8;">Current</div>
                    <div style="font-size:18px;font-weight:700;">₹{day_close:,.2f}</div>
                </div>
                <div style="background:linear-gradient(135deg,#0f172a,#1e293b);color:white;padding:15px;border-radius:8px;text-align:center;">
                    <div style="font-size:12px;color:#94a3b8;">Day Range</div>
                    <div style="font-size:18px;font-weight:700;">₹{day_low:,.2f} - ₹{day_high:,.2f}</div>
                </div>
                <div style="background:linear-gradient(135deg,#0f172a,#1e293b);color:white;padding:15px;border-radius:8px;text-align:center;">
                    <div style="font-size:12px;color:#94a3b8;">Change</div>
                    <div style="font-size:18px;font-weight:700;color:{'#4ade80' if day_change >= 0 else '#f87171'};">{day_change:+.2f}%</div>
                </div>
            </div>
            """
        else:
            stats_html = ""

        # Mini intraday chart (last 50 points)
        chart_html = generate_intraday_chart(df.tail(50)) if len(df) > 0 else ""

        html = wrap_html(
            f"{stats_html}{chart_html}<h2 style='margin-top:20px;'>Last 50 Data Points</h2>{make_table(df_display)}",
            title=f"{symbol} Intraday Analysis"
        )

        return html

    except Exception as e:
        print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetch_intraday: {e}")
        return wrap_html(f"<h1>Error: {e}</h1>")


def generate_intraday_chart(df, width=800, height=250):
    """Generate SVG line chart for intraday data"""
    try:
        if df.empty or 'Close' not in df.columns:
            return ""
        
        closes = df['Close'].values
        n = len(closes)
        
        margin = 30
        chart_w = width - 2 * margin
        chart_h = height - 2 * margin
        
        min_p = np.min(closes)
        max_p = np.max(closes)
        range_p = max_p - min_p if max_p != min_p else 1
        
        # Generate points
        points = []
        for i, price in enumerate(closes):
            x = margin + (i / (n - 1)) * chart_w if n > 1 else margin + chart_w / 2
            y = margin + chart_h - ((price - min_p) / range_p * chart_h)
            points.append(f"{x:.1f},{y:.1f}")
        
        # Area fill
        area_points = f"{margin},{margin + chart_h} " + " ".join(points) + f" {margin + chart_w},{margin + chart_h}"
        
        svg = f"""
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:15px;margin-bottom:20px;">
            <div style="font-weight:600;margin-bottom:10px;color:#1e293b;">Intraday Price Movement</div>
            <svg width="{width}" height="{height}" style="background:#ffffff;border:1px solid #e2e8f0;border-radius:6px;">
                <defs>
                    <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stop-color="#3b82f6" stop-opacity="0.3"/>
                        <stop offset="100%" stop-color="#3b82f6" stop-opacity="0.05"/>
                    </linearGradient>
                </defs>
                <polygon points="{area_points}" fill="url(#areaGradient)"/>
                <polyline points="{' '.join(points)}" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <text x="{width-margin}" y="{margin-5}" font-size="11" fill="#3b82f6" text-anchor="end" font-weight="600">₹{closes[-1]:,.2f}</text>
                <text x="{margin}" y="{height-5}" font-size="9" fill="#64748b">{len(closes)} points</text>
            </svg>
        </div>
        """
        return svg
    except:
        return ""


# ================================================================
#                           DAILY
# ================================================================

def fetch_daily(symbol, period="1y"):
    """Fetch daily data with technical indicators and Nifty 50 comparison"""
    key = f"daily_{symbol}_{period}"
    
    try:
        # Fetch stock and index concurrently
        def fetch_stock_data():
            ticker = get_ticker(symbol)
            hist = ticker.history(period=period, interval="1d")
            info = ticker.info
            return hist, info
        
        def fetch_index_data():
            try:
                nifty = yf.Ticker("^NSEI")
                return nifty.history(period=period, interval="1d")
            except:
                return pd.DataFrame()
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            stock_future = executor.submit(fetch_stock_data)
            index_future = executor.submit(fetch_index_data)
            (hist, info), index_hist = stock_future.result(), index_future.result()
        
        if hist.empty:
            return wrap_html(f"<h1>No daily data for {symbol}</h1>")
        
        # Process data
        df = hist.copy()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Calculate technical indicators
        df = calculate_technical_indicators(df)
        
        # Reset index for display
        df_display = df.reset_index()
        
        # Format numbers
        numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'SMA20', 'SMA50', 'RSI']
        for col in numeric_cols:
            if col in df_display.columns:
                if col == 'Volume':
                    df_display[col] = df_display[col].apply(lambda x: format_large_number(x) if pd.notna(x) else x)
                else:
                    df_display[col] = df_display[col].round(2)
        
        # Build header with stock info
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))
        day_change = info.get('regularMarketChange', 0)
        day_change_pct = info.get('regularMarketChangePercent', 0)
        
        header = f"""
        <div style="background:linear-gradient(135deg,#0f172a,#1e293b);color:white;padding:20px;border-radius:12px;margin-bottom:20px;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <h1 style="margin:0;font-size:28px;">{info.get('longName', symbol)}</h1>
                    <p style="margin:5px 0 0 0;color:#94a3b8;">{symbol} • {info.get('sector', 'N/A')} • {info.get('industry', 'N/A')}</p>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:32px;font-weight:700;">₹{current_price:,.2f}</div>
                    <div style="color:{'#4ade80' if day_change >= 0 else '#f87171'};font-size:18px;font-weight:600;">
                        {day_change:+.2f} ({day_change_pct:+.2f}%)
                    </div>
                </div>
            </div>
        </div>
        """
        
        # Generate comparison chart with index
        comparison_chart = generate_comparison_chart(df, index_hist, symbol)
        
        # Key metrics cards
        metrics = calculate_key_metrics(df, info)
        metrics_html = build_metrics_cards(metrics)
        
        html = wrap_html(
            f"{header}{metrics_html}{comparison_chart}<h2 style='margin-top:20px;'>Historical Data</h2>{make_table(df_display)}",
            title=f"{symbol} Daily Analysis"
        )
        
        return html
        
    except Exception as e:
        print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetch_daily: {e}")
        return wrap_html(html_error(f"Daily Error: {e}"))


def calculate_technical_indicators(df):
    """Calculate SMA, RSI, and other indicators"""
    try:
        # Simple Moving Averages
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        df['SMA50'] = df['Close'].rolling(window=50).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Daily Change %
        df['Change%'] = df['Close'].pct_change() * 100
        
        # Volume vs Average
        df['Vol_vs_Avg'] = df['Volume'] / df['Volume'].rolling(20).mean()
        
    except Exception as e:
        print(f"Error calculating indicators: {e}")
    
    return df


def calculate_key_metrics(df, info):
    """Calculate key performance metrics"""
    metrics = {}
    
    try:
        if not df.empty and len(df) > 1:
            latest = df.iloc[-1]
            first = df.iloc[0]
            
            metrics['52w_high'] = df['High'].max()
            metrics['52w_low'] = df['Low'].min()
            metrics['current'] = latest['Close']
            metrics['ytd_return'] = (latest['Close'] / first['Close'] - 1) * 100
            metrics['volatility'] = df['Close'].pct_change().std() * np.sqrt(252) * 100
            metrics['avg_volume'] = df['Volume'].mean()
            
            # Position in 52w range
            metrics['range_position'] = (metrics['current'] - metrics['52w_low']) / (metrics['52w_high'] - metrics['52w_low']) * 100
            
    except Exception as e:
        print(f"Error calculating metrics: {e}")
    
    return metrics


def build_metrics_cards(metrics):
    """Build metric cards HTML"""
    if not metrics:
        return ""
    
    return f"""
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin-bottom:20px;">
        <div style="background:#f0fdf4;border:1px solid #16a34a;border-radius:10px;padding:15px;">
            <div style="font-size:12px;color:#64748b;">52W Range Position</div>
            <div style="font-size:20px;font-weight:700;color:#16a34a;">{metrics.get('range_position', 0):.1f}%</div>
            <div style="background:#e2e8f0;height:4px;border-radius:2px;margin-top:8px;">
                <div style="background:#16a34a;width:{min(metrics.get('range_position', 0), 100)}%;height:100%;border-radius:2px;"></div>
            </div>
        </div>
        <div style="background:#eff6ff;border:1px solid #3b82f6;border-radius:10px;padding:15px;">
            <div style="font-size:12px;color:#64748b;">Period Return</div>
            <div style="font-size:20px;font-weight:700;color:#3b82f6;">{metrics.get('ytd_return', 0):+.2f}%</div>
        </div>
        <div style="background:#fefce8;border:1px solid #eab308;border-radius:10px;padding:15px;">
            <div style="font-size:12px;color:#64748b;">Volatility (Annual)</div>
            <div style="font-size:20px;font-weight:700;color:#ca8a04;">{metrics.get('volatility', 0):.2f}%</div>
        </div>
        <div style="background:#faf5ff;border:1px solid #9333ea;border-radius:10px;padding:15px;">
            <div style="font-size:12px;color:#64748b;">Avg Volume</div>
            <div style="font-size:20px;font-weight:700;color:#9333ea;">{format_large_number(metrics.get('avg_volume', 0))}</div>
        </div>
    </div>
    """

def generate_comparison_chart(stock_df, index_df, symbol, width=800, height=300):
    """Generate normalized comparison chart between stock and Nifty 50"""
    try:
        if stock_df.empty or index_df.empty:
            return ""
        
        # Normalize both to 100 at start
        stock_norm = (stock_df['Close'] / stock_df['Close'].iloc[0]) * 100
        index_norm = (index_df['Close'] / index_df['Close'].iloc[0]) * 100
        
        # Align dates
        common_dates = stock_norm.index.intersection(index_norm.index)
        stock_norm = stock_norm.loc[common_dates]
        index_norm = index_norm.loc[common_dates]  # FIXED: was using [ instead of (
        
        if len(stock_norm) < 2:
            return ""
        
        n = len(stock_norm)
        margin = 40
        chart_w = width - 2 * margin
        chart_h = height - 2 * margin
        
        # Generate points for both lines
        min_val = min(stock_norm.min(), index_norm.min())
        max_val = max(stock_norm.max(), index_norm.max())
        range_val = max_val - min_val if max_val != min_val else 1
        
        stock_points = []
        index_points = []
        
        for i, (date, val) in enumerate(stock_norm.items()):
            x = margin + (i / (n - 1)) * chart_w if n > 1 else margin + chart_w / 2
            y = margin + chart_h - ((val - min_val) / range_val * chart_h)
            stock_points.append(f"{x:.1f},{y:.1f}")
        
        for i, (date, val) in enumerate(index_norm.items()):
            x = margin + (i / (n - 1)) * chart_w if n > 1 else margin + chart_w / 2
            y = margin + chart_h - ((val - min_val) / range_val * chart_h)
            index_points.append(f"{x:.1f},{y:.1f}")
        
        # Current values
        stock_current = stock_norm.iloc[-1]
        index_current = index_norm.iloc[-1]
        
        svg = f"""
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:15px;margin-bottom:20px;">
            <div style="font-weight:600;margin-bottom:10px;color:#1e293b;">{symbol} vs Nifty 50 (Normalized)</div>
            <svg width="{width}" height="{height}" style="background:#ffffff;border:1px solid #e2e8f0;border-radius:6px;">
                <polyline points="{' '.join(stock_points)}" fill="none" stroke="#3b82f6" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                <polyline points="{' '.join(index_points)}" fill="none" stroke="#f59e0b" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="5,5"/>
                <text x="{width-margin}" y="{margin-10}" font-size="12" fill="#3b82f6" text-anchor="end" font-weight="600">{symbol}: {stock_current:.1f}</text>
                <text x="{width-margin}" y="{margin+5}" font-size="12" fill="#f59e0b" text-anchor="end" font-weight="600">Nifty 50: {index_current:.1f}</text>
            </svg>
            <div style="display:flex;gap:20px;margin-top:10px;justify-content:center;">
                <div style="display:flex;align-items:center;gap:5px;">
                    <div style="width:20px;height:3px;background:#3b82f6;"></div>
                    <span style="font-size:12px;color:#64748b;">{symbol}</span>
                </div>
                <div style="display:flex;align-items:center;gap:5px;">
                    <div style="width:20px;height:3px;background:#f59e0b;border-top:2px dashed #f59e0b;"></div>
                    <span style="font-size:12px;color:#64748b;">Nifty 50</span>
                </div>
            </div>
        </div>
        """
        return svg
    except Exception as e:
        print(f"Error generating comparison chart: {e}")
        return ""
# ================================================================
#                        QUARTERLY
# ================================================================
# ================================================================
#                        QUARTERLY
# ================================================================

def fetch_qresult(symbol):
    key = f"qresult_{symbol}"

    try:
        df = qresult(symbol)
        if df.empty:
            return wrap_html(f"<h1>No quarterly results for {symbol}</h1>")

        df_display = df.copy()
        
        # Convert to numeric first, then format
        for col in df_display.columns:
            df_display[col] = pd.to_numeric(df_display[col], errors='coerce')
            df_display[col] = df_display[col].apply(
                lambda x: format_large_number(x) if pd.notna(x) and isinstance(x, (int, float)) else x
            )

        df_display.reset_index(inplace=True)
        
        # Add growth calculations - only if we have numeric columns
        numeric_cols = [c for c in df_display.columns if c != 'index' and pd.api.types.is_numeric_dtype(df_display[c])]
        
        if len(numeric_cols) >= 2:
            latest_col = numeric_cols[0]
            prev_col = numeric_cols[1]
            
            # Calculate growth only on numeric values
            def calc_growth(row):
                try:
                    latest = pd.to_numeric(row[latest_col], errors='coerce')
                    prev = pd.to_numeric(row[prev_col], errors='coerce')
                    if pd.notna(latest) and pd.notna(prev) and prev != 0:
                        growth = ((latest - prev) / abs(prev)) * 100
                        return round(growth, 2)
                    return None
                except:
                    return None
            
            growth_values = df_display.apply(calc_growth, axis=1)
            
            # Style growth column
            def style_growth(val):
                if pd.isna(val) or val is None:
                    return '-'
                color = '#16a34a' if val > 0 else '#dc2626'
                return f'<span style="color:{color};font-weight:600;">{val:+.2f}%</span>'
            
            df_display['QoQ Growth%'] = growth_values.apply(style_growth)

        html = wrap_html(
            f"<div style='background:#f0f9ff;border:1px solid #0ea5e9;border-radius:10px;padding:15px;margin-bottom:20px;'>"
            f"<div style='font-weight:600;color:#0c4a6e;'>📊 Quarterly Financial Results</div>"
            f"<div style='font-size:12px;color:#64748b;margin-top:5px;'>Showing QoQ comparison and growth metrics</div>"
            f"</div>{make_table(df_display)}", 
            title=f"{symbol} Quarterly Results"
        )

        return html

    except Exception as e:
        print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetch_qresult: {e}")
        import traceback
        print(traceback.format_exc())
        return wrap_html(html_error(f"Quarterly Error: {e}"))


# ================================================================
#                          ANNUAL
# ================================================================

def fetch_result(symbol):
    key = f"result_{symbol}"

    try:
        df = result(symbol)
        if df.empty:
            return wrap_html(f"<h1>No annual results for {symbol}</h1>")

        df_display = df.copy()
        
        # Convert to numeric first, then format
        for col in df_display.columns:
            df_display[col] = pd.to_numeric(df_display[col], errors='coerce')
            df_display[col] = df_display[col].apply(
                lambda x: format_large_number(x) if pd.notna(x) and isinstance(x, (int, float)) else x
            )

        df_display.reset_index(inplace=True)
        
        # Add YoY growth - only if we have numeric columns
        numeric_cols = [c for c in df_display.columns if c != 'index' and pd.api.types.is_numeric_dtype(df_display[c])]
        
        if len(numeric_cols) >= 2:
            latest_col = numeric_cols[0]
            prev_col = numeric_cols[1]
            
            def calc_growth(row):
                try:
                    latest = pd.to_numeric(row[latest_col], errors='coerce')
                    prev = pd.to_numeric(row[prev_col], errors='coerce')
                    if pd.notna(latest) and pd.notna(prev) and prev != 0:
                        growth = ((latest - prev) / abs(prev)) * 100
                        return round(growth, 2)
                    return None
                except:
                    return None
            
            growth_values = df_display.apply(calc_growth, axis=1)
            
            def style_growth(val):
                if pd.isna(val) or val is None:
                    return '-'
                color = '#16a34a' if val > 0 else '#dc2626'
                return f'<span style="color:{color};font-weight:600;">{val:+.2f}%</span>'
            
            df_display['YoY Growth%'] = growth_values.apply(style_growth)

        html = wrap_html(
            f"<div style='background:#f0fdf4;border:1px solid #16a34a;border-radius:10px;padding:15px;margin-bottom:20px;'>"
            f"<div style='font-weight:600;color:#14532d;'>📈 Annual Financial Results</div>"
            f"<div style='font-size:12px;color:#64748b;margin-top:5px;'>Showing YoY comparison and growth trends</div>"
            f"</div>{make_table(df_display)}", 
            title=f"{symbol} Annual Results"
        )

        return html

    except Exception as e:
        print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetch_result: {e}")
        import traceback
        print(traceback.format_exc())
        return wrap_html(html_error(f"Annual Error: {e}"))
# ================================================================
#                        BALANCE SHEET
# ================================================================

def fetch_balance(symbol):
    key = f"balance_{symbol}"

    try:
        df = balance(symbol)
        if df.empty:
            return wrap_html(f"<h1>No balance sheet for {symbol}</h1>")

        df_display = df.copy()
        for col in df_display.columns:
            df_display[col] = df_display[col].apply(
                lambda x: format_large_number(x) if isinstance(x, (int, float)) else x
            )

        df_display.reset_index(inplace=True)
        
        # Calculate key ratios if possible
        html = wrap_html(
            f"<div style='background:#faf5ff;border:1px solid #9333ea;border-radius:10px;padding:15px;margin-bottom:20px;'>"
            f"<div style='font-weight:600;color:#581c87;'>⚖️ Balance Sheet Overview</div>"
            f"<div style='font-size:12px;color:#64748b;margin-top:5px;'>Assets, liabilities and shareholders' equity</div>"
            f"</div>{make_table(df_display)}", 
            title=f"{symbol} Balance Sheet"
        )

        return html

    except Exception as e:
        print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetch_balance: {e}")
        return wrap_html(html_error(f"Balance Error: {e}"))


# ================================================================
#                          CASHFLOW
# ================================================================

def fetch_cashflow(symbol):
    key = f"cashflow_{symbol}"

    try:
        df = cashflow(symbol)
        if df.empty:
            return wrap_html(f"<h1>No cashflow for {symbol}</h1>")

        df_display = df.copy()
        for col in df_display.columns:
            df_display[col] = df_display[col].apply(
                lambda x: format_large_number(x) if isinstance(x, (int, float)) else x
            )

        df_display.reset_index(inplace=True)
        
        # Highlight free cash flow if available
        html = wrap_html(
            f"<div style='background:#fefce8;border:1px solid #eab308;border-radius:10px;padding:15px;margin-bottom:20px;'>"
            f"<div style='font-weight:600;color:#854d0e;'>💰 Cash Flow Statement</div>"
            f"<div style='font-size:12px;color:#64748b;margin-top:5px;'>Operating, investing and financing activities</div>"
            f"</div>{make_table(df_display)}", 
            title=f"{symbol} Cash Flow"
        )

        return html

    except Exception as e:
        print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetch_cashflow: {e}")
        return wrap_html(html_error(f"Cash Flow Error: {e}"))


# ================================================================
#                         DIVIDEND
# ================================================================

def fetch_dividend(symbol):
    key = f"dividend_{symbol}"

    try:
        df = dividend(symbol)
        if df.empty:
            return wrap_html(f"<h1>No dividend history for {symbol}</h1>")

        df_display = df.copy()
        df_display.reset_index(inplace=True)
        
        # Calculate dividend stats
        total_div = df_display['Dividend'].sum() if 'Dividend' in df_display.columns else 0
        avg_div = df_display['Dividend'].mean() if 'Dividend' in df_display.columns else 0
        latest_div = df_display['Dividend'].iloc[-1] if 'Dividend' in df_display.columns and not df_display.empty else 0
        
        stats_html = f"""
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:15px;margin-bottom:20px;">
            <div style="background:#eff6ff;border:1px solid #3b82f6;border-radius:10px;padding:15px;text-align:center;">
                <div style="font-size:12px;color:#64748b;">Latest Dividend</div>
                <div style="font-size:22px;font-weight:700;color:#3b82f6;">₹{latest_div:.2f}</div>
            </div>
            <div style="background:#f0fdf4;border:1px solid #16a34a;border-radius:10px;padding:15px;text-align:center;">
                <div style="font-size:12px;color:#64748b;">Average Dividend</div>
                <div style="font-size:22px;font-weight:700;color:#16a34a;">₹{avg_div:.2f}</div>
            </div>
            <div style="background:#faf5ff;border:1px solid #9333ea;border-radius:10px;padding:15px;text-align:center;">
                <div style="font-size:12px;color:#64748b;">Total (Period)</div>
                <div style="font-size:22px;font-weight:700;color:#9333ea;">₹{total_div:.2f}</div>
            </div>
        </div>
        """

        html = wrap_html(
            f"<div style='background:#eff6ff;border:1px solid #2563eb;border-radius:10px;padding:15px;margin-bottom:20px;'>"
            f"<div style='font-weight:600;color:#1e40af;'>💵 Dividend History</div>"
            f"<div style='font-size:12px;color:#64748b;margin-top:5px;'>Cash distributions to shareholders</div>"
            f"</div>{stats_html}{make_table(df_display)}", 
            title=f"{symbol} Dividends"
        )

        return html

    except Exception as e:
        print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetch_dividend: {e}")
        return wrap_html(html_error(f"Dividend Error: {e}"))


# ================================================================
#                            SPLIT
# ================================================================

def fetch_split(symbol):
    key = f"split_{symbol}"

    try:
        df = split(symbol)
        if df.empty:
            return wrap_html(f"<h1>No splits for {symbol}</h1>")

        df_display = df.copy()
        df_display.reset_index(inplace=True)
        
        # Add split ratio description
        if 'Split' in df_display.columns:
            df_display['Ratio'] = df_display['Split'].apply(lambda x: f"{int(x)}:1" if x >= 1 else f"1:{int(1/x)}")

        html = wrap_html(
            f"<div style='background:#f0fdf4;border:1px solid #16a34a;border-radius:10px;padding:15px;margin-bottom:20px;'>"
            f"<div style='font-weight:600;color:#14532d;'>✂️ Stock Splits History</div>"
            f"<div style='font-size:12px;color:#64748b;margin-top:5px;'>Historical share splits and ratios</div>"
            f"</div>{make_table(df_display)}", 
            title=f"{symbol} Splits"
        )

        return html

    except Exception as e:
        print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetch_split: {e}")
        return wrap_html(html_error(f"Split Error: {e}"))


# ================================================================
#                           EARNINGS
# ================================================================

def fetch_other(symbol):
    key = f"other_{symbol}"

    try:
        ticker = get_ticker(symbol)
        df = ticker.earnings

        if df is None or df.empty:
            return wrap_html(f"<h1>No earnings data for {symbol}</h1>")

        df_display = df.copy()
        df_display.reset_index(inplace=True)
        
        # Add growth if possible
        if len(df_display) > 1 and 'Earnings' in df_display.columns:
            df_display['YoY Growth%'] = df_display['Earnings'].pct_change() * 100
            df_display['YoY Growth%'] = df_display['YoY Growth%'].round(2)

        html = wrap_html(
            f"<div style='background:#fef2f2;border:1px solid #dc2626;border-radius:10px;padding:15px;margin-bottom:20px;'>"
            f"<div style='font-weight:600;color:#991b1b;'>📊 Earnings Overview</div>"
            f"<div style='font-size:12px;color:#64748b;margin-top:5px;'>Revenue and earnings trends</div>"
            f"</div>{make_table(df_display)}", 
            title=f"{symbol} Earnings"
        )

        return html

    except Exception as e:
        print(f"[{dt.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetch_other: {e}")
        return wrap_html(html_error(f"Earnings Error: {e}"))