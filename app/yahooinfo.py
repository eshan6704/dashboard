'''# ==============================
# Imports
# ==============================
import yfinance as yf
import pandas as pd
import traceback
from datetime import datetime, timezone

from .persist import exists, load, save

# ==============================
# Icons
# ==============================
MAIN_ICONS = {
    "Price / Volume": "📈",
    "Fundamentals": "📊",
    "Trend": "📈",
    "Signals": "🧠",
    "Company Profile": "🏢",
    "Management": "👔",
    "VWAP": "📌",
}

# ==============================
# Short names
# ==============================
SHORT_NAMES = {
    "regularMarketPrice": "Price",
    "regularMarketChange": "Chg",
    "regularMarketChangePercent": "Chg%",
    "regularMarketPreviousClose": "Prev",
    "regularMarketOpen": "Open",
    "regularMarketDayHigh": "High",
    "regularMarketDayLow": "Low",
    "regularMarketVolume": "Vol",
    "averageDailyVolume10Day": "Avg Vol 10D",
    "averageDailyVolume3Month": "Avg Vol 3M",
    "fiftyDayAverage": "50DMA",
    "twoHundredDayAverage": "200DMA",
    "fiftyTwoWeekLow": "52W Low",
    "fiftyTwoWeekHigh": "52W High",
    "mostRecentQuarter":"Recent Q",
    "lastFiscalYearEnd":"FY End",
    "vwap":"VWAP",
    "dailyGapPercent":"Gap%",
    "dailyRangePercent":"Range%"
}

# ==============================
# Price / Volume Sub-Groups
# ==============================
PRICE_VOLUME_GROUPS = {
    "Market Price": ["Price","Chg","Chg%","Prev","Open"],
    "Intraday Range": ["High","Low","dailyRangePercent"],
    "Volume & Liquidity": ["Vol","Avg Vol 10D","Avg Vol 3M"],
    "Moving Averages": ["50DMA","200DMA","vs 50DMA","vs 200DMA"],
    "52W Range": ["52W Low","52W High","52W Pos"],
    "VWAP & Gap": ["VWAP","dailyGapPercent"]
}

# ==============================
# Noise keys
# ==============================
NOISE_KEYS = {
    "maxAge","priceHint","triggerable",
    "customPriceAlertConfidence",
    "sourceInterval","exchangeDataDelayedBy",
    "esgPopulated"
}

# ==============================
# Low-level Yahoo fetch
# ==============================
def yfinfo(symbol):
    try:
        t = yf.Ticker(symbol + ".NS")
        info = t.info
        return info if isinstance(info, dict) else {}
    except Exception as e:
        return {"__error__": str(e)}

# ==============================
# Formatting
# ==============================
def human_number(n):
    try:
        n = float(n)
        if abs(n) >= 1e7: return f"{n/1e7:.2f}Cr"
        if abs(n) >= 1e5: return f"{n/1e5:.2f}L"
        if abs(n) >= 1e3: return f"{n/1e3:.2f}K"
        return f"{n:,.2f}"
    except:
        return str(n)

DATE_KEYWORDS = ("date", "time", "timestamp", "fiscal", "quarter","earnings","dividend")
def looks_like_unix_ts(v):
    try:
        v = int(v)
        return (946684800 <= v <= 4102444800 or 946684800000 <= v <= 4102444800000)
    except:
        return False
def unix_to_dt(v):
    v = int(v)
    if v > 10**12: v //= 1000
    return datetime.fromtimestamp(v, tz=timezone.utc)
def fy_quarter_label(dt):
    y, m = dt.year, dt.month
    if m >= 4:
        fy = y + 1
        q = (m - 1)//3 + 1
    else:
        fy = y
        q = (m + 8)//3
    return f"Q{q} FY{str(fy)[-2:]}"
def format_value(k, v):
    lk = k.lower()
    # Date / Quarter
    if isinstance(v,(int,float)) and looks_like_unix_ts(v):
        if any(x in lk for x in DATE_KEYWORDS):
            dt = unix_to_dt(v)
            if "quarter" in lk:
                return fy_quarter_label(dt)
            return dt.strftime("%d %b %Y")
    # Numbers
    if isinstance(v,(int,float)):
        cls = "pos" if v>0 else "neg" if v<0 else ""
        if "percent" in lk:
            return f'<span class="{cls}">{v:.2f}%</span>'
        if any(x in lk for x in ["marketcap","revenue","income","value","cap","enterprise"]):
            return f'<span class="{cls}">₹{human_number(v)}</span>'
        return f'<span class="{cls}">{human_number(v)}</span>'
    return v

# ==============================
# HTML Helpers
# ==============================
def column_layout(html):
    return f"""
    <style>
        .grid{{display:grid;gap:10px;grid-template-columns:repeat(3,1fr);}}
        @media(max-width:1024px){{.grid{{grid-template-columns:repeat(2,1fr);}}}}
        @media(max-width:640px){{.grid{{grid-template-columns:1fr;}}}}
        .pos{{color:#0a7d32;font-weight:600;}}
        .neg{{color:#b00020;font-weight:600;}}
    </style>
    <div class="grid">{html}</div>
    """
def html_card(title,body,mini=False):
    font = "12px" if mini else "14px"
    pad  = "6px" if mini else "10px"
    return f"""
    <div style="background:#e6f0fa;border:1px solid #a3c0e0;border-radius:8px;padding:{pad};
                font-size:{font};margin-bottom:6px;">
        <div style="font-weight:600;margin-bottom:6px;">{title}</div>{body}
    </div>
    """
def make_table(df):
    return "".join(
        f"""<div style="display:flex;justify-content:space-between;border-bottom:1px dashed #bcd0ea;padding:2px 0;">
            <span>{r.Field}</span><span>{r.Value}</span></div>"""
        for r in df.itertuples()
    )
def collapsible(title,body):
    return f"""
    <details open>
        <summary style="cursor:pointer;font-weight:600;font-size:15px;padding:6px 0;">
            {title}
        </summary>{body}
    </details>
    """

# ==============================
# Data Helpers
# ==============================
def build_df_from_dict(data):
    rows = [(SHORT_NAMES.get(k,k[:16]), format_value(k,v)) for k,v in data.items() if k not in NOISE_KEYS]
    return pd.DataFrame(rows,columns=["Field","Value"])

def resolve_duplicates(data):
    DUP = {
        "price":["regularMarketPrice","currentPrice"],
        "prev":["regularMarketPreviousClose","previousClose"],
        "open":["regularMarketOpen","open"],
        "high":["regularMarketDayHigh","dayHigh"],
        "low":["regularMarketDayLow","dayLow"],
        "volume":["regularMarketVolume","volume"]
    }
    resolved, used = {}, set()
    for keys in DUP.values():
        for k in keys:
            if k in data:
                resolved[k] = data[k]
                used.update(keys)
                break
    for k,v in data.items():
        if k not in used:
            resolved[k] = v
    return resolved

def classify(k,v):
    lk = k.lower()
    if k=="companyOfficers": return "management"
    if any(x in lk for x in ["pe","pb","roe","roa","margin","debt","revenue","profit","eps","cap"]):
        return "fundamental"
    if isinstance(v,(int,float)): return "price_volume"
    if isinstance(v,str) and len(v)>80: return "long_text"
    return "profile"

def group_info(info):
    g = {"price_volume":{}, "fundamental":{}, "profile":{}, "management":{}, "long_text":{}}
    for k,v in info.items():
        if k in NOISE_KEYS or v in [None,"",[],{}]: continue
        g[classify(k,v)][k] = v
    return g

def split_df(df):
    n = len(df)
    cols = 1 if n<=6 else 2 if n<=14 else 3
    size = (n+cols-1)//cols
    return [df.iloc[i:i+size] for i in range(0,n,size)]

# ==============================
# Derived Metrics & Signals
# ==============================
def build_price_volume_derived(info):
    out={}
    price=info.get("regularMarketPrice")
    dma50=info.get("fiftyDayAverage")
    dma200=info.get("twoHundredDayAverage")
    low52=info.get("fiftyTwoWeekLow")
    high52=info.get("fiftyTwoWeekHigh")
    if price and dma50: out["vs 50DMA"]="Above ↑" if price>dma50 else "Below ↓"
    if price and dma200: out["vs 200DMA"]="Above ↑" if price>dma200 else "Below ↓"
    if price and low52 and high52 and high52!=low52: out["52W Pos"]=f"{(price-low52)/(high52-low52)*100:.1f}%"
    # Gap % and daily range %
    prev=info.get("regularMarketPreviousClose")
    high=info.get("regularMarketDayHigh")
    low=info.get("regularMarketDayLow")
    if price and prev: out["dailyGapPercent"]=(price-prev)/prev*100
    if high and low and price: out["dailyRangePercent"]=(high-low)/price*100
    # VWAP (approximation)
    vol=info.get("regularMarketVolume")
    if vol and price: out["VWAP"]=price
    return out

def build_smart_signals(info):
    rows=[]
    pe=info.get("trailingPE")
    roe=info.get("returnOnEquity")
    debt=info.get("debtToEquity")
    price=info.get("regularMarketPrice")
    dma50=info.get("fiftyDayAverage")
    dma200=info.get("twoHundredDayAverage")
    if pe: rows.append(("Valuation","Expensive" if pe>35 else "Cheap" if pe<15 else "Fair"))
    if roe: rows.append(("Quality","High" if roe>0.18 else "Average"))
    if debt: rows.append(("Balance Sheet","Weak" if debt>1 else "Healthy"))
    if price and dma50 and dma200:
        trend = "Bullish" if price>dma50>dma200 else "Bearish" if price<dma50<dma200 else "Neutral"
        rows.append(("Momentum",trend))
    return pd.DataFrame(rows,columns=["Field","Value"])

# ==============================
# Build Price/Volume Section
# ==============================
def build_price_volume_section(info,pv_data):
    df=build_df_from_dict(pv_data)
    derived=build_price_volume_derived(info)
    if derived: df=pd.concat([df,pd.DataFrame(derived.items(),columns=["Field","Value"])],ignore_index=True)
    cards=""
    for title,fields in PRICE_VOLUME_GROUPS.items():
        sub=df[df["Field"].isin(fields)]
        if not sub.empty: cards+=html_card(title,make_table(sub),mini=True)
    trend_df=df[df["Field"].isin(["vs 50DMA","vs 200DMA","52W Pos"])]
    if not trend_df.empty: cards+=html_card("Trend & Momentum",make_table(trend_df),mini=True)
    signals=build_smart_signals(info)
    if not signals.empty: cards+=html_card("Smart Signals",make_table(signals),mini=True)
    return column_layout(cards)

# ==============================
# Main Function
# ==============================
def fetch_info(symbol):
    key=f"info_{symbol}"
    if exists(key,"html"):
        cached=load(key,"html")
        if cached: return cached
    try:
        info=yfinfo(symbol)
        if "__error__" in info: return "No data"
        groups=group_info(info)
        html=""
        # Price / Volume
        pv=resolve_duplicates(groups["price_volume"])
        if pv: html+=html_card(f"{MAIN_ICONS['Price / Volume']} Price / Volume",build_price_volume_section(info,pv))
        # Fundamentals
        if groups["fundamental"]:
            df=build_df_from_dict(groups["fundamental"])
            html+=html_card(f"{MAIN_ICONS['Fundamentals']} Fundamentals",
                            column_layout("".join(html_card("Fundamentals",make_table(c),mini=True) for c in split_df(df))))
        # Company Profile
        if groups["profile"]:
            df=build_df_from_dict(groups["profile"])
            html+=html_card(f"{MAIN_ICONS['Company Profile']} Company Profile",
                            column_layout("".join(html_card("Profile",make_table(c),mini=True) for c in split_df(df))))
        # Management
        if groups["management"].get("companyOfficers"):
            cards=""
            for o in groups["management"]["companyOfficers"]:
                cards+=html_card(o.get("name",""),o.get("title",""),mini=True)
            html+=html_card(f"{MAIN_ICONS['Management']} Management",column_layout(cards))
        # Long Text
        for k,v in groups["long_text"].items():
            html+=html_card(SHORT_NAMES.get(k,k[:16]),v)
        save(key,html,"html")
        return html
    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>"
'''
# ==============================
# Imports
# ==============================
import yfinance as yf
import pandas as pd
import traceback
from datetime import datetime, timezone

from .persist import exists, load, save

# ==============================
# Icons
# ==============================
MAIN_ICONS = {
    "Price / Volume": "📈",
    "Fundamentals": "📊",
    "Trend": "📈",
    "Signals": "🧠",
    "Company Profile": "🏢",
    "Management": "👔",
    "VWAP": "📌",
    "IPO": "🚀"
}

# ==============================
# Short names
# ==============================
SHORT_NAMES = {
    "regularMarketPrice": "Price",
    "regularMarketChange": "Chg",
    "regularMarketChangePercent": "Chg%",
    "regularMarketPreviousClose": "Prev",
    "regularMarketOpen": "Open",
    "regularMarketDayHigh": "High",
    "regularMarketDayLow": "Low",
    "regularMarketVolume": "Vol",
    "averageDailyVolume10Day": "Avg Vol 10D",
    "averageDailyVolume3Month": "Avg Vol 3M",
    "fiftyDayAverage": "50DMA",
    "twoHundredDayAverage": "200DMA",
    "fiftyTwoWeekLow": "52W Low",
    "fiftyTwoWeekHigh": "52W High",
    "mostRecentQuarter":"Recent Q",
    "lastFiscalYearEnd":"FY End",
    "vwap":"VWAP",
    "dailyGapPercent":"Gap%",
    "dailyRangePercent":"Range%",
    "firstTradeDate":"IPO Date"
}

# ==============================
# Price / Volume Sub-Groups
# ==============================
PRICE_VOLUME_GROUPS = {
    "Market Price": ["Price","Chg","Chg%","Prev","Open","firstTradeDate"],
    "Intraday Range": ["High","Low","dailyRangePercent"],
    "Volume & Liquidity": ["Vol","Avg Vol 10D","Avg Vol 3M"],
    "Moving Averages": ["50DMA","200DMA","vs 50DMA","vs 200DMA"],
    "52W Range": ["52W Low","52W High","52W Pos"],
    "VWAP & Gap": ["VWAP","dailyGapPercent"]
}

# ==============================
# Noise keys
# ==============================
NOISE_KEYS = {
    "maxAge","priceHint","triggerable",
    "customPriceAlertConfidence",
    "sourceInterval","exchangeDataDelayedBy",
    "esgPopulated"
}

# ==============================
# Low-level Yahoo fetch
# ==============================
def yfinfo(symbol):
    try:
        t = yf.Ticker(symbol + ".NS")
        info = t.info
        return info if isinstance(info, dict) else {}
    except Exception as e:
        return {"__error__": str(e)}

# ==============================
# Formatting
# ==============================
def human_number(n):
    try:
        n = float(n)
        if abs(n) >= 1e7: return f"{n/1e7:.2f}Cr"
        if abs(n) >= 1e5: return f"{n/1e5:.2f}L"
        if abs(n) >= 1e3: return f"{n/1e3:.2f}K"
        return f"{n:,.2f}"
    except:
        return str(n)

DATE_KEYWORDS = ("date", "time", "timestamp", "fiscal", "quarter","earnings","dividend","firstTradeDate")
def looks_like_unix_ts(v):
    try:
        v = int(v)
        return (946684800 <= v <= 4102444800 or 946684800000 <= v <= 4102444800000)
    except:
        return False
def unix_to_dt(v):
    v = int(v)
    if v > 10**12: v //= 1000
    return datetime.fromtimestamp(v, tz=timezone.utc)
def fy_quarter_label(dt):
    y, m = dt.year, dt.month
    if m >= 4:
        fy = y + 1
        q = (m - 1)//3 + 1
    else:
        fy = y
        q = (m + 8)//3
    return f"Q{q} FY{str(fy)[-2:]}"
def format_value(k, v):
    lk = k.lower()
    # Date / Quarter
    if isinstance(v,(int,float)) and looks_like_unix_ts(v):
        if any(x in lk for x in DATE_KEYWORDS):
            dt = unix_to_dt(v)
            if "quarter" in lk:
                return fy_quarter_label(dt)
            return dt.strftime("%d %b %Y")
    # Numbers
    if isinstance(v,(int,float)):
        cls = "pos" if v>0 else "neg" if v<0 else ""
        if "percent" in lk:
            return f'<span class="{cls}">{v:.2f}%</span>'
        if any(x in lk for x in ["marketcap","revenue","income","value","cap","enterprise"]):
            return f'<span class="{cls}">₹{human_number(v)}</span>'
        return f'<span class="{cls}">{human_number(v)}</span>'
    # Strings
    if isinstance(v,str) and len(v)>80:
        return f'<div style="font-size:12px;">{v}</div>'
    return v

# ==============================
# HTML Helpers
# ==============================
def column_layout(html):
    return f"""
    <style>
        .grid{{display:grid;gap:10px;grid-template-columns:repeat(3,1fr);}}
        @media(max-width:1024px){{.grid{{grid-template-columns:repeat(2,1fr);}}}}
        @media(max-width:640px){{.grid{{grid-template-columns:1fr;}}}}
        .pos{{color:#0a7d32;font-weight:600;}}
        .neg{{color:#b00020;font-weight:600;}}
        .alert{{color:#d97706;font-weight:600;}}
    </style>
    <div class="grid">{html}</div>
    """
def html_card(title,body,mini=False):
    font = "12px" if mini else "14px"
    pad  = "6px" if mini else "10px"
    return f"""
    <div style="background:#e6f0fa;border:1px solid #a3c0e0;border-radius:8px;padding:{pad};
                font-size:{font};margin-bottom:6px;">
        <div style="font-weight:600;margin-bottom:6px;">{title}</div>{body}
    </div>
    """
def make_table(df):
    return "".join(
        f"""<div style="display:flex;justify-content:space-between;border-bottom:1px dashed #bcd0ea;padding:2px 0;">
            <span>{r.Field}</span><span>{r.Value}</span></div>"""
        for r in df.itertuples()
    )

# ==============================
# Data Helpers
# ==============================
def build_df_from_dict(data):
    rows = [(SHORT_NAMES.get(k,k[:16]), format_value(k,v)) for k,v in data.items() if k not in NOISE_KEYS]
    return pd.DataFrame(rows,columns=["Field","Value"])

def resolve_duplicates(data):
    DUP = {
        "price":["regularMarketPrice","currentPrice"],
        "prev":["regularMarketPreviousClose","previousClose"],
        "open":["regularMarketOpen","open"],
        "high":["regularMarketDayHigh","dayHigh"],
        "low":["regularMarketDayLow","dayLow"],
        "volume":["regularMarketVolume","volume"]
    }
    resolved, used = {}, set()
    for keys in DUP.values():
        for k in keys:
            if k in data:
                resolved[k] = data[k]
                used.update(keys)
                break
    for k,v in data.items():
        if k not in used:
            resolved[k] = v
    return resolved

def classify(k,v):
    lk = k.lower()
    if k=="companyOfficers": return "management"
    if any(x in lk for x in ["pe","pb","roe","roa","margin","debt","revenue","profit","eps","cap"]):
        return "fundamental"
    if isinstance(v,(int,float)): return "price_volume"
    if isinstance(v,str) and len(v)>80: return "long_text"
    return "profile"

def group_info(info):
    g = {"price_volume":{}, "fundamental":{}, "profile":{}, "management":{}, "long_text":{}}
    for k,v in info.items():
        if k in NOISE_KEYS or v in [None,"",[],{}]: continue
        g[classify(k,v)][k] = v
    return g

def split_df(df):
    n = len(df)
    cols = 1 if n<=6 else 2 if n<=14 else 3
    size = (n+cols-1)//cols
    return [df.iloc[i:i+size] for i in range(0,n,size)]

# ==============================
# Derived Metrics & Signals
# ==============================
def build_price_volume_derived(info):
    out={}
    price=info.get("regularMarketPrice")
    dma50=info.get("fiftyDayAverage")
    dma200=info.get("twoHundredDayAverage")
    low52=info.get("fiftyTwoWeekLow")
    high52=info.get("fiftyTwoWeekHigh")
    if price and dma50: out["vs 50DMA"]="Above ↑" if price>dma50 else "Below ↓"
    if price and dma200: out["vs 200DMA"]="Above ↑" if price>dma200 else "Below ↓"
    if price and low52 and high52 and high52!=low52: out["52W Pos"]=f"{(price-low52)/(high52-low52)*100:.1f}%"
    prev=info.get("regularMarketPreviousClose")
    high=info.get("regularMarketDayHigh")
    low=info.get("regularMarketDayLow")
    if price and prev: out["dailyGapPercent"]=(price-prev)/prev*100
    if high and low and price: out["dailyRangePercent"]=(high-low)/price*100
    vol=info.get("regularMarketVolume")
    if vol and price: out["VWAP"]=price
    if info.get("firstTradeDate"): out["firstTradeDate"]=info.get("firstTradeDate")
    return out

def build_smart_signals(info):
    rows=[]
    pe=info.get("trailingPE")
    roe=info.get("returnOnEquity")
    debt=info.get("debtToEquity")
    price=info.get("regularMarketPrice")
    dma50=info.get("fiftyDayAverage")
    dma200=info.get("twoHundredDayAverage")
    # Alerts
    if pe: rows.append(("Valuation",f'<span class="alert">{"Expensive" if pe>35 else "Cheap" if pe<15 else "Fair"}</span>'))
    if roe: rows.append(("Quality",f'<span class="alert">{"High" if roe>0.18 else "Average"}</span>'))
    if debt: rows.append(("Balance Sheet",f'<span class="alert">{"Weak" if debt>1 else "Healthy"}</span>'))
    if price and dma50 and dma200:
        trend = "Bullish" if price>dma50>dma200 else "Bearish" if price<dma50<dma200 else "Neutral"
        rows.append(("Momentum",f'<span class="alert">{trend}</span>'))
    return pd.DataFrame(rows,columns=["Field","Value"])

# ==============================
# Build Price/Volume Section
# ==============================
def build_price_volume_section(info,pv_data):
    df=build_df_from_dict(pv_data)
    derived=build_price_volume_derived(info)
    if derived: df=pd.concat([df,pd.DataFrame(derived.items(),columns=["Field","Value"])],ignore_index=True)
    cards=""
    for title,fields in PRICE_VOLUME_GROUPS.items():
        sub=df[df["Field"].isin(fields)]
        if not sub.empty: cards+=html_card(title,make_table(sub),mini=True)
    trend_df=df[df["Field"].isin(["vs 50DMA","vs 200DMA","52W Pos"])]
    if not trend_df.empty: cards+=html_card("Trend & Momentum",make_table(trend_df),mini=True)
    signals=build_smart_signals(info)
    if not signals.empty: cards+=html_card("Smart Signals",make_table(signals),mini=True)
    return column_layout(cards)

# ==============================
# Main Function
# ==============================
def fetch_info(symbol):
    key=f"info_{symbol}"
    if exists(key,"html"):
        cached=load(key,"html")
        if cached: return cached
    try:
        info=yfinfo(symbol)
        if "__error__" in info: return "No data"
        groups=group_info(info)
        html=""
        # Price / Volume
        pv=resolve_duplicates(groups["price_volume"])
        if pv: html+=html_card(f"{MAIN_ICONS['Price / Volume']} Price / Volume",build_price_volume_section(info,pv))
        # Fundamentals
        if groups["fundamental"]:
            df=build_df_from_dict(groups["fundamental"])
            html+=html_card(f"{MAIN_ICONS['Fundamentals']} Fundamentals",
                            column_layout("".join(html_card("Fundamentals",make_table(c),mini=True) for c in split_df(df))))
        # Company Profile
        if groups["profile"]:
            df=build_df_from_dict(groups["profile"])
            html+=html_card(f"{MAIN_ICONS['Company Profile']} Company Profile",
                            column_layout("".join(html_card("Profile",make_table(c),mini=True) for c in split_df(df))))
        # Management
        if groups["management"].get("companyOfficers"):
            cards=""
            for o in groups["management"]["companyOfficers"]:
                cards+=html_card(o.get("name",""),o.get("title",""),mini=True)
            html+=html_card(f"{MAIN_ICONS['Management']} Management",column_layout(cards))
        # Long Text
        for k,v in groups["long_text"].items():
            html+=html_card(SHORT_NAMES.get(k,k[:16]),v)
        save(key,html,"html")
        return html
    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>"
