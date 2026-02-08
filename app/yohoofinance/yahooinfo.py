# ==============================
# Imports
# ==============================
import yfinance as yf
import pandas as pd
import numpy as np
import traceback
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
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
    "Trend": "📉",
    "Index": "🇮🇳"  # ADD THIS LINE
}
# ==============================
# Short names (Extended)
# ==============================
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
    "fiftyTwoWeekChangePercent": "52W Chg%",
    "fiftyDayAverageChange": "50DMA Chg",
    "twoHundredDayAverageChange": "200DMA Chg",
    "fiftyDayAverageChangePercent": "50DMA Chg%",
    "twoHundredDayAverageChangePercent": "200DMA Chg%",
    "regularMarketDayRange": "Day Range",
    "averageVolume": "Avg Volume",
    "averageVolume10days": "Avg Vol 10D",
    "averageVolume3Month": "Avg Vol 3M",
    
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
    "totalAssets": "Total Assets",
    "totalLiabilities": "Total Liabilities",
    
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
    "sustainableGrowthRate": "Sust. Growth Rate",
    
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
    "splitRatio": "Split Ratio",
    
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
    "companyOfficers": "Key Officers",
    "auditRisk": "Audit Risk",
    "boardRisk": "Board Risk",
    "compensationRisk": "Comp Risk",
    "shareHolderRightsRisk": "SH Rights Risk",
    "overallRisk": "Overall Risk",
    
    # Ownership
    "heldPercentInsiders": "Insider Ownership",
    "heldPercentInstitutions": "Institutional Ownership",
    "sharesOutstanding": "Shares Outstanding",
    "impliedSharesOutstanding": "Implied Shares",
    "floatShares": "Float",
    "sharesShort": "Short Interest",
    "shortRatio": "Short Ratio",
    "shortPercentOfFloat": "Short % of Float",
    "sharesShortPriorMonth": "Short Interest (Prior)",
    "shortPercentOfSharesOutstanding": "Short % Outstanding",
    
    # Analyst
    "recommendationKey": "Rating",
    "recommendationMean": "Rating Mean",
    "numberOfAnalystOpinions": "Analysts Count",
    "targetHighPrice": "Target High",
    "targetLowPrice": "Target Low",
    "targetMeanPrice": "Target Mean",
    "targetMedianPrice": "Target Median",
    "currentPrice": "Current Price",
    
    # Events
    "earningsDate": "Next Earnings",
    "earningsQuarter": "Earnings Quarter",
    "exDividendDate": "Ex-Div Date",
    "dividendDate": "Dividend Date",
    "firstTradeDate": "IPO Date",
    
    # Risk & Beta
    "beta": "Beta",
    "beta3Year": "3Y Beta",
    "beta5Year": "5Y Beta",
    "volatility": "Volatility",
    "standardDeviation": "Std Dev",
    
    # Technicals
    "rsi": "RSI(14)",
    "macd": "MACD",
    "signal": "Signal",
    "momentum_10d": "10D Momentum",
    "momentum_20d": "20D Momentum",
    "volatility_20d": "20D Volatility",
    "adr": "ADR%",
    "vwap": "VWAP",
    
    # Other
    "currency": "Currency",
    "exchange": "Exchange",
    "quoteType": "Type",
    "symbol": "Symbol",
    "underlyingSymbol": "Underlying",
    "shortName": "Short Name",
    "longName": "Full Name"
}

# ==============================
# Groups Configuration
# ==============================
PRICE_VOLUME_GROUPS = {
    "Live Trading": ["Price", "Chg", "Chg%", "Prev Close", "Open"],
    "Day's Range": ["High", "Low", "Day Range", "52W Chg%"],
    "Volume Analysis": ["Volume", "Avg Vol 10D", "Avg Vol 3M", "Vol Spike (1D/10D)", "Vol Trend (11D/30D)", "Rel Volume", "Vol vs 3M Avg"],
    "Moving Averages": ["50 DMA", "200 DMA", "50DMA Chg%", "200DMA Chg%"],
    "52-Week Range": ["52W Low", "52W High", "52W Pos"]
}

FUNDAMENTAL_GROUPS = {
    "Valuation": ["Market Cap", "Enterprise Value", "P/E (TTM)", "Forward P/E", "P/B", "P/S", "PEG Ratio", "EV/Revenue", "EV/EBITDA"],
    "Profitability": ["ROE", "ROA", "ROCE", "Profit Margin", "Operating Margin", "EBITDA Margin", "Gross Margin"],
    "Financial Health": ["Debt/Equity", "Current Ratio", "Quick Ratio", "Total Cash", "Total Debt", "Net Debt", "Cash/Share"],
    "Income": ["Revenue", "Revenue/Share", "EPS (TTM)", "Forward EPS", "Trailing EPS"],
    "Growth Metrics": ["Revenue Growth", "Earnings Growth", "Quarterly Rev Growth", "Quarterly EPS Growth", "Sust. Growth Rate"]
}

# ==============================
# Noise keys (Extended)
# ==============================
NOISE_KEYS = {
    "maxAge", "priceHint", "triggerable", "customPriceAlertConfidence",
    "sourceInterval", "exchangeDataDelayedBy", "esgPopulated", "cryptoTradeable",
    "firstTradeDateMilliseconds", "timeZoneFullName", "timeZoneShortName",
    "uuid", "messageBoardId", "gmtOffSetMilliseconds", "exchangeTimezoneName", "preMarketTime", "postMarketTime", "marketState",
    "corporateActions", "dividendEvents", "earningsEvents", "splitEvents",
    "pageViews", "quotetype", "history", "dataGranularity", "range", "scale",
    "validRanges", "validIntervals", "instrumentType", "symbol", "underlyingSymbol",
    "quoteType", "exchange", "currency", "financialCurrency", "market", "uuid"
}

# ==============================
# Safe Value Handling
# ==============================
def is_empty_value(v):
    """Safely check if a value is empty/None without triggering array comparisons"""
    # Handle None
    if v is None:
        return True
    
    # Handle strings
    if isinstance(v, str):
        return v == ""
    
    # Handle empty collections
    if isinstance(v, (list, tuple)) and len(v) == 0:
        return True
    if isinstance(v, dict) and len(v) == 0:
        return True
    
    # Handle numpy arrays - check size, don't use pd.isna
    if isinstance(v, np.ndarray):
        return v.size == 0
    
    # Handle pandas Series/DataFrame
    if isinstance(v, pd.Series):
        return v.empty
    if isinstance(v, pd.DataFrame):
        return v.empty
    
    # Handle numpy scalars - never empty
    if isinstance(v, (np.integer, np.floating, np.bool_)):
        return False
    
    # Handle any object with size attribute (arrays, etc)
    if hasattr(v, 'size') and callable(getattr(v, 'size', None)):
        try:
            return v.size == 0
        except:
            pass
    
    # Handle any object with empty attribute
    if hasattr(v, 'empty'):
        try:
            return bool(v.empty)
        except:
            pass
    
    # Handle any object with __len__ but not strings/bytes
    if hasattr(v, '__len__') and not isinstance(v, (str, bytes)):
        try:
            if len(v) == 0:
                return True
            # If it has length > 0, it's not empty (don't check contents)
            return False
        except:
            pass
    
    # Only use pd.isna on scalar values
    # Check if it's a scalar type first
    if isinstance(v, (int, float, bool, str)):
        try:
            return bool(pd.isna(v))
        except:
            return False
    
    # For anything else, assume not empty to be safe
    return False


def is_simple_value(v):
    """Check if value is a simple scalar we can process"""
    if isinstance(v, (str, int, float, bool)):
        return True
    if isinstance(v, (np.integer, np.floating)):
        return True
    if isinstance(v, datetime):
        return True
    return False

# ==============================
# Data Fetching
# ==============================
def yfinfo(symbol):
    try:
        # Fetch stock and index concurrently
        def fetch_stock():
            t = yf.Ticker(symbol + ".NS")
            info = t.info
            df = t.history(period="1y", interval="1d")
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df = df.reset_index()
            for c in ["Open", "High", "Low", "Close", "Volume"]:
                if c in df.columns:
                    df[c] = pd.to_numeric(df[c], errors="coerce")
            df = df.dropna(subset=["Date", "Open", "High", "Low", "Close"])
            return info, df
        
        def fetch_index():
            try:
                t = yf.Ticker("^NSEI")
                df = t.history(period="1y", interval="1d")
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                df = df.reset_index()
                for c in ["Open", "High", "Low", "Close"]:
                    if c in df.columns:
                        df[c] = pd.to_numeric(df[c], errors="coerce")
                df = df.dropna(subset=["Date", "Open", "High", "Low", "Close"])
                return df
            except:
                return pd.DataFrame()
        
        # Concurrent fetch
        with ThreadPoolExecutor(max_workers=2) as executor:
            stock_future = executor.submit(fetch_stock)
            index_future = executor.submit(fetch_index)
            (info, hist), index_hist = stock_future.result(), index_future.result()
        
        # Fetch other data
        t = yf.Ticker(symbol + ".NS")
        try:
            actions = t.actions if hasattr(t, 'actions') else pd.DataFrame()
            if not isinstance(actions, pd.DataFrame):
                actions = pd.DataFrame()
        except:
            actions = pd.DataFrame()
        
        try:
            calendar = t.calendar if hasattr(t, 'calendar') else pd.DataFrame()
            if not isinstance(calendar, pd.DataFrame):
                calendar = pd.DataFrame()
        except:
            calendar = pd.DataFrame()
        
        try:
            recommendations = t.recommendations if hasattr(t, 'recommendations') else pd.DataFrame()
            if not isinstance(recommendations, pd.DataFrame):
                recommendations = pd.DataFrame()
        except:
            recommendations = pd.DataFrame()
        
        return (info if isinstance(info, dict) else {}), hist, index_hist, actions, calendar, recommendations
        
    except Exception as e:
        return {"__error__": str(e)}, pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()        
# ==============================
# Formatting
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

def format_percent(v, decimals=2, include_sign=True):
    try:
        v = float(v)
        cls = "pos" if v > 0 else "neg" if v < 0 else ""
        sign = "+" if include_sign and v > 0 else ""
        return f'<span class="{cls}">{sign}{v:.{decimals}f}%</span>'
    except:
        return str(v)

def format_currency(v, symbol="₹"):
    try:
        v = float(v)
        cls = "pos" if v > 0 else "neg" if v < 0 else ""
        return f'<span class="{cls}">{symbol}{human_number(v)}</span>'
    except:
        return str(v)

def format_date(ts):
    try:
        if isinstance(ts, (int, float)):
            if ts > 1e12: ts = ts / 1000
            dt = datetime.fromtimestamp(ts, tz=timezone.utc)
            return dt.strftime("%d %b %Y")
        if isinstance(ts, datetime):
            return ts.strftime("%d %b %Y")
        if isinstance(ts, str):
            return ts
        return str(ts)
    except:
        return str(ts)

def looks_like_unix_ts(v):
    try:
        v = int(v)
        return (946684800 <= v <= 4102444800 or 946684800000 <= v <= 4102444800000)
    except:
        return False

def format_value(k, v):
    lk = k.lower()
    
    # Handle dates
    if looks_like_unix_ts(v) and any(x in lk for x in ["date", "time"]):
        return format_date(v)
    
    # Handle percentages
    if any(x in lk for x in ["percent", "yield", "margin", "ratio", "growth", "change", "spike", "short", "insider", "institution", "payout", "roe", "roa", "roce", "adr", "volatility", "beta", "risk"]):
        return format_percent(v)
    
    # Handle currency
    if any(x in lk for x in ["cap", "value", "price", "cash", "debt", "revenue", "income", "ebitda", "target", "book", "sales", "assets", "liabilities"]):
        return format_currency(v)
    
    # Handle large numbers
    if isinstance(v, (int, float, np.integer, np.floating)) and abs(v) >= 1e3:
        return human_number(v)
    
    # Handle text
    if isinstance(v, str):
        if len(v) > 100:
            return f'<div class="long-text">{v}</div>'
        return v
    
    return str(v)

# ==============================
# HTML Helpers
# ==============================
def column_layout(html, cols=3):
    return f"""
    <style>
        .grid{{display:grid;gap:12px;grid-template-columns:repeat({cols},1fr);}}
        @media(max-width:1200px){{.grid{{grid-template-columns:repeat(2,1fr);}}}}
        @media(max-width:768px){{.grid{{grid-template-columns:1fr;}}}}
        .pos{{color:#16a34a;font-weight:700;}}
        .neg{{color:#dc2626;font-weight:700;}}
        .alert{{color:#ea580c;font-weight:700;}}
        .neutral{{color:#6b7280;}}
        .strong{{color:#059669;font-weight:700;}}
        .weak{{color:#dc2626;font-weight:700;}}
        .long-text{{font-size:12px;line-height:1.5;color:#374151;max-height:150px;overflow-y:auto;padding:10px;background:#f8fafc;border-radius:6px;border:1px solid #e2e8f0;}}
        .event-card{{background:#fefce8;border-left:4px solid #eab308;padding:10px;margin:5px 0;border-radius:4px;}}
        .split-card{{background:#f0fdf4;border-left:4px solid #16a34a;padding:10px;margin:5px 0;border-radius:4px;}}
        .div-card{{background:#eff6ff;border-left:4px solid #2563eb;padding:10px;margin:5px 0;border-radius:4px;}}
    </style>
    <div class="grid">{html}</div>
    """

def html_card(title, body, mini=False, accent=False, color=None):
    colors = {
        "blue": ("#eff6ff", "#3b82f6"),
        "green": ("#f0fdf4", "#16a34a"),
        "yellow": ("#fefce8", "#eab308"),
        "red": ("#fef2f2", "#dc2626"),
        "purple": ("#faf5ff", "#9333ea")
    }
    
    if color and color in colors:
        bg, border = colors[color]
    elif accent:
        bg, border = "#fef3c7", "#f59e0b"
    else:
        bg, border = "#f8fafc", "#e2e8f0"
    
    font = "13px" if mini else "14px"
    pad = "10px" if mini else "14px"
    title_size = "13px" if mini else "15px"
    
    return f"""
    <div style="background:{bg};border:1px solid {border};border-radius:10px;padding:{pad};
                font-size:{font};margin-bottom:8px;box-shadow:0 1px 3px rgba(0,0,0,0.1);">
        <div style="font-weight:700;margin-bottom:8px;color:#1e293b;font-size:{title_size};border-bottom:1px solid {border};padding-bottom:6px;">{title}</div>
        {body}
    </div>
    """

def make_table(df, highlight_fields=None):
    if df.empty:
        return ""
    rows = []
    for r in df.itertuples():
        val = r.Value
        if highlight_fields and r.Field in highlight_fields:
            val = f"<strong>{val}</strong>"
        rows.append(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #e2e8f0;padding:6px 0;">
            <span style="color:#64748b;font-size:12px;">{r.Field}</span>
            <span style="font-weight:600;color:#0f172a;">{val}</span>
        </div>
        """)
    return "".join(rows)

def make_progress_bar(value, max_val=100, color="#0ea5e9"):
    try:
        pct = min(abs(float(value)) / max_val * 100, 100)
        return f"""
        <div style="background:#e2e8f0;height:6px;border-radius:3px;margin-top:4px;overflow:hidden;">
            <div style="background:{color};width:{pct}%;height:100%;border-radius:3px;"></div>
        </div>
        <div style="text-align:right;font-size:10px;color:#64748b;margin-top:2px;">{value:.1f}%</div>
        """
    except:
        return ""

# ==============================
# Data Processing (FIXED)
# ==============================
def build_df_from_dict(data):
    """Build DataFrame with safe empty value checking"""
    rows = []
    for k, v in data.items():
        if k in NOISE_KEYS:
            continue
        if is_empty_value(v):
            continue
        if not is_simple_value(v):
            continue
        try:
            formatted = format_value(k, v)
            rows.append((SHORT_NAMES.get(k, k[:25]), formatted))
        except Exception:
            continue
    
    return pd.DataFrame(rows, columns=["Field", "Value"])

def resolve_duplicates(data):
    """Resolve duplicate fields with safe value checking"""
    DUP = {
        "price": ["regularMarketPrice", "currentPrice"],
        "volume": ["regularMarketVolume", "volume"],
        "change": ["regularMarketChange", "change"],
        "changePercent": ["regularMarketChangePercent", "changePercent"]
    }
    
    resolved, used = {}, set()
    
    for keys in DUP.values():
        for k in keys:
            if k in data and not is_empty_value(data[k]) and is_simple_value(data[k]):
                resolved[k] = data[k]
                used.update(keys)
                break
    
    for k, v in data.items():
        if k not in used and not is_empty_value(v) and is_simple_value(v):
            resolved[k] = v
    
    return resolved

def classify(k, v):
    """Classify data with safe type checking"""
    if not is_simple_value(v):
        return "profile"
    
    lk = k.lower()
    if k == "companyOfficers":
        return "management"
    if any(x in lk for x in ["dividend", "payout", "yield", "exdividend"]):
        return "dividends"
    if any(x in lk for x in ["split", "splitfactor"]):
        return "splits"
    if any(x in lk for x in ["earnings", "revenue", "eps", "growth", "margin", "pe", "pb", "ps", "roe", "roa", "debt", "equity", "cash", "ratio", "cap", "ebitda", "asset", "liability"]):
        return "fundamental"
    if any(x in lk for x in ["price", "volume", "change", "high", "low", "open", "average", "dma", "52week", "vwap", "gap", "range", "spike", "rsi", "volatility", "beta"]):
        return "price_volume"
    if any(x in lk for x in ["insider", "institution", "short", "float", "shares", "held", "ownership"]):
        return "ownership"
    if any(x in lk for x in ["recommendation", "analyst", "target", "rating", "estimate"]):
        return "analyst"
    if any(x in lk for x in ["risk", "audit", "board", "compensation"]):
        return "risk"
    if any(x in lk for x in ["sector", "industry", "country", "employees", "website", "phone", "address", "summary", "description", "business", "officer"]):
        return "profile"
    if isinstance(v, str) and len(v) > 100:
        return "long_text"
    return "profile"

def group_info(info):
    """Group info with safe value handling"""
    groups = {
        "price_volume": {}, "fundamental": {}, "dividends": {}, "splits": {},
        "ownership": {}, "analyst": {}, "risk": {}, "profile": {},
        "management": {}, "long_text": {}
    }
    
    for k, v in info.items():
        if k in NOISE_KEYS:
            continue
        if is_empty_value(v):
            continue
        if not is_simple_value(v):
            continue
            
        cat = classify(k, v)
        if cat in groups:
            groups[cat][k] = v
    
    return groups

def split_df(df, max_rows=8):
    if df.empty:
        return [df]
    n = len(df)
    cols = 1 if n <= 6 else 2 if n <= 14 else 3
    size = max((n + cols - 1) // cols, max_rows)
    return [df.iloc[i:i+size] for i in range(0, n, size)]

# ==============================
# Calculations
# ==============================
def calculate_volume_spikes(info, hist_df):
    """Calculate proper volume spikes with safety checks"""
    out = {}
    
    today_vol = info.get("regularMarketVolume") or info.get("volume")
    
    # Validate inputs
    if not today_vol or not isinstance(today_vol, (int, float, np.integer, np.floating)):
        return out
    
    if hist_df.empty or not isinstance(hist_df, pd.DataFrame):
        return out
    
    if 'Volume' not in hist_df.columns:
        return out
    
    volumes = hist_df['Volume'].dropna()
    if len(volumes) < 10:
        return out
    
    try:
        # Convert to float safely
        today_vol = float(today_vol)
        avg_10d = float(volumes.tail(10).mean())
        
        # 1. Daily Spike: Today vs 10-day average
        if avg_10d > 0 and not pd.isna(avg_10d):
            spike = (today_vol / avg_10d - 1) * 100
            out["volumeSpike"] = round(spike, 2)
            out["relativeVolume"] = round(today_vol / avg_10d, 2)
        
        # 2. Trend Spike: 11-day average vs 30-day average
        if len(volumes) >= 30:
            last_10 = volumes.tail(10).tolist()
            last_11 = last_10 + [today_vol]
            avg_11d = sum(last_11) / 11
            avg_30d = float(volumes.tail(30).mean())
            
            if avg_30d > 0 and not pd.isna(avg_30d):
                trend_spike = (avg_11d / avg_30d - 1) * 100
                out["volumeSpikeTrend"] = round(trend_spike, 2)
        
        # 3. vs 3-month average
        if len(volumes) >= 60:
            avg_3m = float(volumes.tail(60).mean())
            if avg_3m > 0 and not pd.isna(avg_3m):
                out["volumeVsAvg3M"] = round((today_vol / avg_3m - 1) * 100, 2)
                
    except (TypeError, ValueError, ZeroDivisionError):
        pass
    
    return out

def calculate_technicals(hist_df):
    """Calculate technical indicators"""
    out = {}
    if hist_df.empty or len(hist_df) < 20 or 'Close' not in hist_df.columns:
        return out
    
    closes = hist_df['Close'].dropna()
    if len(closes) < 20:
        return out
    
    try:
        # RSI
        def calculate_rsi(prices, period=14):
            if len(prices) < period + 1:
                return None
            deltas = prices.diff().dropna()
            gains = deltas.where(deltas > 0, 0)
            losses = -deltas.where(deltas < 0, 0)
            avg_gain = gains.rolling(window=period).mean().iloc[-1]
            avg_loss = losses.rolling(window=period).mean().iloc[-1]
            if avg_loss == 0 or pd.isna(avg_loss):
                return 100
            rs = avg_gain / avg_loss
            return 100 - (100 / (1 + rs))
        
        rsi = calculate_rsi(closes, 14)
        if rsi is not None and not pd.isna(rsi):
            out["rsi"] = round(float(rsi), 2)
        
        # MACD
        if len(closes) >= 26:
            exp1 = closes.ewm(span=12).mean()
            exp2 = closes.ewm(span=26).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9).mean()
            out["macd"] = round(float(macd.iloc[-1]), 2)
            out["signal"] = round(float(signal.iloc[-1]), 2)
        
        # Momentum
        if len(closes) >= 10:
            out["momentum_10d"] = round(float((closes.iloc[-1] / closes.iloc[-10] - 1) * 100), 2)
        if len(closes) >= 20:
            out["momentum_20d"] = round(float((closes.iloc[-1] / closes.iloc[-20] - 1) * 100), 2)
        
        # Volatility
        if len(closes) >= 20:
            returns = closes.pct_change().dropna()
            if len(returns) >= 20:
                vol = float(returns.tail(20).std() * (252 ** 0.5) * 100)
                out["volatility_20d"] = round(vol, 2)
        
        # ADR
        if all(x in hist_df.columns for x in ['High', 'Low', 'Close']):
            adr = float(((hist_df['High'] - hist_df['Low']) / hist_df['Close'] * 100).tail(20).mean())
            out["adr"] = round(adr, 2)
            
    except Exception:
        pass
    
    return out

def calculate_derived_metrics(info, hist_df):
    """Calculate all derived price/volume metrics"""
    out = {}
    price = info.get("regularMarketPrice")
    
    if not price or not isinstance(price, (int, float, np.integer, np.floating)):
        return out
    
    try:
        price = float(price)
        
        # Moving averages comparison
        dma50 = info.get("fiftyDayAverage")
        dma200 = info.get("twoHundredDayAverage")
        
        if dma50 and isinstance(dma50, (int, float, np.integer, np.floating)):
            dma50 = float(dma50)
            out["vs50DMA"] = "Above ↑" if price > dma50 else "Below ↓"
            out["fiftyDayAverageChangePercent"] = round((price / dma50 - 1) * 100, 2)
        
        if dma200 and isinstance(dma200, (int, float, np.integer, np.floating)):
            dma200 = float(dma200)
            out["vs200DMA"] = "Above ↑" if price > dma200 else "Below ↓"
            out["twoHundredDayAverageChangePercent"] = round((price / dma200 - 1) * 100, 2)
        
        # 52-week position
        low52 = info.get("fiftyTwoWeekLow")
        high52 = info.get("fiftyTwoWeekHigh")
        if low52 and high52 and isinstance(low52, (int, float)) and isinstance(high52, (int, float)):
            low52, high52 = float(low52), float(high52)
            if high52 != low52:
                pos = (price - low52) / (high52 - low52) * 100
                out["52WPos"] = round(pos, 1)
        
        # Intraday metrics
        prev = info.get("regularMarketPreviousClose")
        high = info.get("regularMarketDayHigh")
        low = info.get("regularMarketDayLow")
        
        if prev and isinstance(prev, (int, float)) and prev != 0:
            out["dailyGapPercent"] = round((price - prev) / prev * 100, 2)
        
        if high and low and isinstance(high, (int, float)) and isinstance(low, (int, float)) and price != 0:
            out["dailyRangePercent"] = round((float(high) - float(low)) / price * 100, 2)
        
        # VWAP
        out["vwap"] = round(price, 2)
        
    except Exception:
        pass
    
    return out

# ==============================
# Event Processing
# ==============================
def process_events(info, actions, calendar):
    """Process dividends, splits, earnings, and other events"""
    events = []
    
    # Ensure calendar is a DataFrame
    if isinstance(calendar, dict):
        calendar = pd.DataFrame(calendar)
    if not isinstance(calendar, pd.DataFrame):
        calendar = pd.DataFrame()
    
    # Ensure actions is a DataFrame
    if isinstance(actions, dict):
        actions = pd.DataFrame(actions)
    if not isinstance(actions, pd.DataFrame):
        actions = pd.DataFrame()
    
    # Upcoming earnings from calendar
    if not calendar.empty and 'Earnings Date' in calendar.columns:
        try:
            for date in calendar['Earnings Date']:
                if pd.notna(date):
                    events.append({
                        "type": "earnings",
                        "date": date,
                        "title": "Earnings Release",
                        "desc": "Quarterly earnings announcement"
                    })
        except:
            pass
    
    # Historical dividends from actions
    if not actions.empty and 'Dividends' in actions.columns:
        try:
            divs = actions[actions['Dividends'] > 0]['Dividends'].tail(5)
            for date, amount in divs.items():
                events.append({
                    "type": "dividend",
                    "date": date,
                    "title": f"Dividend: ₹{float(amount):.2f}",
                    "desc": f"Cash dividend of ₹{float(amount):.2f} per share"
                })
        except:
            pass
    
    # Historical splits from actions
    if not actions.empty and 'Stock Splits' in actions.columns:
        try:
            splits = actions[actions['Stock Splits'] != 0]['Stock Splits'].tail(5)
            for date, ratio in splits.items():
                if ratio > 0:
                    events.append({
                        "type": "split",
                        "date": date,
                        "title": f"Stock Split: {float(ratio)}:1",
                        "desc": f"Stock split at ratio {float(ratio)}:1"
                    })
        except:
            pass
    
    # Future dates from info
    if info.get("earningsDate"):
        try:
            date = info.get("earningsDate")
            if isinstance(date, (int, float)):
                date = datetime.fromtimestamp(date if date < 1e12 else date/1000, tz=timezone.utc)
            events.append({
                "type": "earnings",
                "date": date,
                "title": "Upcoming Earnings",
                "desc": "Next earnings announcement"
            })
        except:
            pass
    
    if info.get("exDividendDate"):
        try:
            date = info.get("exDividendDate")
            if isinstance(date, (int, float)):
                date = datetime.fromtimestamp(date if date < 1e12 else date/1000, tz=timezone.utc)
            events.append({
                "type": "dividend",
                "date": date,
                "title": "Ex-Dividend Date",
                "desc": "Shares trade ex-dividend"
            })
        except:
            pass
    
    if info.get("dividendDate"):
        try:
            date = info.get("dividendDate")
            if isinstance(date, (int, float)):
                date = datetime.fromtimestamp(date if date < 1e12 else date/1000, tz=timezone.utc)
            events.append({
                "type": "dividend",
                "date": date,
                "title": "Dividend Payment",
                "desc": "Dividend payment date"
            })
        except:
            pass
    
    # Sort by date
    try:
        events.sort(key=lambda x: x['date'] if isinstance(x['date'], datetime) else datetime.now(), reverse=True)
    except:
        pass
    
    return events
    

def build_events_section(events):
    """Build HTML for events timeline"""
    if not events:
        return ""
    
    html = ""
    for e in events[:10]:
        try:
            if isinstance(e['date'], datetime):
                date_str = e['date'].strftime("%d %b %Y")
            else:
                date_str = str(e['date'])[:10]
        except:
            date_str = "Unknown"
        
        if e['type'] == 'dividend':
            card_class = "div-card"
            icon = "💰"
        elif e['type'] == 'split':
            card_class = "split-card"
            icon = "✂️"
        else:
            card_class = "event-card"
            icon = "📢"
        
        html += f"""
        <div class="{card_class}">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div style="font-weight:600;">{icon} {e['title']}</div>
                <div style="font-size:12px;color:#64748b;">{date_str}</div>
            </div>
            <div style="font-size:12px;color:#374151;margin-top:4px;">{e['desc']}</div>
        </div>
        """
    
    return html_card(f"{MAIN_ICONS['Events']} Corporate Events", html, color="yellow")

# ==============================
# Signals & Analysis
# ==============================
def build_comprehensive_signals(info, technicals, spikes):
    """Build comprehensive trading signals"""
    rows = []
    price = info.get("regularMarketPrice")
    
    try:
        # Valuation
        pe = info.get("trailingPE")
        forward_pe = info.get("forwardPE")
        
        if pe and isinstance(pe, (int, float, np.integer, np.floating)):
            pe = float(pe)
            if pe < 10:
                rows.append(("Valuation", "Strong Buy", f"P/E {pe:.1f}x (Deep Value)", "strong"))
            elif pe < 15:
                rows.append(("Valuation", "Buy", f"P/E {pe:.1f}x (Undervalued)", "strong"))
            elif pe > 30:
                rows.append(("Valuation", "Avoid", f"P/E {pe:.1f}x (Overvalued)", "weak"))
            elif pe > 50:
                rows.append(("Valuation", "Sell", f"P/E {pe:.1f}x (Bubble)", "weak"))
            else:
                rows.append(("Valuation", "Hold", f"P/E {pe:.1f}x (Fair)", "neutral"))
        
        # Quality Score
        roe = info.get("returnOnEquity", 0) or 0
        roa = info.get("returnOnAssets", 0) or 0
        margins = info.get("profitMargins", 0) or 0
        
        if isinstance(roe, (int, float, np.integer, np.floating)):
            roe = float(roe)
        else:
            roe = 0
            
        if isinstance(roa, (int, float, np.integer, np.floating)):
            roa = float(roa)
        else:
            roa = 0
            
        if isinstance(margins, (int, float, np.integer, np.floating)):
            margins = float(margins)
        else:
            margins = 0
        
        quality_score = sum([
            1 if roe > 0.15 else 0,
            1 if roa > 0.05 else 0,
            1 if margins > 0.15 else 0
        ])
        
        if quality_score == 3:
            rows.append(("Quality", "Excellent", f"ROE {roe*100:.1f}%, ROA {roa*100:.1f}%", "strong"))
        elif quality_score >= 2:
            rows.append(("Quality", "Good", f"ROE {roe*100:.1f}%, Margins {margins*100:.1f}%", "neutral"))
        else:
            rows.append(("Quality", "Poor", "Weak profitability metrics", "weak"))
        
        # Financial Health
        debt = info.get("debtToEquity", 0) or 0
        current = info.get("currentRatio", 0) or 0
        
        if isinstance(debt, (int, float, np.integer, np.floating)):
            debt = float(debt)
        else:
            debt = 0
            
        if isinstance(current, (int, float, np.integer, np.floating)):
            current = float(current)
        else:
            current = 0
        
        if debt < 0.5 and current > 1.5:
            rows.append(("Health", "Strong", f"D/E {debt:.2f}, Current {current:.2f}", "strong"))
        elif debt > 1 or current < 1:
            rows.append(("Health", "Weak", f"D/E {debt:.2f}, Current {current:.2f}", "weak"))
        else:
            rows.append(("Health", "Stable", f"D/E {debt:.2f}, Current {current:.2f}", "neutral"))
        
        # Trend Analysis
        dma50 = info.get("fiftyDayAverage")
        dma200 = info.get("twoHundredDayAverage")
        
        if price and dma50 and dma200:
            price = float(price) if isinstance(price, (int, float, np.integer, np.floating)) else 0
            dma50 = float(dma50) if isinstance(dma50, (int, float, np.integer, np.floating)) else 0
            dma200 = float(dma200) if isinstance(dma200, (int, float, np.integer, np.floating)) else 0
            
            if price > dma50 > dma200:
                trend = "Strong Bull"
                cls = "strong"
            elif price > dma50:
                trend = "Bullish"
                cls = "neutral"
            elif price < dma50 < dma200:
                trend = "Strong Bear"
                cls = "weak"
            else:
                trend = "Bearish"
                cls = "neutral"
            rows.append(("Trend", trend, f"Price vs 50/200 DMA", cls))
        
        # Volume Analysis
        if spikes.get("volumeSpike"):
            spike = float(spikes["volumeSpike"])
            if spike > 100:
                rows.append(("Volume", "Spike!", f"+{spike:.0f}% vs 10-day avg", "strong"))
            elif spike > 50:
                rows.append(("Volume", "High", f"+{spike:.0f}% vs 10-day avg", "neutral"))
            elif spike < -50:
                rows.append(("Volume", "Low", f"{spike:.0f}% vs 10-day avg", "weak"))
        
        # Technicals
        rsi = technicals.get("rsi")
        if rsi and isinstance(rsi, (int, float, np.integer, np.floating)):
            rsi = float(rsi)
            if rsi > 70:
                rows.append(("RSI", "Overbought", f"RSI {rsi:.1f} - Consider selling", "weak"))
            elif rsi < 30:
                rows.append(("RSI", "Oversold", f"RSI {rsi:.1f} - Buying opportunity", "strong"))
            else:
                rows.append(("RSI", "Neutral", f"RSI {rsi:.1f}", "neutral"))
        
        # Dividend Score
        div_yield = info.get("dividendYield", 0) or 0
        payout = info.get("payoutRatio", 0) or 0
        
        if isinstance(div_yield, (int, float, np.integer, np.floating)):
            div_yield = float(div_yield)
        else:
            div_yield = 0
            
        if isinstance(payout, (int, float, np.integer, np.floating)):
            payout = float(payout)
        else:
            payout = 0
        
        if div_yield > 0.03 and payout < 0.6:
            rows.append(("Dividend", "Attractive", f"Yield {div_yield*100:.1f}%, Payout {payout*100:.0f}%", "strong"))
        elif div_yield > 0:
            rows.append(("Dividend", "Moderate", f"Yield {div_yield*100:.1f}%", "neutral"))
        
        # Growth
        rev_growth = info.get("revenueGrowth", 0) or 0
        earnings_growth = info.get("earningsGrowth", 0) or 0
        
        if isinstance(rev_growth, (int, float, np.integer, np.floating)):
            rev_growth = float(rev_growth)
        else:
            rev_growth = 0
            
        if isinstance(earnings_growth, (int, float, np.integer, np.floating)):
            earnings_growth = float(earnings_growth)
        else:
            earnings_growth = 0
        
        if rev_growth > 0.2 and earnings_growth > 0.2:
            rows.append(("Growth", "High", f"Rev +{rev_growth*100:.0f}%, EPS +{earnings_growth*100:.0f}%", "strong"))
        elif rev_growth < 0:
            rows.append(("Growth", "Declining", f"Rev {rev_growth*100:.0f}%", "weak"))
            
    except Exception:
        pass
    
    return rows

# ==============================
# Section Builders
# ==============================
def build_price_volume_section(info, hist_df):
    """Build comprehensive price/volume section"""
    # Get base data
    pv_data = {}
    for k in ["regularMarketPrice", "regularMarketChange", "regularMarketChangePercent",
              "regularMarketPreviousClose", "regularMarketOpen", "regularMarketDayHigh",
              "regularMarketDayLow", "regularMarketVolume", "averageDailyVolume10Day",
              "averageDailyVolume3Month", "fiftyDayAverage", "twoHundredDayAverage",
              "fiftyTwoWeekLow", "fiftyTwoWeekHigh", "fiftyTwoWeekChange"]:
        if k in info and is_simple_value(info[k]):
            pv_data[k] = info[k]
    
    # Calculate metrics
    derived = calculate_derived_metrics(info, hist_df)
    spikes = calculate_volume_spikes(info, hist_df)
    technicals = calculate_technicals(hist_df)
    
    # Merge all
    all_data = {**pv_data, **derived, **spikes, **technicals}
    df = build_df_from_dict(all_data)
    
    # Build cards by group
    cards = ""
    for title, fields in PRICE_VOLUME_GROUPS.items():
        sub = df[df["Field"].isin(fields)]
        if not sub.empty:
            extra = ""
            if title == "52-Week Range" and "52WPos" in derived:
                extra = make_progress_bar(derived["52WPos"], 100, "#0ea5e9")
            cards += html_card(title, make_table(sub) + extra, mini=True)
    
    # Add signals
    signals = build_comprehensive_signals(info, technicals, spikes)
    if signals:
        signal_html = "".join([
            f'<div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #e2e8f0;padding:8px 0;">'
            f'<div><div style="font-weight:600;color:#0f172a;">{s[0]}</div>'
            f'<div style="font-size:11px;color:#64748b;">{s[2]}</div></div>'
            f'<span class="{s[3]}">{s[1]}</span></div>'
            for s in signals
        ])
        cards += html_card(f"{MAIN_ICONS['Signals']} Trading Signals", signal_html, accent=True)
    
    return column_layout(cards, cols=3)

def build_fundamentals_section(fund_data):
    """Build comprehensive fundamentals"""
    if not fund_data:
        return ""
    
    cards = ""
    for title, fields in FUNDAMENTAL_GROUPS.items():
        sub_data = {}
        for k, v in fund_data.items():
            if SHORT_NAMES.get(k, k[:25]) in fields and is_simple_value(v):
                sub_data[k] = v
        
        if sub_data:
            df = build_df_from_dict(sub_data)
            if not df.empty:
                cards += html_card(title, make_table(df), mini=True)
    
    return html_card(f"{MAIN_ICONS['Fundamentals']} Fundamentals", column_layout(cards, cols=3)) if cards else ""

def build_dividend_section(div_data, info):
    """Build dividend-specific section"""
    # Combine div data with info
    all_div = {}
    for k, v in div_data.items():
        if is_simple_value(v):
            all_div[k] = v
    
    for k in ['dividendYield', 'dividendRate', 'payoutRatio', 'fiveYearAvgDividendYield',
              'trailingAnnualDividendRate', 'trailingAnnualDividendYield', 'exDividendDate',
              'dividendDate', 'lastDividendValue', 'lastDividendDate']:
        if k in info and is_simple_value(info[k]):
            all_div[k] = info[k]
    
    if not all_div:
        return ""
    
    df = build_df_from_dict(all_div)
    return html_card(f"{MAIN_ICONS['Dividends']} Dividend Analysis", make_table(df), color="blue")

def build_split_section(split_data, info):
    """Build stock split section"""
    all_split = {}
    for k, v in split_data.items():
        if is_simple_value(v):
            all_split[k] = v
    
    for k in ['lastSplitFactor', 'lastSplitDate', 'splitRatio']:
        if k in info and is_simple_value(info[k]):
            all_split[k] = info[k]
    
    if not all_split:
        return ""
    
    df = build_df_from_dict(all_split)
    return html_card(f"{MAIN_ICONS['Splits']} Stock Splits", make_table(df), color="green")

def build_ownership_section(own_data):
    """Build ownership structure"""
    if not own_data:
        return ""
    
    simple_data = {k: v for k, v in own_data.items() if is_simple_value(v)}
    if not simple_data:
        return ""
    
    df = build_df_from_dict(simple_data)
    if df.empty:
        return ""
    
    # Fix: cols goes to column_layout, not html_card
    return html_card(f"{MAIN_ICONS['Ownership']} Ownership Structure", 
                     column_layout(make_table(df), cols=2))
    
def build_analyst_section(analyst_data, recommendations):
    """Build analyst coverage"""
    if not analyst_data:
        return ""
    
    simple_data = {k: v for k, v in analyst_data.items() if is_simple_value(v)}
    df = build_df_from_dict(simple_data)
    html = make_table(df)
    
    # Add recent recommendations if available
    if not recommendations.empty and 'To Grade' in recommendations.columns:
        try:
            recent = recommendations.tail(5)
            html += "<div style='margin-top:10px;font-weight:600;border-top:1px solid #e2e8f0;padding-top:8px;'>Recent Ratings:</div>"
            for idx, row in recent.iterrows():
                date = idx.strftime("%d %b") if hasattr(idx, 'strftime') else str(idx)[:10]
                grade = row.get('To Grade', 'N/A')
                html += f"<div style='font-size:12px;padding:4px 0;'>{date}: {grade}</div>"
        except:
            pass
    
    return html_card(f"{MAIN_ICONS['Analyst']} Analyst Coverage", html, color="purple")

def build_risk_section(risk_data):
    """Build risk metrics"""
    if not risk_data:
        return ""
    
    simple_data = {k: v for k, v in risk_data.items() if is_simple_value(v)}
    if not simple_data:
        return ""
    
    df = build_df_from_dict(simple_data)
    return html_card(f"{MAIN_ICONS['Risk']} Risk Metrics", make_table(df), color="red")

def build_profile_section(profile_data, officers):
    """Build company profile"""
    if not profile_data and not officers:
        return ""
    
    html = ""
    
    # Short info
    short_fields = {k: v for k, v in profile_data.items() if isinstance(v, str) and len(v) <= 100}
    if short_fields:
        df = build_df_from_dict(short_fields)
        if not df.empty:
            html += column_layout("".join(html_card("Company Info", make_table(c), mini=True) for c in split_df(df)), cols=2)
    
    # Long description
    long_fields = {k: v for k, v in profile_data.items() if isinstance(v, str) and len(v) > 100}
    for k, v in long_fields.items():
        html += html_card(SHORT_NAMES.get(k, k[:20]), format_value(k, v))
    
    # Management
    if officers:
        cards = ""
        for o in officers[:8]:
            if isinstance(o, dict):
                name = o.get("name", "Unknown")
                title = o.get("title", "")
                age = o.get("age", "")
                age_str = f" ({age})" if age else ""
                pay = o.get("totalPay", 0)
                pay_str = f" - ₹{human_number(pay)}" if pay and isinstance(pay, (int, float)) else ""
                cards += html_card(f"{name}{age_str}", f'<div style="color:#64748b;font-size:11px;">{title}{pay_str}</div>', mini=True)
        if cards:
            html += html_card(f"{MAIN_ICONS['Management']} Leadership", column_layout(cards, cols=4))
    
    return html

def build_daily_trend_section(info, hist_df):
    """Build daily trend overview with mini candlestick chart and insights"""
    # Check if hist_df is valid
    if hist_df is None or (isinstance(hist_df, pd.DataFrame) and hist_df.empty):
        print("DEBUG: hist_df is None or empty")
        return ""
    
    # Handle both index and column date formats
    df = hist_df.copy()
    
    # If Date is a column, set it as index
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')
    
    if len(df) < 5:  # Need at least 5 days for chart
        print(f"DEBUG: Only {len(df)} rows, need at least 5")
        return ""
    
    try:
        # Ensure numeric columns exist
        required_cols = ['Open', 'High', 'Low', 'Close']
        for col in required_cols:
            if col not in df.columns:
                print(f"DEBUG: Missing column {col}")
                return ""
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        if 'Volume' in df.columns:
            df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')
        
        # Drop rows with NaN in required columns
        df = df.dropna(subset=required_cols)
        
        if len(df) < 5:
            print(f"DEBUG: After dropna, only {len(df)} rows")
            return ""
        
        # Get last 30 days for mini chart (or all if less)
        view = df.tail(30)
        
        # Generate mini SVG candlestick chart
        chart_svg = generate_mini_candlestick(view)
        
        # Calculate insights
        latest = view.iloc[-1]
        prev = view.iloc[-2] if len(view) > 1 else latest
        
        close = float(latest['Close'])
        day_change = (close - float(prev['Close'])) / float(prev['Close']) * 100 if len(view) > 1 else 0
        
        # Week change (approx 5-6 trading days)
        week_ago_idx = max(0, len(view) - 6)
        week_ago = view.iloc[week_ago_idx]
        week_change = (close - float(week_ago['Close'])) / float(week_ago['Close']) * 100
        
        # Month change (first available)
        month_ago = view.iloc[0]
        month_change = (close - float(month_ago['Close'])) / float(month_ago['Close']) * 100
        
        # Moving averages
        df['MA20'] = df['Close'].rolling(min(20, len(df))).mean()
        latest_ma = df['MA20'].iloc[-1]
        ma20 = float(latest_ma) if not pd.isna(latest_ma) else close
        
        # Simple trend
        trend = "Bullish" if close > ma20 else "Bearish" if close < ma20 else "Neutral"
        trend_color = "#16a34a" if trend == "Bullish" else "#dc2626" if trend == "Bearish" else "#6b7280"
        
        # 52-week position from available data
        high_52w = float(df['High'].max())
        low_52w = float(df['Low'].min())
        pos_52w = (close - low_52w) / (high_52w - low_52w) * 100 if high_52w != low_52w else 50
        
        # Volume
        volume = int(latest['Volume']) if 'Volume' in latest and not pd.isna(latest['Volume']) else 0
        avg_vol = int(df['Volume'].mean()) if 'Volume' in df.columns and len(df) > 0 else 1
        vol_spike = (volume / avg_vol - 1) * 100 if avg_vol > 0 else 0
        
        # Build insights HTML
        insights_html = f"""
        <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:8px;">
            <div style="background:#f0fdf4;border:1px solid #16a34a;border-radius:6px;padding:8px;">
                <div style="font-size:11px;color:#64748b;">Day Change</div>
                <div style="font-size:14px;font-weight:700;color:{'#16a34a' if day_change >= 0 else '#dc2626'};">{day_change:+.2f}%</div>
            </div>
            <div style="background:#eff6ff;border:1px solid #3b82f6;border-radius:6px;padding:8px;">
                <div style="font-size:11px;color:#64748b;">Period Change</div>
                <div style="font-size:14px;font-weight:700;color:{'#16a34a' if month_change >= 0 else '#dc2626'};">{month_change:+.2f}%</div>
            </div>
            <div style="background:#fefce8;border:1px solid #eab308;border-radius:6px;padding:8px;">
                <div style="font-size:11px;color:#64748b;">Trend Signal</div>
                <div style="font-size:14px;font-weight:700;color:{trend_color};">{trend}</div>
            </div>
            <div style="background:#f8fafc;border:1px solid #cbd5e1;border-radius:6px;padding:8px;">
                <div style="font-size:11px;color:#64748b;">Range Position</div>
                <div style="font-size:14px;font-weight:700;">{pos_52w:.1f}%</div>
                <div style="background:#e2e8f0;height:4px;border-radius:2px;margin-top:4px;">
                    <div style="background:#0ea5e9;width:{min(pos_52w,100)}%;height:100%;border-radius:2px;"></div>
                </div>
            </div>
            <div style="background:#f8fafc;border:1px solid #cbd5e1;border-radius:6px;padding:8px;grid-column:span 2;">
                <div style="font-size:11px;color:#64748b;">Volume vs Avg</div>
                <div style="font-size:14px;font-weight:700;color:{'#16a34a' if vol_spike > 50 else '#64748b'};">{vol_spike:+.0f}%</div>
            </div>
        </div>
        """
        
        # Combine chart and insights
        html = f"""
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:15px;align-items:start;">
            <div>
                {chart_svg}
                <div style="text-align:center;font-size:11px;color:#64748b;margin-top:5px;">Last {len(view)} Trading Days</div>
            </div>
            <div>
                {insights_html}
            </div>
        </div>
        """
        
        return html_card(f"{MAIN_ICONS['Trend']} Daily Trend Overview", html, color="blue")
        
    except Exception as e:
        print(f"ERROR in build_daily_trend_section: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return ""
def generate_mini_candlestick(df, width=400, height=200):
    """Generate compact SVG candlestick chart"""
    try:
        if len(df) < 2:
            return ""
        
        # Ensure we have required columns
        required = ['Open', 'High', 'Low', 'Close']
        if not all(c in df.columns for c in required):
            print(f"DEBUG generate_mini_candlestick: missing columns, have {df.columns.tolist()}")
            return ""
        
        n = len(df)
        margin = 20
        chart_w = width - 2 * margin
        chart_h = height - 2 * margin
        
        # Price scale
        min_price = float(df['Low'].min())
        max_price = float(df['High'].max())
        price_range = max_price - min_price if max_price != min_price else 1
        
        # Volume scale
        max_vol = float(df['Volume'].max()) if 'Volume' in df.columns else 1
        
        # Candle dimensions
        candle_w = chart_w / n * 0.7 if n > 0 else 10
        spacing = chart_w / n if n > 0 else 10
        
        svg_elements = []
        
        # Background grid
        for i in range(5):
            y = margin + (chart_h * i / 4)
            svg_elements.append(f'<line x1="{margin}" y1="{y}" x2="{width-margin}" y2="{y}" stroke="#e2e8f0" stroke-width="1"/>')
        
        # Draw candles
        for i, (idx, row) in enumerate(df.iterrows()):
            x = margin + i * spacing + spacing * 0.15
            
            open_p = float(row['Open'])
            high_p = float(row['High'])
            low_p = float(row['Low'])
            close_p = float(row['Close'])
            
            # Y coordinates (inverted)
            y_open = margin + chart_h - ((open_p - min_price) / price_range * chart_h)
            y_close = margin + chart_h - ((close_p - min_price) / price_range * chart_h)
            y_high = margin + chart_h - ((high_p - min_price) / price_range * chart_h)
            y_low = margin + chart_h - ((low_p - min_price) / price_range * chart_h)
            
            # Color
            color = "#16a34a" if close_p >= open_p else "#dc2626"
            
            # Wick
            svg_elements.append(f'<line x1="{x + candle_w/2}" y1="{y_high}" x2="{x + candle_w/2}" y2="{y_low}" stroke="{color}" stroke-width="1"/>')
            
            # Body
            body_top = min(y_open, y_close)
            body_height = max(abs(y_close - y_open), 1)
            
            svg_elements.append(f'<rect x="{x}" y="{body_top}" width="{candle_w}" height="{body_height}" fill="{color}" stroke="{color}" stroke-width="1"/>')
            
            # Volume bars at bottom
            if 'Volume' in row and max_vol > 0:
                vol = float(row['Volume'])
                vol_height = (vol / max_vol) * (chart_h * 0.15)
                vol_y = height - margin - vol_height
                svg_elements.append(f'<rect x="{x}" y="{vol_y}" width="{candle_w}" height="{vol_height}" fill="#94a3b8" opacity="0.5"/>')
        
        # Current price line
        last_close = float(df.iloc[-1]['Close'])
        y_last = margin + chart_h - ((last_close - min_price) / price_range * chart_h)
        svg_elements.append(f'<line x1="{margin}" y1="{y_last}" x2="{width-margin}" y2="{y_last}" stroke="#0ea5e9" stroke-width="1" stroke-dasharray="3,3" opacity="0.7"/>')
        
        svg = f"""
        <svg width="{width}" height="{height}" style="background:#ffffff;border:1px solid #e2e8f0;border-radius:6px;">
            <rect width="100%" height="100%" fill="#fafafa"/>
            {''.join(svg_elements)}
            <text x="{width-margin}" y="{y_last-3}" font-size="10" fill="#0ea5e9" text-anchor="end">{last_close:.2f}</text>
        </svg>
        """
        
        return svg
        
    except Exception as e:
        print(f"ERROR in generate_mini_candlestick: {str(e)}")
        return ""
def calculate_index_correlation(stock_df, index_df):
    """Calculate beta, correlation, and relative strength"""
    metrics = {}
    
    if stock_df.empty or index_df.empty:
        return metrics
    
    try:
        stock_df['Date'] = pd.to_datetime(stock_df['Date']).dt.date
        index_df['Date'] = pd.to_datetime(index_df['Date']).dt.date
        
        merged = pd.merge(stock_df[['Date', 'Close']], index_df[['Date', 'Close']], 
                         on='Date', suffixes=('_stock', '_index'))
        
        if len(merged) < 20:
            return metrics
        
        merged['stock_ret'] = merged['Close_stock'].pct_change()
        merged['index_ret'] = merged['Close_index'].pct_change()
        merged = merged.dropna()
        
        if len(merged) < 10:
            return metrics
        
        # Beta
        covariance = merged['stock_ret'].cov(merged['index_ret'])
        variance = merged['index_ret'].var()
        if variance != 0:
            metrics['beta'] = round(covariance / variance, 2)
        
        # Correlation
        correlation = merged['stock_ret'].corr(merged['index_ret'])
        if not pd.isna(correlation):
            metrics['correlation'] = round(correlation * 100, 1)
        
        # Relative strength
        stock_change = (merged['Close_stock'].iloc[-1] / merged['Close_stock'].iloc[0] - 1) * 100
        index_change = (merged['Close_index'].iloc[-1] / merged['Close_index'].iloc[0] - 1) * 100
        metrics['stock_change'] = round(stock_change, 2)
        metrics['index_change'] = round(index_change, 2)
        metrics['relative_strength'] = round(stock_change - index_change, 2)
        metrics['outperformance'] = "Outperforming" if metrics['relative_strength'] > 0 else "Underperforming"
        
        # Volatility
        stock_vol = merged['stock_ret'].std() * (252 ** 0.5) * 100
        index_vol = merged['index_ret'].std() * (252 ** 0.5) * 100
        metrics['stock_volatility'] = round(stock_vol, 2)
        metrics['index_volatility'] = round(index_vol, 2)
        metrics['volatility_premium'] = round(stock_vol - index_vol, 2)
        
    except Exception as e:
        print(f"Correlation error: {e}")
    
    return metrics

def build_combined_trend_section(info, stock_hist, index_hist):
    """Build side-by-side stock and index trend with correlation metrics"""
    
    if stock_hist.empty or len(stock_hist) < 5:
        return ""
    
    try:
        # Prepare data
        stock_df = stock_hist.copy()
        if 'Date' in stock_df.columns:
            stock_df['Date'] = pd.to_datetime(stock_df['Date'])
            stock_df = stock_df.set_index('Date')
        
        index_df = index_hist.copy()
        if not index_df.empty and 'Date' in index_df.columns:
            index_df['Date'] = pd.to_datetime(index_df['Date'])
            index_df = index_df.set_index('Date')
        
        stock_view = stock_df.tail(50)
        index_view = index_df.tail(50) if not index_df.empty else pd.DataFrame()
        
        # Charts
        stock_chart = generate_mini_candlestick(stock_view, width=480, height=180)
        index_chart = generate_mini_candlestick(index_view, width=480, height=180) if not index_view.empty else ""
        
        # Insights
        stock_insights = calculate_insights(stock_view, "stock")
        index_insights = calculate_insights(index_view, "index") if not index_view.empty else {}
        
        # Correlation
        correlation_metrics = calculate_index_correlation(stock_hist, index_hist)
        
        # Layout
        charts_row = f"""
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:20px;">
            <div>
                <div style="font-weight:600;margin-bottom:8px;color:#1e293b;">🇮🇳 Nifty 50</div>
                {index_chart if index_chart else '<div style="height:180px;background:#f1f5f9;border-radius:6px;display:flex;align-items:center;justify-content:center;color:#64748b;">No data</div>'}
            </div>
            <div>
                <div style="font-weight:600;margin-bottom:8px;color:#1e293b;">📉 {info.get('shortName', 'Stock')}</div>
                {stock_chart}
            </div>
        </div>
        """
        
        insights_row = f"""
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:20px;">
            <div>{build_insights_card(index_insights, "Nifty 50", "#3b82f6") if index_insights else ''}</div>
            <div>{build_insights_card(stock_insights, info.get('shortName', 'Stock'), "#16a34a")}</div>
        </div>
        """
        
        correlation_html = build_correlation_card(correlation_metrics) if correlation_metrics else ""
        
        full_html = charts_row + insights_row + correlation_html
        
        return html_card("📊 Market Trend Analysis", full_html, color="blue")
        
    except Exception as e:
        print(f"ERROR in build_combined_trend_section: {e}")
        return ""

def calculate_insights(df, type_label):
    """Calculate insights for dataframe"""
    if df.empty or len(df) < 2:
        return {}
    
    try:
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        period_ago = df.iloc[0]
        
        close = float(latest['Close'])
        prev_close = float(prev['Close'])
        period_close = float(period_ago['Close'])
        
        day_change = (close - prev_close) / prev_close * 100 if prev_close != 0 else 0
        period_change = (close - period_close) / period_close * 100 if period_close != 0 else 0
        
        ma20 = df['Close'].rolling(min(20, len(df))).mean().iloc[-1]
        trend = "Bullish" if close > ma20 else "Bearish" if close < ma20 else "Neutral"
        
        high = df['High'].max()
        low = df['Low'].min()
        pos = (close - low) / (high - low) * 100 if high != low else 50
        
        volume = int(latest['Volume']) if 'Volume' in latest and not pd.isna(latest['Volume']) else 0
        avg_vol = df['Volume'].mean() if 'Volume' in df.columns else 1
        vol_spike = (volume / avg_vol - 1) * 100 if avg_vol > 0 else 0
        
        return {
            'day_change': day_change,
            'period_change': period_change,
            'trend': trend,
            'position': pos,
            'vol_spike': vol_spike,
            'close': close
        }
    except:
        return {}

def build_insights_card(insights, name, color):
    """Build insights card"""
    if not insights:
        return ""
    
    trend_color = "#16a34a" if insights['trend'] == "Bullish" else "#dc2626" if insights['trend'] == "Bearish" else "#6b7280"
    
    return f"""
    <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:12px;">
        <div style="font-weight:600;margin-bottom:10px;color:#1e293b;border-bottom:1px solid #e2e8f0;padding-bottom:6px;">{name} Insights</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
            <div style="background:white;border:1px solid #e2e8f0;border-radius:6px;padding:8px;">
                <div style="font-size:10px;color:#64748b;">Day Change</div>
                <div style="font-size:13px;font-weight:700;color:{'#16a34a' if insights['day_change'] >= 0 else '#dc2626'};">{insights['day_change']:+.2f}%</div>
            </div>
            <div style="background:white;border:1px solid #e2e8f0;border-radius:6px;padding:8px;">
                <div style="font-size:10px;color:#64748b;">Period Change</div>
                <div style="font-size:13px;font-weight:700;color:{'#16a34a' if insights['period_change'] >= 0 else '#dc2626'};">{insights['period_change']:+.2f}%</div>
            </div>
            <div style="background:white;border:1px solid #e2e8f0;border-radius:6px;padding:8px;">
                <div style="font-size:10px;color:#64748b;">Trend</div>
                <div style="font-size:13px;font-weight:700;color:{trend_color};">{insights['trend']}</div>
            </div>
            <div style="background:white;border:1px solid #e2e8f0;border-radius:6px;padding:8px;">
                <div style="font-size:10px;color:#64748b;">Range Position</div>
                <div style="font-size:13px;font-weight:700;">{insights['position']:.1f}%</div>
                <div style="background:#e2e8f0;height:3px;border-radius:2px;margin-top:3px;">
                    <div style="background:{color};width:{min(insights['position'],100)}%;height:100%;border-radius:2px;"></div>
                </div>
            </div>
        </div>
        <div style="background:white;border:1px solid #e2e8f0;border-radius:6px;padding:8px;margin-top:8px;">
            <div style="font-size:10px;color:#64748b;">Volume vs Avg</div>
            <div style="font-size:13px;font-weight:700;color:{'#16a34a' if insights['vol_spike'] > 50 else '#64748b'};">{insights['vol_spike']:+.0f}%</div>
        </div>
    </div>
    """

def build_correlation_card(metrics):
    """Build correlation metrics card"""
    if not metrics:
        return ""
    
    beta = metrics.get('beta', 'N/A')
    correlation = metrics.get('correlation', 'N/A')
    relative = metrics.get('relative_strength', 'N/A')
    outperf = metrics.get('outperformance', '')
    stock_vol = metrics.get('stock_volatility', 'N/A')
    index_vol = metrics.get('index_volatility', 'N/A')
    vol_prem = metrics.get('volatility_premium', 'N/A')
    
    beta_desc = "High Volatility" if isinstance(beta, (int, float)) and beta > 1.5 else "Stable" if isinstance(beta, (int, float)) and beta < 0.5 else "Market-like"
    beta_color = "#dc2626" if isinstance(beta, (int, float)) and beta > 1.5 else "#16a34a" if isinstance(beta, (int, float)) and beta < 0.5 else "#6b7280"
    
    relative_color = "#16a34a" if isinstance(relative, (int, float)) and relative > 0 else "#dc2626" if isinstance(relative, (int, float)) and relative < 0 else "#6b7280"
    
    return f"""
    <div style="background:linear-gradient(135deg,#f0f9ff 0%,#e0f2fe 100%);border:1px solid #0ea5e9;border-radius:10px;padding:16px;margin-top:10px;">
        <div style="font-weight:700;margin-bottom:12px;color:#0c4a6e;font-size:16px;">🔗 Stock vs Index Correlation</div>
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;">
            <div style="background:white;border-radius:8px;padding:12px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,0.1);">
                <div style="font-size:24px;font-weight:800;color:{beta_color};">{beta}</div>
                <div style="font-size:11px;color:#64748b;margin-top:4px;">Beta</div>
                <div style="font-size:10px;color:{beta_color};font-weight:600;">{beta_desc}</div>
            </div>
            <div style="background:white;border-radius:8px;padding:12px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,0.1);">
                <div style="font-size:24px;font-weight:800;color:#7c3aed;">{correlation}%</div>
                <div style="font-size:11px;color:#64748b;margin-top:4px;">Correlation</div>
            </div>
            <div style="background:white;border-radius:8px;padding:12px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,0.1);">
                <div style="font-size:24px;font-weight:800;color:{relative_color};">{relative:+.1f}%</div>
                <div style="font-size:11px;color:#64748b;margin-top:4px;">vs Nifty 50</div>
                <div style="font-size:10px;color:{relative_color};font-weight:600;">{outperf}</div>
            </div>
            <div style="background:white;border-radius:8px;padding:12px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,0.1);">
                <div style="font-size:24px;font-weight:800;color:#7c3aed;">{vol_prem:+.1f}%</div>
                <div style="font-size:11px;color:#64748b;margin-top:4px;">Vol Premium</div>
            </div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px;">
            <div style="background:white;border-radius:6px;padding:10px;display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:12px;color:#64748b;">Stock Volatility</span>
                <span style="font-weight:700;color:#0f172a;">{stock_vol}%</span>
            </div>
            <div style="background:white;border-radius:6px;padding:10px;display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:12px;color:#64748b;">Index Volatility</span>
                <span style="font-weight:700;color:#0f172a;">{index_vol}%</span>
            </div>
        </div>
    </div>
    """
# ==============================
# Main Function (FIXED)
# ==============================
def fetch_info(symbol):
    try:
        # Fetch all data including index
        info, hist, index_hist, actions, calendar, recommendations = yfinfo(symbol)
        
        if "__error__" in info:
            return f'<div style="color:#dc2626;padding:20px;">Error: {info["__error__"]}</div>'
        
        # Group data
        groups = group_info(info)
        
        # Get market time
        market_time = info.get("regularMarketTime")
        time_str = ""
        if market_time:
            try:
                if isinstance(market_time, (int, float)):
                    if market_time > 1e12:
                        market_time = market_time / 1000
                    dt_utc = datetime.fromtimestamp(market_time, tz=timezone.utc)
                    dt_ist = dt_utc + timedelta(hours=5, minutes=30)
                    time_str = dt_ist.strftime("%d %b %Y, %I:%M %p")
            except:
                pass
        
        # Header
        name = info.get("longName") or info.get("shortName") or symbol
        price = float(info.get("regularMarketPrice", 0) or 0)
        change = float(info.get("regularMarketChange", 0) or 0)
        change_pct = float(info.get("regularMarketChangePercent", 0) or 0)
        currency = info.get("currency", "₹")
        
        header = f"""
        <div style="background:linear-gradient(135deg,#0f172a 0%,#1e293b 100%);color:white;padding:24px;border-radius:12px;margin-bottom:24px;box-shadow:0 4px 6px rgba(0,0,0,0.1);">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:20px;">
                <div>
                    <div style="font-size:28px;font-weight:800;margin-bottom:4px;">{name}</div>
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
        
        parts = [header]
        
        # ADDED: Combined Stock + Index Trend Section
        combined_trend = build_combined_trend_section(info, hist, index_hist)
        if combined_trend:
            parts.append(combined_trend)
        
        # Price/Volume with all metrics
        parts.append(build_price_volume_section(info, hist))
        
        # Events
        events = process_events(info, actions, calendar)
        if events:
            parts.append(build_events_section(events))
        
        # Fundamentals
        if groups["fundamental"]:
            parts.append(build_fundamentals_section(groups["fundamental"]))
        
        # Dividends
        if groups["dividends"] or info.get("dividendYield"):
            parts.append(build_dividend_section(groups["dividends"], info))
        
        # Splits
        if groups["splits"] or info.get("lastSplitFactor"):
            parts.append(build_split_section(groups["splits"], info))
        
        # Ownership
        if groups["ownership"]:
            parts.append(build_ownership_section(groups["ownership"]))
        
        # Analyst
        if groups["analyst"]:
            parts.append(build_analyst_section(groups["analyst"], recommendations))
        
        # Risk
        if groups["risk"]:
            parts.append(build_risk_section(groups["risk"]))
        
        # Profile & Management
        if groups["profile"] or groups["management"]:
            parts.append(build_profile_section(groups["profile"], groups["management"].get("companyOfficers")))
        
        # Any remaining long text
        for k, v in groups.get("long_text", {}).items():
            if k not in groups["profile"]:
                parts.append(html_card(SHORT_NAMES.get(k, k[:20]), format_value(k, v)))
        
        return "".join(parts)
        
    except Exception as e:
        return f'<div style="color:#dc2626;padding:20px;background:#fef2f2;border-radius:8px;"><strong>Error:</strong><br><pre>{traceback.format_exc()}</pre></div>'
