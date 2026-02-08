# ==============================
# FULL PAGE OPTIMIZED FOR HF SPACES
# ==============================
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
from functools import lru_cache
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
import html

# ==============================
# Configuration
# ==============================
CACHE_MAXSIZE = 128
MAX_WORKERS = 2  # HF Spaces friendly
HISTORY_PERIOD = "70d"  # Min needed for 200 DMA

# ==============================
# Icons & Styling
# ==============================
MAIN_ICONS = {
    "Price / Volume": "📊",
    "Fundamentals": "📈",
    "Technicals": "⚡",
    "Signals": "🎯",
    "Company Profile": "🏢",
    "Management": "👔",
    "Events": "📅",
    "Ownership": "🤝",
    "Analyst": "📉",
    "Risk": "🛡️",
    "Splits": "✂️",
    "Dividends": "💰",
    "Earnings": "📢",
    "Trend": "📉"
}

SHORT_NAMES = {
    # Price & Volume
    "regularMarketPrice": "Price",
    "regularMarketChange": "Chg",
    "regularMarketChangePercent": "Chg%",
    "regularMarketPreviousClose": "Prev Close",
    "regularMarketOpen": "Open",
    "regularMarketDayHigh": "High",
    "regularMarketDayLow": "Low",
    "regularMarketVolume": "Volume",
    "averageDailyVolume10Day": "Avg Vol 10D",
    "averageDailyVolume3Month": "Avg Vol 3M",
    "fiftyDayAverage": "50 DMA",
    "twoHundredDayAverage": "200 DMA",
    "fiftyTwoWeekLow": "52W Low",
    "fiftyTwoWeekHigh": "52W High",
    "fiftyTwoWeekChange": "52W Chg%",
    "fiftyDayAverageChangePercent": "50DMA Chg%",
    "twoHundredDayAverageChangePercent": "200DMA Chg%",
    "vs50DMA": "vs 50DMA",
    "vs200DMA": "vs 200DMA",
    "52WPos": "52W Position",
    
    # Volume Spikes
    "volumeSpike": "Vol Spike (1D/10D)",
    "volumeSpikeTrend": "Vol Trend (11D/30D)",
    "relativeVolume": "Rel Volume",
    "volumeVsAvg3M": "Vol vs 3M Avg",
    
    # Valuation
    "marketCap": "Market Cap",
    "enterpriseValue": "Enterprise Value",
    "trailingPE": "P/E (TTM)",
    "forwardPE": "Forward P/E",
    "priceToBook": "P/B",
    "priceToSalesTrailing12Months": "P/S",
    "trailingPegRatio": "PEG Ratio",
    "enterpriseToRevenue": "EV/Revenue",
    "enterpriseToEbitda": "EV/EBITDA",
    
    # Profitability
    "returnOnEquity": "ROE",
    "returnOnAssets": "ROA",
    "returnOnCapitalEmployed": "ROCE",
    "profitMargins": "Profit Margin",
    "operatingMargins": "Operating Margin",
    "ebitdaMargins": "EBITDA Margin",
    "grossMargins": "Gross Margin",
    
    # Financial Health
    "debtToEquity": "Debt/Equity",
    "currentRatio": "Current Ratio",
    "quickRatio": "Quick Ratio",
    "totalCash": "Total Cash",
    "totalDebt": "Total Debt",
    "totalCashPerShare": "Cash/Share",
    "netDebt": "Net Debt",
    
    # Income & Growth
    "totalRevenue": "Revenue",
    "revenuePerShare": "Revenue/Share",
    "earningsPerShare": "EPS (TTM)",
    "forwardEps": "Forward EPS",
    "trailingEps": "Trailing EPS",
    "revenueGrowth": "Revenue Growth",
    "earningsGrowth": "Earnings Growth",
    "earningsQuarterlyGrowth": "Quarterly EPS Growth",
    "revenueQuarterlyGrowth": "Quarterly Rev Growth",
    
    # Dividends
    "dividendYield": "Div Yield",
    "dividendRate": "Div Rate",
    "payoutRatio": "Payout Ratio",
    "fiveYearAvgDividendYield": "5Y Avg Div Yield",
    "trailingAnnualDividendRate": "Trailing Div",
    "trailingAnnualDividendYield": "Trailing Div Yield",
    "exDividendDate": "Ex-Div Date",
    "dividendDate": "Div Date",
    "lastDividendValue": "Last Div",
    "lastDividendDate": "Last Div Date",
    
    # Splits
    "lastSplitFactor": "Last Split",
    "lastSplitDate": "Split Date",
    
    # Company Info
    "sector": "Sector",
    "industry": "Industry",
    "country": "Country",
    "employees": "Employees",
    "website": "Website",
    "phone": "Phone",
    "address1": "Address",
    "city": "City",
    "state": "State",
    "zip": "ZIP",
    "longBusinessSummary": "Business Summary",
    
    # Ownership
    "heldPercentInsiders": "Insider Ownership",
    "heldPercentInstitutions": "Institutional Ownership",
    "sharesOutstanding": "Shares Outstanding",
    "floatShares": "Float",
    "sharesShort": "Short Interest",
    "shortRatio": "Short Ratio",
    "shortPercentOfFloat": "Short % of Float",
    "shortPercentOfSharesOutstanding": "Short % Outstanding",
    
    # Analyst
    "recommendationKey": "Rating",
    "recommendationMean": "Rating Mean",
    "numberOfAnalystOpinions": "Analysts Count",
    "targetHighPrice": "Target High",
    "targetLowPrice": "Target Low",
    "targetMeanPrice": "Target Mean",
    "targetMedianPrice": "Target Median",
    
    # Risk & Beta
    "beta": "Beta",
    "overallRisk": "Overall Risk",
    "auditRisk": "Audit Risk",
    "boardRisk": "Board Risk",
    "compensationRisk": "Comp Risk",
    "shareHolderRightsRisk": "SH Rights Risk",
    
    # Technicals
    "rsi": "RSI(14)",
    "macd": "MACD",
    "signal": "Signal",
    "momentum_10d": "10D Momentum",
    "momentum_20d": "20D Momentum",
    "volatility_20d": "20D Volatility",
    "adr": "ADR%",
    
    # Other
    "currency": "Currency",
    "exchange": "Exchange",
    "shortName": "Short Name",
    "longName": "Full Name"
}

NOISE_KEYS = {
    "maxAge", "priceHint", "triggerable", "customPriceAlertConfidence",
    "sourceInterval", "exchangeDataDelayedBy", "esgPopulated", "cryptoTradeable",
    "firstTradeDateMilliseconds", "timeZoneFullName", "timeZoneShortName",
    "uuid", "messageBoardId", "gmtOffSetMilliseconds", "exchangeTimezoneName",
    "preMarketTime", "postMarketTime", "marketState", "quoteType", "symbol",
    "underlyingSymbol", "financialCurrency", "market", "history", "dataGranularity",
    "range", "scale", "validRanges", "validIntervals", "instrumentType"
}

# ==============================
# Utility Functions
# ==============================
def human_number(n):
    try:
        n = float(n)
        if abs(n) >= 1e9: return f"{n/1e9:.2f}B"
        if abs(n) >= 1e7: return f"{n/1e7:.2f}Cr"
        if abs(n) >= 1e5: return f"{n/1e5:.2f}L"
        if abs(n) >= 1e3: return f"{n/1e3:.2f}K"
        return f"{n:,.2f}"
    except:
        return str(n)

def format_value(k, v):
    """Fast formatting without heavy pandas"""
    if v is None or v == "":
        return "-"
    
    lk = k.lower()
    
    # Handle percentages
    if any(x in lk for x in ["percent", "yield", "margin", "ratio", "growth", "change", "spike", "short", "insider", "institution", "payout", "roe", "roa", "roce", "adr", "volatility", "beta", "risk", "position"]):
        try:
            v = float(v)
            cls = "pos" if v > 0 else "neg" if v < 0 else ""
            sign = "+" if v > 0 else ""
            return f'<span class="{cls}">{sign}{v:.2f}%</span>'
        except:
            return str(v)
    
    # Handle currency
    if any(x in lk for x in ["cap", "value", "price", "cash", "debt", "revenue", "income", "ebitda", "target", "book", "sales", "assets"]):
        try:
            v = float(v)
            return f"₹{human_number(v)}"
        except:
            return str(v)
    
    # Handle dates
    if isinstance(v, (int, float)) and v > 1e9:
        try:
            if v > 1e12: v = v / 1000
            dt = datetime.fromtimestamp(v, tz=timezone.utc)
            return dt.strftime("%d %b %Y")
        except:
            pass
    
    # Escape HTML to prevent XSS
    if isinstance(v, str):
        return html.escape(v[:500])  # Limit length
    
    return str(v)

# ==============================
# Optimized Data Fetching
# ==============================
@lru_cache(maxsize=CACHE_MAXSIZE)
def get_cached_info(symbol: str):
    """Cache ticker info"""
    try:
        t = yf.Ticker(symbol)
        return t.info
    except:
        return None

def fetch_all_data(symbol: str):
    """Fetch all data concurrently"""
    ticker_symbol = symbol + ".NS"
    
    def fetch_info():
        try:
            t = yf.Ticker(ticker_symbol)
            return t.info
        except Exception as e:
            return {"__error__": str(e)}
    
    def fetch_history():
        try:
            t = yf.Ticker(ticker_symbol)
            hist = t.history(period=HISTORY_PERIOD, interval="1d", auto_adjust=True)
            return hist if isinstance(hist, pd.DataFrame) else pd.DataFrame()
        except:
            return pd.DataFrame()
    
    def fetch_actions():
        try:
            t = yf.Ticker(ticker_symbol)
            actions = t.actions
            return actions if isinstance(actions, pd.DataFrame) else pd.DataFrame()
        except:
            return pd.DataFrame()
    
    def fetch_calendar():
        try:
            t = yf.Ticker(ticker_symbol)
            cal = t.calendar
            return cal if isinstance(cal, pd.DataFrame) else pd.DataFrame()
        except:
            return pd.DataFrame()
    
    def fetch_recommendations():
        try:
            t = yf.Ticker(ticker_symbol)
            rec = t.recommendations
            return rec if isinstance(rec, pd.DataFrame) else pd.DataFrame()
        except:
            return pd.DataFrame()
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(fetch_info): 'info',
            executor.submit(fetch_history): 'hist',
            executor.submit(fetch_actions): 'actions',
            executor.submit(fetch_calendar): 'calendar',
            executor.submit(fetch_recommendations): 'recs'
        }
        
        results = {}
        for future in as_completed(futures):
            key = futures[future]
            try:
                results[key] = future.result()
            except:
                results[key] = pd.DataFrame() if key != 'info' else {}
    
    return (results.get('info', {}), results.get('hist', pd.DataFrame()),
            results.get('actions', pd.DataFrame()), results.get('calendar', pd.DataFrame()),
            results.get('recs', pd.DataFrame()))

# ==============================
# Vectorized Calculations
# ==============================
def calculate_metrics(info: dict, hist: pd.DataFrame):
    """All calculations in one vectorized pass"""
    if hist.empty or len(hist) < 20:
        return {}, {}, {}
    
    # Ensure numeric
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        if col in hist.columns:
            hist[col] = pd.to_numeric(hist[col], errors='coerce')
    
    hist = hist.dropna()
    if len(hist) < 20:
        return {}, {}, {}
    
    closes = hist['Close'].values
    volumes = hist['Volume'].values if 'Volume' in hist.columns else np.array([])
    n = len(closes)
    
    price_metrics = {}
    tech_metrics = {}
    volume_metrics = {}
    
    price = info.get("regularMarketPrice")
    if price and isinstance(price, (int, float)):
        price = float(price)
        
        # Moving averages
        if n >= 50:
            ma50 = np.mean(closes[-50:])
            price_metrics["fiftyDayAverage"] = round(ma50, 2)
            price_metrics["fiftyDayAverageChangePercent"] = round((price/ma50 - 1)*100, 2)
            price_metrics["vs50DMA"] = "Above ↑" if price > ma50 else "Below ↓"
        
        if n >= 60:  # Use available data for 200 MA
            ma200 = np.mean(closes[-min(200, n):])
            price_metrics["twoHundredDayAverage"] = round(ma200, 2)
            price_metrics["twoHundredDayAverageChangePercent"] = round((price/ma200 - 1)*100, 2)
            price_metrics["vs200DMA"] = "Above ↑" if price > ma200 else "Below ↓"
        
        # 52-week range from available data
        if n >= 60:
            high_52w = np.max(closes)
            low_52w = np.min(closes)
            price_metrics["fiftyTwoWeekHigh"] = round(high_52w, 2)
            price_metrics["fiftyTwoWeekLow"] = round(low_52w, 2)
            if high_52w != low_52w:
                price_metrics["52WPos"] = round((price - low_52w)/(high_52w - low_52w)*100, 1)
    
    # Volume metrics
    if len(volumes) >= 10:
        today_vol = info.get("regularMarketVolume") or info.get("volume")
        if today_vol and isinstance(today_vol, (int, float)):
            today_vol = float(today_vol)
            avg_10d = np.mean(volumes[-10:])
            if avg_10d > 0:
                volume_metrics["volumeSpike"] = round((today_vol/avg_10d - 1)*100, 2)
                volume_metrics["relativeVolume"] = round(today_vol/avg_10d, 2)
            
            if len(volumes) >= 30:
                avg_30d = np.mean(volumes[-30:])
                if avg_30d > 0:
                    volume_metrics["volumeVsAvg3M"] = round((today_vol/avg_30d - 1)*100, 2)
    
    # Technicals
    if n >= 15:
        deltas = np.diff(closes)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        avg_gain = np.mean(gains[-14:])
        avg_loss = np.mean(losses[-14:])
        if avg_loss == 0:
            rsi = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        tech_metrics["rsi"] = round(rsi, 2)
    
    if n >= 26:
        ema12 = pd.Series(closes).ewm(span=12, adjust=False).mean().values
        ema26 = pd.Series(closes).ewm(span=26, adjust=False).mean().values
        tech_metrics["macd"] = round(ema12[-1] - ema26[-1], 2)
        signal = pd.Series(ema12 - ema26).ewm(span=9, adjust=False).mean().values[-1]
        tech_metrics["signal"] = round(signal, 2)
    
    if n >= 10:
        tech_metrics["momentum_10d"] = round((closes[-1]/closes[-10] - 1)*100, 2)
    if n >= 20:
        tech_metrics["momentum_20d"] = round((closes[-1]/closes[-20] - 1)*100, 2)
        returns = np.diff(closes[-21:]) / closes[-21:-1]
        tech_metrics["volatility_20d"] = round(np.std(returns) * np.sqrt(252) * 100, 2)
    
    if all(c in hist.columns for c in ['High', 'Low']):
        highs = hist['High'].values[-20:]
        lows = hist['Low'].values[-20:]
        tech_metrics["adr"] = round(np.mean((highs - lows)/closes[-20:] * 100), 2)
    
    return price_metrics, volume_metrics, tech_metrics

# ==============================
# HTML Builders (Optimized)
# ==============================
def build_card(title: str, content: str, icon: str = "", color: str = "blue"):
    colors = {
        "blue": ("#eff6ff", "#3b82f6"),
        "green": ("#f0fdf4", "#16a34a"),
        "yellow": ("#fefce8", "#eab308"),
        "red": ("#fef2f2", "#dc2626"),
        "purple": ("#faf5ff", "#9333ea"),
        "dark": ("#0f172a", "#1e293b")
    }
    bg, border = colors.get(color, ("#f8fafc", "#e2e8f0"))
    
    return f"""
    <div style="background:{bg};border:1px solid {border};border-radius:10px;padding:14px;margin-bottom:12px;box-shadow:0 1px 3px rgba(0,0,0,0.1);">
        <div style="font-weight:700;margin-bottom:10px;color:#1e293b;font-size:15px;border-bottom:1px solid {border};padding-bottom:6px;">
            {icon} {title}
        </div>
        {content}
    </div>
    """

def build_table(data: dict, fields: list = None):
    """Build HTML table without pandas"""
    if not data:
        return "<div style='color:#64748b;font-size:12px;'>No data available</div>"
    
    rows = []
    for k, v in data.items():
        if fields and k not in fields:
            continue
        if v is None or v == "":
            continue
        
        label = SHORT_NAMES.get(k, k[:25])
        formatted = format_value(k, v)
        
        rows.append(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #e2e8f0;padding:6px 0;">
            <span style="color:#64748b;font-size:12px;">{label}</span>
            <span style="font-weight:600;color:#0f172a;font-size:13px;">{formatted}</span>
        </div>
        """)
    
    return "".join(rows) if rows else "<div style='color:#64748b;font-size:12px;'>No data available</div>"

def build_grid(cards: list, cols: int = 3):
    return f"""
    <style>
        .grid{{display:grid;gap:12px;grid-template-columns:repeat({cols},1fr);}}
        @media(max-width:1200px){{.grid{{grid-template-columns:repeat(2,1fr);}}}}
        @media(max-width:768px){{.grid{{grid-template-columns:1fr;}}}}
        .pos{{color:#16a34a;font-weight:700;}}
        .neg{{color:#dc2626;font-weight:700;}}
    </style>
    <div class="grid">{''.join(cards)}</div>
    """

def build_mini_chart(hist: pd.DataFrame):
    """Generate mini line chart SVG"""
    if hist.empty or len(hist) < 20:
        return ""
    
    try:
        closes = hist['Close'].values[-30:]
        n = len(closes)
        min_p, max_p = np.min(closes), np.max(closes)
        range_p = max_p - min_p if max_p != min_p else 1
        
        points = []
        for i, price in enumerate(closes):
            x = 20 + (i / (n-1)) * 260
            y = 130 - ((price - min_p) / range_p) * 110
            points.append(f"{x:.1f},{y:.1f}")
        
        return f"""
        <svg width="300" height="150" style="background:#fafafa;border:1px solid #e2e8f0;border-radius:6px;">
            <polyline points="{' '.join(points)}" fill="none" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <text x="280" y="20" font-size="11" fill="#2563eb" text-anchor="end" font-weight="bold">{closes[-1]:.2f}</text>
            <text x="20" y="145" font-size="9" fill="#64748b">{len(closes)} days</text>
        </svg>
        """
    except:
        return ""

def build_signals(info: dict, price_m: dict, tech_m: dict, vol_m: dict):
    """Build trading signals"""
    signals = []
    
    # Valuation
    pe = info.get("trailingPE")
    if isinstance(pe, (int, float)):
        pe = float(pe)
        if pe < 15:
            signals.append(("Valuation", "Buy", f"P/E {pe:.1f}x (Undervalued)", "pos"))
        elif pe > 30:
            signals.append(("Valuation", "Avoid", f"P/E {pe:.1f}x (Overvalued)", "neg"))
        else:
            signals.append(("Valuation", "Hold", f"P/E {pe:.1f}x (Fair)", ""))
    
    # Trend
    if "vs50DMA" in price_m and "vs200DMA" in price_m:
        if price_m["vs50DMA"].startswith("Above") and price_m["vs200DMA"].startswith("Above"):
            signals.append(("Trend", "Bullish", "Above 50/200 DMA", "pos"))
        elif price_m["vs50DMA"].startswith("Below") and price_m["vs200DMA"].startswith("Below"):
            signals.append(("Trend", "Bearish", "Below 50/200 DMA", "neg"))
    
    # Quality
    roe = info.get("returnOnEquity")
    if isinstance(roe, (int, float)) and roe > 0.15:
        signals.append(("Quality", "Strong", f"ROE {float(roe)*100:.1f}%", "pos"))
    
    # Volume
    spike = vol_m.get("volumeSpike")
    if isinstance(spike, (int, float)) and spike > 50:
        signals.append(("Volume", "Spike", f"+{float(spike):.0f}% vs avg", "pos"))
    
    # RSI
    rsi = tech_m.get("rsi")
    if isinstance(rsi, (int, float)):
        rsi = float(rsi)
        if rsi > 70:
            signals.append(("RSI", "Overbought", f"RSI {rsi:.1f}", "neg"))
        elif rsi < 30:
            signals.append(("RSI", "Oversold", f"RSI {rsi:.1f}", "pos"))
    
    if not signals:
        return ""
    
    rows = "".join([
        f'<div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #e2e8f0;padding:8px 0;">'
        f'<div><div style="font-weight:600;">{s[0]}</div><div style="font-size:11px;color:#64748b;">{s[2]}</div></div>'
        f'<span class="{s[3]}">{s[1]}</span></div>'
        for s in signals
    ])
    
    return build_card("Trading Signals", rows, MAIN_ICONS["Signals"], "yellow")

def build_events(info: dict, actions: pd.DataFrame, calendar: pd.DataFrame):
    """Build corporate events timeline"""
    events = []
    
    # Earnings
    if not calendar.empty and 'Earnings Date' in calendar.columns:
        for date in calendar['Earnings Date'].dropna()[:2]:
            events.append(("earnings", date, "Earnings Release", "📢"))
    
    # Dividends from actions
    if not actions.empty and 'Dividends' in actions.columns:
        divs = actions[actions['Dividends'] > 0]['Dividends'].tail(3)
        for date, amt in divs.items():
            events.append(("dividend", date, f"Dividend ₹{float(amt):.2f}", "💰"))
    
    # Splits from actions
    if not actions.empty and 'Stock Splits' in actions.columns:
        splits = actions[actions['Stock Splits'] != 0]['Stock Splits'].tail(2)
        for date, ratio in splits.items():
            events.append(("split", date, f"Split {float(ratio)}:1", "✂️"))
    
    if not events:
        return ""
    
    # Sort by date
    events.sort(key=lambda x: x[1] if hasattr(x[1], 'strftime') else datetime.now(), reverse=True)
    
    colors = {"earnings": "#fefce8", "dividend": "#eff6ff", "split": "#f0fdf4"}
    borders = {"earnings": "#eab308", "dividend": "#2563eb", "split": "#16a34a"}
    
    html = ""
    for typ, date, title, icon in events[:6]:
        date_str = date.strftime("%d %b %Y") if hasattr(date, 'strftime') else str(date)[:10]
        html += f"""
        <div style="background:{colors[typ]};border-left:3px solid {borders[typ]};padding:8px 12px;margin:6px 0;border-radius:4px;">
            <div style="display:flex;justify-content:space-between;font-size:12px;">
                <span style="font-weight:600;">{icon} {title}</span>
                <span style="color:#64748b;">{date_str}</span>
            </div>
        </div>
        """
    
    return build_card("Corporate Events", html, MAIN_ICONS["Events"], "yellow")

# ==============================
# Section Builders
# ==============================
def build_price_volume_section(info: dict, hist: pd.DataFrame, price_m: dict, vol_m: dict, tech_m: dict):
    """Build price/volume section"""
    # Base data
    base = {
        "regularMarketPrice": info.get("regularMarketPrice"),
        "regularMarketChange": info.get("regularMarketChange"),
        "regularMarketChangePercent": info.get("regularMarketChangePercent"),
        "regularMarketPreviousClose": info.get("regularMarketPreviousClose"),
        "regularMarketOpen": info.get("regularMarketOpen"),
        "regularMarketDayHigh": info.get("regularMarketDayHigh"),
        "regularMarketDayLow": info.get("regularMarketDayLow"),
        "regularMarketVolume": info.get("regularMarketVolume"),
    }
    
    # Merge with calculated metrics
    all_data = {**base, **price_m, **vol_m, **tech_m}
    
    # Create cards
    cards = []
    
    # Live Trading
    live_fields = ["regularMarketPrice", "regularMarketChange", "regularMarketChangePercent", 
                   "regularMarketPreviousClose", "regularMarketOpen"]
    live_data = {k: all_data.get(k) for k in live_fields if all_data.get(k) is not None}
    if live_data:
        cards.append(build_card("Live Trading", build_table(live_data), "", "blue"))
    
    # Day's Range
    range_fields = ["regularMarketDayHigh", "regularMarketDayLow", "fiftyTwoWeekHigh", 
                    "fiftyTwoWeekLow", "52WPos"]
    range_data = {k: all_data.get(k) for k in range_fields if all_data.get(k) is not None}
    if range_data:
        # Add progress bar for 52W position
        extra = ""
        if "52WPos" in range_data:
            pos = float(range_data["52WPos"])
            extra = f'<div style="background:#e2e8f0;height:6px;border-radius:3px;margin-top:8px;"><div style="background:#0ea5e9;width:{min(pos,100)}%;height:100%;border-radius:3px;"></div></div>'
        cards.append(build_card("Range Analysis", build_table(range_data) + extra, "", "green"))
    
    # Volume
    vol_fields = ["regularMarketVolume", "volumeSpike", "relativeVolume", "volumeVsAvg3M"]
    vol_data = {k: all_data.get(k) for k in vol_fields if all_data.get(k) is not None}
    if vol_data:
        cards.append(build_card("Volume Analysis", build_table(vol_data), "", "purple"))
    
    # Moving Averages
    ma_fields = ["fiftyDayAverage", "twoHundredDayAverage", "fiftyDayAverageChangePercent", 
                 "twoHundredDayAverageChangePercent", "vs50DMA", "vs200DMA"]
    ma_data = {k: all_data.get(k) for k in ma_fields if all_data.get(k) is not None}
    if ma_data:
        cards.append(build_card("Moving Averages", build_table(ma_data), "", "yellow"))
    
    # Technicals
    tech_fields = ["rsi", "macd", "signal", "momentum_10d", "momentum_20d", "volatility_20d", "adr"]
    tech_data = {k: all_data.get(k) for k in tech_fields if all_data.get(k) is not None}
    if tech_data:
        cards.append(build_card("Technical Indicators", build_table(tech_data), "", "red"))
    
    return build_grid(cards, cols=3)

def build_fundamentals_section(info: dict):
    """Build fundamentals section"""
    groups = {
        "Valuation": ["marketCap", "enterpriseValue", "trailingPE", "forwardPE", "priceToBook", 
                      "priceToSalesTrailing12Months", "trailingPegRatio", "enterpriseToRevenue", "enterpriseToEbitda"],
        "Profitability": ["returnOnEquity", "returnOnAssets", "returnOnCapitalEmployed", 
                         "profitMargins", "operatingMargins", "ebitdaMargins", "grossMargins"],
        "Financial Health": ["debtToEquity", "currentRatio", "quickRatio", "totalCash", 
                            "totalDebt", "totalCashPerShare"],
        "Income": ["totalRevenue", "revenuePerShare", "earningsPerShare", "forwardEps", "trailingEps"],
        "Growth": ["revenueGrowth", "earningsGrowth", "earningsQuarterlyGrowth", "revenueQuarterlyGrowth"]
    }
    
    cards = []
    for title, fields in groups.items():
        data = {k: info.get(k) for k in fields if info.get(k) is not None}
        if data:
            cards.append(build_card(title, build_table(data), "", "blue"))
    
    return build_grid(cards, cols=3) if cards else ""

def build_dividend_section(info: dict):
    """Build dividend section"""
    fields = ['dividendYield', 'dividendRate', 'payoutRatio', 'fiveYearAvgDividendYield',
              'trailingAnnualDividendRate', 'exDividendDate', 'dividendDate']
    data = {k: info.get(k) for k in fields if info.get(k) is not None}
    
    if not data:
        return ""
    
    return build_card("Dividend Analysis", build_table(data), MAIN_ICONS["Dividends"], "blue")

def build_ownership_section(info: dict):
    """Build ownership section"""
    fields = ['heldPercentInsiders', 'heldPercentInstitutions', 'sharesOutstanding', 
              'floatShares', 'sharesShort', 'shortRatio', 'shortPercentOfFloat']
    data = {k: info.get(k) for k in fields if info.get(k) is not None}
    
    if not data:
        return ""
    
    return build_card("Ownership Structure", build_table(data), MAIN_ICONS["Ownership"], "purple")

def build_analyst_section(info: dict, recs: pd.DataFrame):
    """Build analyst section"""
    fields = ['recommendationKey', 'recommendationMean', 'numberOfAnalystOpinions',
              'targetHighPrice', 'targetLowPrice', 'targetMeanPrice', 'targetMedianPrice']
    data = {k: info.get(k) for k in fields if info.get(k) is not None}
    
    html = build_table(data)
    
    # Add recent recommendations
    if not recs.empty and 'To Grade' in recs.columns and len(recs) > 0:
        html += "<div style='margin-top:10px;font-weight:600;border-top:1px solid #e2e8f0;padding-top:8px;'>Recent Ratings:</div>"
        recent = recs.tail(5)
        for idx, row in recent.iterrows():
            date = idx.strftime("%d %b") if hasattr(idx, 'strftime') else str(idx)[:10]
            grade = row.get('To Grade', 'N/A')
            html += f"<div style='font-size:12px;padding:3px 0;'>{date}: <strong>{grade}</strong></div>"
    
    return build_card("Analyst Coverage", html, MAIN_ICONS["Analyst"], "purple")

def build_risk_section(info: dict):
    """Build risk section"""
    fields = ['beta', 'overallRisk', 'auditRisk', 'boardRisk', 'compensationRisk', 'shareHolderRightsRisk']
    data = {k: info.get(k) for k in fields if info.get(k) is not None}
    
    if not data:
        return ""
    
    return build_card("Risk Metrics", build_table(data), MAIN_ICONS["Risk"], "red")

def build_profile_section(info: dict):
    """Build company profile"""
    # Short info
    short_fields = ['sector', 'industry', 'country', 'employees', 'website', 'phone']
    short_data = {k: info.get(k) for k in short_fields if info.get(k)}
    
    html = ""
    if short_data:
        html += build_card("Company Info", build_table(short_data), "", "blue")
    
    # Business summary
    summary = info.get("longBusinessSummary")
    if summary:
        summary_html = f'<div style="font-size:13px;line-height:1.6;color:#374151;max-height:200px;overflow-y:auto;padding:10px;background:#f8fafc;border-radius:6px;">{html.escape(str(summary)[:1000])}</div>'
        html += build_card("Business Summary", summary_html, "", "green")
    
    return html

# ==============================
# Main Function
# ==============================
def fetch_info(symbol: str):
    try:
        # Fetch all data concurrently
        info, hist, actions, calendar, recs = fetch_all_data(symbol)
        
        if "__error__" in info:
            return f'<div style="color:#dc2626;padding:20px;">Error: {info["__error__"]}</div>'
        
        # Calculate all metrics
        price_m, vol_m, tech_m = calculate_metrics(info, hist)
        
        # Build header
        name = info.get("longName") or info.get("shortName") or symbol
        price = float(info.get("regularMarketPrice", 0) or 0)
        change = float(info.get("regularMarketChange", 0) or 0)
        change_pct = float(info.get("regularMarketChangePercent", 0) or 0)
        currency = info.get("currency", "₹")
        
        # Market time
        market_time = info.get("regularMarketTime")
        time_str = ""
        if market_time and isinstance(market_time, (int, float)):
            try:
                if market_time > 1e12: market_time = market_time / 1000
                dt_utc = datetime.fromtimestamp(market_time, tz=timezone.utc)
                dt_ist = dt_utc + timedelta(hours=5, minutes=30)
                time_str = dt_ist.strftime("%d %b %Y, %I:%M %p IST")
            except:
                pass
        
        header = f"""
        <div style="background:linear-gradient(135deg,#0f172a 0%,#1e293b 100%);color:white;padding:24px;border-radius:12px;margin-bottom:24px;box-shadow:0 4px 6px rgba(0,0,0,0.1);">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:20px;">
                <div>
                    <div style="font-size:28px;font-weight:800;margin-bottom:4px;">{html.escape(str(name))}</div>
                    <div style="font-size:14px;color:#94a3b8;">{symbol} • {info.get('exchange','')} • {info.get('sector','')} • {info.get('industry','')}</div>
                    <div style="font-size:12px;color:#64748b;margin-top:4px;">🕐 {time_str or 'Market Closed'}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:36px;font-weight:800;">{currency}{price:,.2f}</div>
                    <div style="font-size:18px;color:{'#4ade80' if change >= 0 else '#f87171'};font-weight:600;">
                        {'+' if change > 0 else ''}{change:,.2f} ({'+' if change_pct > 0 else ''}{change_pct:.2f}%)
                    </div>
                </div>
            </div>
        </div>
        """
        
        # Build all sections
        parts = [header]
        
        # Price/Volume with chart
        chart_svg = build_mini_chart(hist)
        if chart_svg:
            parts.append(build_card("Price Trend (30D)", chart_svg, MAIN_ICONS["Trend"], "blue"))
        
        parts.append(build_price_volume_section(info, hist, price_m, vol_m, tech_m))
        
        # Signals
        sig_html = build_signals(info, price_m, tech_m, vol_m)
        if sig_html:
            parts.append(sig_html)
        
        # Events
        events_html = build_events(info, actions, calendar)
        if events_html:
            parts.append(events_html)
        
        # Fundamentals
        fund_html = build_fundamentals_section(info)
        if fund_html:
            parts.append(build_card("Fundamentals", fund_html, MAIN_ICONS["Fundamentals"], "green"))
        
        # Dividends
        div_html = build_dividend_section(info)
        if div_html:
            parts.append(div_html)
        
        # Ownership
        own_html = build_ownership_section(info)
        if own_html:
            parts.append(own_html)
        
        # Analyst
        analyst_html = build_analyst_section(info, recs)
        if analyst_html:
            parts.append(analyst_html)
        
        # Risk
        risk_html = build_risk_section(info)
        if risk_html:
            parts.append(risk_html)
        
        # Profile
        profile_html = build_profile_section(info)
        if profile_html:
            parts.append(profile_html)
        
        return "".join(parts)
        
    except Exception as e:
        return f'<div style="color:#dc2626;padding:20px;background:#fef2f2;border-radius:8px;"><strong>Error:</strong><br>{html.escape(str(e))}<br><pre>{html.escape(traceback.format_exc())}</pre></div>'

# Gradio interface for HF Spaces
if __name__ == "__main__":
    import gradio as gr
    
    demo = gr.Interface(
        fn=fetch_info,
        inputs=gr.Textbox(label="Stock Symbol (e.g., RELIANCE, TCS, INFY)", placeholder="Enter NSE symbol without .NS"),
        outputs=gr.HTML(label="Stock Analysis"),
        examples=[["RELIANCE"], ["TCS"], ["INFY"], ["HDFCBANK"], ["SBIN"]],
        title="Indian Stock Analyzer",
        description="Real-time stock analysis for NSE listed companies. Optimized for fast loading on HF Spaces.",
        theme=gr.themes.Soft()
    )
    
    # Queue prevents timeout on slow requests
    demo.queue(default_concurrency_limit=5).launch()