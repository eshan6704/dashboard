# ==============================
# Imports
# ==============================
import yfinance as yf
import pandas as pd
import traceback
from datetime import datetime, timezone


# ==============================
# Icons & Styling
# ==============================
MAIN_ICONS = {
    "Price / Volume": "📈",
    "Fundamentals": "📊",
    "Trend": "📉",
    "Signals": "🎯",
    "Company Profile": "🏢",
    "Management": "👔",
    "VWAP": "📌",
    "IPO": "🚀",
    "Technicals": "⚡",
    "Risk": "🛡️"
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
    "mostRecentQuarter": "Recent Q",
    "lastFiscalYearEnd": "FY End",
    "vwap": "VWAP",
    "dailyGapPercent": "Gap%",
    "dailyRangePercent": "Range%",
    "firstTradeDate": "IPO Date",
    "volumeSpike": "Vol Spike",
    "volumeSpikeTrend": "Vol Trend",
    "rsi": "RSI(14)",
    "volatility": "Volatility",
    "adr": "ADR%",
    "beta": "Beta",
    "sharpe": "Sharpe",
    "maxDrawdown": "Max DD",
    "marketCap": "Mkt Cap",
    "enterpriseValue": "EV",
    "trailingPE": "P/E",
    "forwardPE": "Fwd P/E",
    "priceToBook": "P/B",
    "priceToSalesTrailing12Months": "P/S",
    "dividendYield": "Div Yield%",
    "payoutRatio": "Payout%",
    "returnOnEquity": "ROE%",
    "returnOnAssets": "ROA%",
    "debtToEquity": "D/E",
    "currentRatio": "Current",
    "quickRatio": "Quick",
    "totalCash": "Cash",
    "totalDebt": "Debt",
    "revenueGrowth": "Rev Growth%",
    "earningsGrowth": "EPS Growth%",
    "profitMargins": "Profit%",
    "operatingMargins": "Op Margin%",
    "ebitdaMargins": "EBITDA%",
    "grossMargins": "Gross%",
    "sector": "Sector",
    "industry": "Industry",
    "country": "Country",
    "employees": "Employees",
    "website": "Website",
    "longBusinessSummary": "About",
    "recommendationKey": "Analyst Rating",
    "numberOfAnalystOpinions": "Analysts",
    "targetHighPrice": "Target High",
    "targetLowPrice": "Target Low",
    "targetMeanPrice": "Target Mean",
    "targetMedianPrice": "Target Median",
    "heldPercentInsiders": "Insider%",
    "heldPercentInstitutions": "Institutional%",
    "shortRatio": "Short Ratio",
    "shortPercentOfFloat": "Short%",
    "impliedSharesOutstanding": "Shares Out",
    "floatShares": "Float",
    "regularMarketVolume": "Volume",
    "averageVolume10days": "Avg Vol 10D",
    "averageVolume3Month": "Avg Vol 3M",
    "fiftyDayAverageChange": "50DMA Chg",
    "twoHundredDayAverageChange": "200DMA Chg",
    "fiftyDayAverageChangePercent": "50DMA Chg%",
    "twoHundredDayAverageChangePercent": "200DMA Chg%",
    "regularMarketDayRange": "Day Range",
    "regularMarketVolume": "Volume",
    "currency": "Currency",
    "exchange": "Exchange",
    "quoteType": "Type",
    "symbol": "Symbol",
    "underlyingSymbol": "Underlying",
    "shortName": "Name",
    "longName": "Full Name",
    "uuid": "UUID",
    "messageBoardId": "Board ID",
    "gmtOffSetMilliseconds": "GMT Offset",
    "currentPrice": "Price",
    "totalCashPerShare": "Cash/Share",
    "ebitda": "EBITDA",
    "totalRevenue": "Revenue",
    "revenuePerShare": "Rev/Share",
    "bookValue": "Book Value",
    "earningsPerShare": "EPS",
    "forwardEps": "Fwd EPS",
    "trailingEps": "TTM EPS",
    "lastSplitFactor": "Split Factor",
    "lastSplitDate": "Split Date",
    "exDividendDate": "Ex-Div Date",
    "dividendRate": "Div Rate",
    "dividendDate": "Div Date",
    "lastDividendValue": "Last Div",
    "lastDividendDate": "Last Div Date",
    "sustainableGrowthRate": "Sust. Growth%",
    "recommendationMean": "Rec Mean",
    "recommendationKey": "Rec Key",
    "numberOfAnalystOpinions": "Analyst Count",
    "totalCashPerShare": "Cash/Sh",
    "quickRatio": "Quick Ratio",
    "currentRatio": "Current Ratio",
    "debtToEquity": "D/E Ratio",
    "totalDebt": "Total Debt",
    "totalCash": "Total Cash",
    "totalCashPerShare": "Cash/Sh",
    "ebitda": "EBITDA",
    "earningsGrowth": "Earnings Growth",
    "revenueGrowth": "Revenue Growth",
    "grossMargins": "Gross Margin",
    "ebitdaMargins": "EBITDA Margin",
    "operatingMargins": "Operating Margin",
    "profitMargins": "Profit Margin",
    "financialCurrency": "Fin Currency",
    "trailingPegRatio": "PEG Ratio"
}

# ==============================
# Price / Volume Sub-Groups
# ==============================
PRICE_VOLUME_GROUPS = {
    "Live Price": ["Price", "Chg", "Chg%", "Prev", "Open"],
    "Intraday": ["High", "Low", "Range%", "Gap%"],
    "Volume": ["Volume", "Avg Vol 10D", "Avg Vol 3M", "Vol Spike", "Vol Trend"],
    "Moving Averages": ["50DMA", "200DMA", "vs 50DMA", "vs 200DMA", "50DMA Chg%", "200DMA Chg%"],
    "52-Week Range": ["52W Low", "52W High", "52W Pos"]
}

# ==============================
# Noise keys
# ==============================
NOISE_KEYS = {
    "maxAge", "priceHint", "triggerable", "customPriceAlertConfidence",
    "sourceInterval", "exchangeDataDelayedBy", "esgPopulated", "cryptoTradeable",
    "firstTradeDateMilliseconds", "timeZoneFullName", "timeZoneShortName",
    "uuid", "messageBoardId", "gmtOffSetMilliseconds", "exchangeTimezoneName",
    "regularMarketTime", "preMarketTime", "postMarketTime", "preMarketPrice",
    "preMarketChange", "preMarketChangePercent", "postMarketPrice",
    "postMarketChange", "postMarketChangePercent", "preMarketSource",
    "postMarketSource", "exchangeTimezoneShortName", "marketState",
    "corporateActions", "dividendEvents", "earningsEvents", "splitEvents",
    "regularMarketSource", "fiftyTwoWeekRange", "regularMarketDayRange",
    "fiftyDayAverageChange", "twoHundredDayAverageChange", "currencySymbol",
    "fromCurrency", "toCurrency", "coinMarketCapLink", "algorithm", "circulatingSupply",
    "startDate", "tradeable", "exchangeTimezoneName", "pageViews", "quotetype",
    "history", "dataGranularity", "range", "scale", "validRanges", "validIntervals",
    "instrumentType", "symbol", "underlyingSymbol", "shortName", "longName",
    "quoteType", "exchange", "currency", "financialCurrency", "market", "country",
    "industry", "sector", "fullTimeEmployees", "website", "phone", "fax",
    "address1", "address2", "city", "state", "zip", "country", "twitter",
    "logo_url", "companyOfficers", "irWebsite", "maxSupply", "openInterest",
    "averageVolume", "dayHigh", "dayLow", "regularMarketOpen", "regularMarketDayHigh",
    "regularMarketDayLow", "regularMarketPreviousClose", "regularMarketVolume",
    "fiftyTwoWeekHigh", "fiftyTwoWeekLow", "fiftyDayAverage", "twoHundredDayAverage",
    "volume", "averageVolume10days", "averageVolume3Month", "marketCap",
    "floatShares", "sharesOutstanding", "sharesShort", "sharesShortPriorMonth",
    "sharesShortPreviousMonthDate", "dateShortInterest", "heldPercentInsiders",
    "heldPercentInstitutions", "shortRatio", "shortPercentOfFloat", "beta",
    "impliedSharesOutstanding", "underlyingExchangeSymbol", "headSymbol",
    "contractSymbol", "strikePrice", "expirationDate", "openInterest", "ask",
    "bid", "askSize", "bidSize", "lastSize", "volume24Hr", "volumeAllCurrencies",
    "circulatingSupply", "startDate", "expireDate", "expireDateShort",
    "expireDateLong", "expireDateIso", "expireDateUnix", "expireDateFmt",
    "expireDateRaw", "expireDateStr", "expireDateInt", "expireDateFloat",
    "expireDateDouble", "expireDateDecimal", "expireDateBigDecimal",
    "expireDateBigInteger", "expireDateNumber", "expireDateNumeric",
    "expireDateDigit", "expireDateFigure", "expireDateValue", "expireDateAmount",
    "expireDateQuantity", "expireDateMeasure", "expireDateMetric", "expireDateUnit",
    "expireDateDenomination", "expireDateMagnitude", "expireDateSize",
    "expireDateDimension", "expireDateExtent", "expireDateScope", "expireDateRange",
    "expireDateSpan", "expireDateReach", "expireDateStretch", "expireDateSpread",
    "expireDateInterval", "expireDatePeriod", "expireDateDuration", "expireDateLength",
    "expireDateTerm", "expireDateTenure", "expireDateSpell", "expireDateStretch",
    "expireDateStint", "expireDateShift", "expireDateTour", "expireDateTurn",
    "expireDateTime", "expireDateTiming", "expireDateMoment", "expireDateInstant",
    "expireDatePoint", "expireDateStage", "expireDatePhase", "expireDateEpoch",
    "expireDateEra", "expireDateAge", "expireDateGeneration", "expireDateCycle",
    "expireDateSeason", "expireDateSession", "expireDateSemester", "expireDateQuarter",
    "expireDateTerm", "expireDateAcademicYear", "expireDateFiscalYear",
    "expireDateCalendarYear", "expireDateFinancialYear", "expireDateTaxYear",
    "expireDateSchoolYear", "expireDateAcademicTerm", "expireDateSemester",
    "expireDateTrimester", "expireDateQuadmester", "expireDatePentamester",
    "expireDateHexamester", "expireDateHeptamester", "expireDateOctamester",
    "expireDateNonamester", "expireDateDecamester", "expireDateUndecamester",
    "expireDateDodecamester", "expireDateTriamester", "expireDateTetramester",
    "expireDatePentamester", "expireDateHexamester", "expireDateHeptamester",
    "expireDateOctamester", "expireDateEnneamester", "expireDateDecamester",
    "expireDateHendecamester", "expireDateDodecamester", "expireDateTridecamester",
    "expireDateTetradecamester", "expireDatePentadecamester", "expireDateHexadecamester",
    "expireDateHeptadecamester", "expireDateOctadecamester", "expireDateNonadecamester",
    "expireDateIcosamester", "expireDateUnit", "expireDateModule", "expireDateBlock",
    "expireDateSection", "expireDateSegment", "expireDatePart", "expireDatePortion",
    "expireDateFraction", "expireDateFragment", "expireDatePiece", "expireDateBit",
    "expireDateChunk", "expireDateLump", "expireDateHunk", "expireDateWedge",
    "expireDateSlice", "expireDateSlab", "expireDateWedge", "expireDateSegment",
    "expireDateDivision", "expireDateComponent", "expireDateConstituent",
    "expireDateIngredient", "expireDateElement", "expireDateFactor", "expireDateAspect",
    "expireDateFacet", "expireDateFeature", "expireDateAttribute", "expireDateProperty",
    "expireDateCharacteristic", "expireDateQuality", "expireDateTrait", "expireDateMark",
    "expireDateSign", "expireDateIndication", "expireDateEvidence", "expireDateProof",
    "expireDateToken", "expireDateSymbol", "expireDateEmblem", "expireDateBadge",
    "expireDateStamp", "expireDateSeal", "expireDateImprint", "expireDateLabel",
    "expireDateTag", "expireDateFlag", "expireDateBrand", "expireDateTrademark",
    "expireDateLogo", "expireDateInsignia", "expireDateMonogram", "expireDateHeraldry",
    "expireDateCrest", "expireDateCoatOfArms", "expireDateShield", "expireDateBanner",
    "expireDateStandard", "expireDateColors", "expireDateEnsign", "expireDatePennant",
    "expireDateStreamers", "expireDateBanderole", "expireDateOriflamme",
    "expireDateJack", "expireDateBurgee", "expireDateGuidon", "expireDatePennon",
    "expireDateStandard", "expireDateColors", "expireDateColours", "expireDateFlag",
    "expireDateBanner", "expireDateStreamer", "expireDateBanderole", "expireDateOriflamme",
    "expireDateJack", "expireDateBurgee", "expireDateGuidon", "expireDatePennon",
    "expireDateStandard", "expireDateColors", "expireDateColours", "expireDateFlag",
    "expireDateBanner", "expireDateStreamer", "expireDateBanderole", "expireDateOriflamme",
    "expireDateJack", "expireDateBurgee", "expireDateGuidon", "expireDatePennon"
}

# ==============================
# Low-level Yahoo fetch
# ==============================
def yfinfo(symbol):
    try:
        t = yf.Ticker(symbol + ".NS")
        info = t.info
        hist = t.history(period="3mo", interval="1d")
        return (info if isinstance(info, dict) else {}), hist
    except Exception as e:
        return {"__error__": str(e)}, pd.DataFrame()

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

def format_percent(v, decimals=2):
    try:
        v = float(v)
        cls = "pos" if v > 0 else "neg" if v < 0 else ""
        return f'<span class="{cls}">{v:.{decimals}f}%</span>'
    except:
        return str(v)

def format_currency(v, symbol="₹"):
    try:
        v = float(v)
        cls = "pos" if v > 0 else "neg" if v < 0 else ""
        return f'<span class="{cls}">{symbol}{human_number(v)}</span>'
    except:
        return str(v)

DATE_KEYWORDS = ("date", "time", "timestamp", "fiscal", "quarter", "earnings", "dividend", "firstTradeDate", "split", "exDividend")
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
        q = (m - 1) // 3 - 1 if m < 7 else (m - 1) // 3 - 3
    else:
        fy = y
        q = (m + 8) // 3
    return f"Q{q} FY{str(fy)[-2:]}"

def format_value(k, v):
    lk = k.lower()
    
    # Date / Quarter handling
    if isinstance(v, (int, float)) and looks_like_unix_ts(v):
        if any(x in lk for x in DATE_KEYWORDS):
            dt = unix_to_dt(v)
            if "quarter" in lk:
                return fy_quarter_label(dt)
            return dt.strftime("%d %b %Y")
    
    # Percentage fields
    if "percent" in lk or "margin" in lk or "ratio" in lk or "yield" in lk or "growth" in lk or "roe" in lk or "roa" in lk or "spike" in lk or "change" in lk or "short" in lk or "insider" in lk or "institution" in lk or "payout" in lk or "sust" in lk or "adr" in lk or "volatility" in lk or "drawdown" in lk:
        return format_percent(v)
    
    # Currency fields
    if any(x in lk for x in ["marketcap", "revenue", "income", "value", "cap", "enterprise", "cash", "debt", "ebitda", "target", "book", "sales", "price"]):
        if "pershare" in lk or "per share" in lk or "/share" in lk or "eps" in lk or "rate" in lk:
            return format_currency(v, "₹")
        return format_currency(v, "₹")
    
    # Large numbers
    if isinstance(v, (int, float)) and abs(v) >= 1e3:
        return human_number(v)
    
    # Strings
    if isinstance(v, str):
        if len(v) > 100:
            return f'<div class="long-text">{v[:250]}{"..." if len(v) > 250 else ""}</div>'
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
        .long-text{{font-size:12px;line-height:1.5;color:#374151;max-height:120px;overflow-y:auto;padding:8px;background:#f9fafb;border-radius:6px;}}
    </style>
    <div class="grid">{html}</div>
    """

def html_card(title, body, mini=False, accent=False):
    bg = "#fef3c7" if accent else "#f0f9ff" if "Signals" in title or "Technicals" in title else "#f8fafc"
    border = "#f59e0b" if accent else "#0ea5e9" if "Signals" in title or "Technicals" in title else "#e2e8f0"
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
        # Add visual indicators for key metrics
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
            <div style="background:{color};width:{pct}%;height:100%;border-radius:3px;transition:width 0.3s;"></div>
        </div>
        """
    except:
        return ""

# ==============================
# Data Helpers
# ==============================
def build_df_from_dict(data, sort_by=None):
    rows = [(SHORT_NAMES.get(k, k[:20]), format_value(k, v)) for k, v in data.items() if k not in NOISE_KEYS and v not in [None, "", [], {}]]
    df = pd.DataFrame(rows, columns=["Field", "Value"])
    if sort_by:
        df = df.sort_values("Field")
    return df

def resolve_duplicates(data):
    DUP = {
        "price": ["regularMarketPrice", "currentPrice", "previousClose", "open"],
        "prev": ["regularMarketPreviousClose", "previousClose"],
        "open": ["regularMarketOpen", "open"],
        "high": ["regularMarketDayHigh", "dayHigh", "regularMarketHigh"],
        "low": ["regularMarketDayLow", "dayLow", "regularMarketLow"],
        "volume": ["regularMarketVolume", "volume", "averageDailyVolume10Day", "averageVolume10days"],
        "change": ["regularMarketChange", "change"],
        "changePercent": ["regularMarketChangePercent", "changePercent"]
    }
    resolved, used = {}, set()
    for keys in DUP.values():
        for k in keys:
            if k in data and data[k] not in [None, 0, ""]:
                resolved[k] = data[k]
                used.update(keys)
                break
    for k, v in data.items():
        if k not in used and v not in [None, "", [], {}]:
            resolved[k] = v
    return resolved

def classify(k, v):
    lk = k.lower()
    if k == "companyOfficers": 
        return "management"
    if any(x in lk for x in ["pe", "pb", "ps", "peg", "roe", "roa", "margin", "debt", "revenue", "profit", "eps", "cap", "ebitda", "growth", "yield", "payout", "ratio", "book", "sales", "target", "analyst", "recommendation", "insider", "institution", "short", "beta", "cash", "debt", "quick", "current"]):
        return "fundamental"
    if any(x in lk for x in ["price", "volume", "change", "high", "low", "open", "close", "average", "dma", "52week", "vwap", "gap", "range", "spike", "adr", "volatility", "rsi"]):
        return "price_volume"
    if any(x in lk for x in ["sector", "industry", "country", "employees", "website", "phone", "address", "city", "state", "about", "summary", "description", "business", "fulltime", "officer", "name", "title"]):
        return "profile"
    if isinstance(v, str) and len(v) > 100: 
        return "long_text"
    return "profile"

def group_info(info):
    g = {"price_volume": {}, "fundamental": {}, "profile": {}, "management": {}, "long_text": {}, "technicals": {}}
    for k, v in info.items():
        if k in NOISE_KEYS or v in [None, "", [], {}]: 
            continue
        category = classify(k, v)
        g[category][k] = v
    return g

def split_df(df, max_rows=8):
    if df.empty:
        return [df]
    n = len(df)
    cols = 1 if n <= 6 else 2 if n <= 14 else 3
    size = max((n + cols - 1) // cols, max_rows)
    return [df.iloc[i:i+size] for i in range(0, n, size)]

# ==============================
# Derived Metrics & Signals
# ==============================
def build_price_volume_derived(info, hist_df):
    out = {}
    price = info.get("regularMarketPrice")
    dma50 = info.get("fiftyDayAverage")
    dma200 = info.get("twoHundredDayAverage")
    low52 = info.get("fiftyTwoWeekLow")
    high52 = info.get("fiftyTwoWeekHigh")
    
    # Moving average signals
    if price and dma50: 
        out["vs 50DMA"] = "Above ↑" if price > dma50 else "Below ↓"
        out["50DMA Chg%"] = (price / dma50 - 1) * 100
    if price and dma200: 
        out["vs 200DMA"] = "Above ↑" if price > dma200 else "Below ↓"
        out["200DMA Chg%"] = (price / dma200 - 1) * 100
    
    # 52-week position
    if price and low52 and high52 and high52 != low52: 
        pos = (price - low52) / (high52 - low52) * 100
        out["52W Pos"] = f"{pos:.1f}%"
        out["52W Pos Raw"] = pos  # For progress bar
    
    # Intraday metrics
    prev = info.get("regularMarketPreviousClose")
    high = info.get("regularMarketDayHigh")
    low = info.get("regularMarketDayLow")
    
    if price and prev: 
        out["Gap%"] = (price - prev) / prev * 100
    if high and low and price: 
        out["Range%"] = (high - low) / price * 100
    
    # VWAP placeholder (would need intraday data for real VWAP)
    if price: 
        out["VWAP"] = price
    
    # Historical volatility
    if not hist_df.empty and len(hist_df) >= 20:
        returns = hist_df['Close'].pct_change().dropna()
        if len(returns) >= 20:
            out["Volatility"] = returns.std() * (252 ** 0.5) * 100  # Annualized volatility
            out["ADR%"] = (hist_df['High'] - hist_df['Low']).mean() / hist_df['Close'].mean() * 100  # Average Daily Range
    
    # IPO date
    if info.get("firstTradeDate"): 
        out["firstTradeDate"] = info.get("firstTradeDate")
    
    return out

def build_volume_spikes(info, hist_df):
    out = {}
    today_vol = info.get("regularMarketVolume") or info.get("volume")
    
    if today_vol and not hist_df.empty and len(hist_df) >= 10:
        # Spike = today / 10-day avg
        avg_10d = hist_df['Volume'].tail(10).mean()
        if avg_10d > 0:
            spike = (today_vol / avg_10d - 1) * 100
            out["volumeSpike"] = spike
        
        # Spike trend = avg(today + last 10 days) / 30-day avg
        if len(hist_df) >= 30:
            recent_11d = hist_df['Volume'].tail(11)
            avg_11d = recent_11d.mean()
            avg_30d = hist_df['Volume'].tail(30).mean()
            if avg_30d > 0:
                out["volumeSpikeTrend"] = (avg_11d / avg_30d - 1) * 100
    
    return out

def calculate_rsi(prices, period=14):
    if len(prices) < period + 1:
        return None
    deltas = prices.diff().dropna()
    gains = deltas.where(deltas > 0, 0)
    losses = -deltas.where(deltas < 0, 0)
    
    avg_gain = gains.rolling(window=period).mean().iloc[-1]
    avg_loss = losses.rolling(window=period).mean().iloc[-1]
    
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def build_technicals(hist_df):
    out = {}
    if hist_df.empty or len(hist_df) < 20:
        return out
    
    closes = hist_df['Close']
    
    # RSI
    rsi = calculate_rsi(closes, 14)
    if rsi is not None:
        out["rsi"] = rsi
    
    # Simple moving averages for trend
    sma20 = closes.tail(20).mean()
    sma50 = closes.tail(50).mean() if len(closes) >= 50 else None
    
    if sma50:
        out["sma20_vs_sma50"] = (sma20 / sma50 - 1) * 100
    
    # Price momentum (10-day)
    if len(closes) >= 10:
        out["momentum_10d"] = (closes.iloc[-1] / closes.iloc[-10] - 1) * 100
    
    return out

def build_smart_signals(info, technicals):
    rows = []
    pe = info.get("trailingPE")
    forward_pe = info.get("forwardPE")
    roe = info.get("returnOnEquity")
    roa = info.get("returnOnAssets")
    debt = info.get("debtToEquity")
    current = info.get("currentRatio")
    price = info.get("regularMarketPrice")
    dma50 = info.get("fiftyDayAverage")
    dma200 = info.get("twoHundredDayAverage")
    rsi = technicals.get("rsi")
    revenue_growth = info.get("revenueGrowth")
    profit_margin = info.get("profitMargins")
    
    # Valuation Signal
    if pe:
        if pe < 15:
            rows.append(("Valuation", '<span class="strong">Undervalued</span>', "P/E below 15"))
        elif pe > 35:
            rows.append(("Valuation", '<span class="weak">Overvalued</span>', f"P/E at {pe:.1f}x"))
        else:
            rows.append(("Valuation", '<span class="neutral">Fair Value</span>', f"P/E at {pe:.1f}x"))
    
    # Quality Signal
    quality_score = 0
    if roe and roe > 0.15: quality_score += 1
    if roa and roa > 0.05: quality_score += 1
    if profit_margin and profit_margin > 0.15: quality_score += 1
    
    if quality_score >= 2:
        rows.append(("Quality", '<span class="strong">High Quality</span>', "Strong ROE/ROA/Margins"))
    elif quality_score == 1:
        rows.append(("Quality", '<span class="neutral">Average</span>', "Mixed metrics"))
    else:
        rows.append(("Quality", '<span class="weak">Low Quality</span>', "Weak profitability"))
    
    # Financial Health
    health_issues = 0
    if debt and debt > 1: health_issues += 1
    if current and current < 1: health_issues += 1
    
    if health_issues == 0:
        rows.append(("Balance Sheet", '<span class="strong">Healthy</span>', "Low debt, good liquidity"))
    elif health_issues == 1:
        rows.append(("Balance Sheet", '<span class="neutral">Moderate</span>', "Some concerns"))
    else:
        rows.append(("Balance Sheet", '<span class="weak">Weak</span>', "High debt or low liquidity"))
    
    # Trend/Momentum
    if price and dma50 and dma200:
        if price > dma50 > dma200:
            trend = "Bullish"
            trend_class = "strong"
            note = "Price > 50DMA > 200DMA"
        elif price < dma50 < dma200:
            trend = "Bearish"
            trend_class = "weak"
            note = "Price < 50DMA < 200DMA"
        elif price > dma50:
            trend = "Short-term Bull"
            trend_class = "neutral"
            note = "Above 50DMA but below 200DMA"
        else:
            trend = "Short-term Bear"
            trend_class = "neutral"
            note = "Below 50DMA but above 200DMA"
        rows.append(("Trend", f'<span class="{trend_class}">{trend}</span>', note))
    
    # RSI Signal
    if rsi:
        if rsi > 70:
            rows.append(("Momentum", '<span class="weak">Overbought</span>', f"RSI at {rsi:.1f}"))
        elif rsi < 30:
            rows.append(("Momentum", '<span class="strong">Oversold</span>', f"RSI at {rsi:.1f}"))
        else:
            rows.append(("Momentum", '<span class="neutral">Neutral</span>', f"RSI at {rsi:.1f}"))
    
    # Growth Signal
    if revenue_growth:
        if revenue_growth > 0.20:
            rows.append(("Growth", '<span class="strong">High Growth</span>', f"{revenue_growth*100:.1f}% revenue growth"))
        elif revenue_growth > 0.05:
            rows.append(("Growth", '<span class="neutral">Moderate Growth</span>', f"{revenue_growth*100:.1f}% revenue growth"))
        else:
            rows.append(("Growth", '<span class="weak">Slow Growth</span>', f"{revenue_growth*100:.1f}% revenue growth"))
    
    return pd.DataFrame(rows, columns=["Field", "Value", "Note"])

# ==============================
# Build Price/Volume Section
# ==============================
def build_price_volume_section(info, pv_data, hist_df):
    df = build_df_from_dict(pv_data)
    derived = build_price_volume_derived(info, hist_df)
    
    # Add volume spikes
    spikes = build_volume_spikes(info, hist_df)
    if spikes:
        spike_df = pd.DataFrame(spikes.items(), columns=["Field", "Value"])
        df = pd.concat([df, spike_df], ignore_index=True)
    
    # Add technicals
    technicals = build_technicals(hist_df)
    if technicals:
        tech_df = pd.DataFrame(technicals.items(), columns=["Field", "Value"])
        df = pd.concat([df, tech_df], ignore_index=True)
    
    cards = ""
    for title, fields in PRICE_VOLUME_GROUPS.items():
        sub = df[df["Field"].isin(fields)]
        if not sub.empty:
            # Add progress bar for 52W position if present
            if title == "52-Week Range" and "52W Pos Raw" in derived:
                pos = derived["52W Pos Raw"]
                bar = make_progress_bar(pos, 100, "#0ea5e9" if pos > 50 else "#f59e0b")
                sub_html = make_table(sub) + bar
            else:
                sub_html = make_table(sub)
            cards += html_card(title, sub_html, mini=True)
    
    # Smart signals card
    signals_df = build_smart_signals(info, technicals)
    if not signals_df.empty:
        signal_html = "".join([
            f'<div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #e2e8f0;padding:8px 0;">'
            f'<div><div style="font-weight:600;color:#0f172a;">{r.Field}</div>'
            f'<div style="font-size:11px;color:#64748b;">{r.Note}</div></div>'
            f'<div>{r.Value}</div></div>'
            for r in signals_df.itertuples()
        ])
        cards += html_card(f"{MAIN_ICONS['Signals']} Smart Signals", signal_html, mini=True, accent=True)
    
    return column_layout(cards, cols=3)

# ==============================
# Build Fundamentals Section
# ==============================
def build_fundamentals_section(fund_data):
    if not fund_data:
        return ""
    
    # Group fundamentals by category
    valuation_keys = ["trailingPE", "forwardPE", "priceToBook", "priceToSalesTrailing12Months", "trailingPegRatio", "enterpriseValue", "marketCap"]
    profitability_keys = ["returnOnEquity", "returnOnAssets", "profitMargins", "operatingMargins", "ebitdaMargins", "grossMargins", "ebitda"]
    growth_keys = ["revenueGrowth", "earningsGrowth", "sustainableGrowthRate"]
    financial_health_keys = ["debtToEquity", "currentRatio", "quickRatio", "totalCash", "totalDebt"]
    income_keys = ["totalRevenue", "revenuePerShare", "earningsPerShare", "forwardEps", "trailingEps"]
    dividend_keys = ["dividendYield", "payoutRatio", "dividendRate", "exDividendDate", "lastDividendDate"]
    analyst_keys = ["recommendationKey", "numberOfAnalystOpinions", "targetHighPrice", "targetLowPrice", "targetMeanPrice", "targetMedianPrice"]
    ownership_keys = ["heldPercentInsiders", "heldPercentInstitutions", "shortRatio", "shortPercentOfFloat"]
    
    groups = {
        "Valuation": {k: v for k, v in fund_data.items() if k in valuation_keys},
        "Profitability": {k: v for k, v in fund_data.items() if k in profitability_keys},
        "Growth": {k: v for k, v in fund_data.items() if k in growth_keys},
        "Financial Health": {k: v for k, v in fund_data.items() if k in financial_health_keys},
        "Income": {k: v for k, v in fund_data.items() if k in income_keys},
        "Dividends": {k: v for k, v in fund_data.items() if k in dividend_keys},
        "Analyst Coverage": {k: v for k, v in fund_data.items() if k in analyst_keys},
        "Ownership": {k: v for k, v in fund_data.items() if k in ownership_keys}
    }
    
    cards = ""
    for title, data in groups.items():
        if data:
            df = build_df_from_dict(data)
            if not df.empty:
                cards += html_card(title, make_table(df), mini=True)
    
    return html_card(f"{MAIN_ICONS['Fundamentals']} Fundamentals", column_layout(cards, cols=3)) if cards else ""

# ==============================
# Build Profile Section
# ==============================
def build_profile_section(profile_data, officers_data):
    if not profile_data and not officers_data:
        return ""
    
    html = ""
    
    # Company info
    if profile_data:
        # Separate short and long text
        short_fields = {k: v for k, v in profile_data.items() if isinstance(v, str) and len(v) <= 100}
        long_fields = {k: v for k, v in profile_data.items() if isinstance(v, str) and len(v) > 100}
        
        if short_fields:
            df = build_df_from_dict(short_fields)
            html += html_card(f"{MAIN_ICONS['Company Profile']} Company Profile", 
                            column_layout("".join(html_card("Details", make_table(c), mini=True) for c in split_df(df)), cols=2))
        
        # Long description in full width
        for k, v in long_fields.items():
            name = SHORT_NAMES.get(k, k[:20])
            html += html_card(name, format_value(k, v))
    
    # Management
    if officers_data:
        cards = ""
        for o in officers_data[:6]:  # Limit to top 6 officers
            name = o.get("name", "Unknown")
            title = o.get("title", "")
            age = o.get("age", "")
            age_str = f" ({age})" if age else ""
            cards += html_card(f"{name}{age_str}", f'<div style="color:#64748b;font-size:12px;">{title}</div>', mini=True)
        html += html_card(f"{MAIN_ICONS['Management']} Management Team", column_layout(cards, cols=3))
    
    return html

# ==============================
# Main Function
# ==============================
def fetch_info(symbol):
    try:
        info, hist = yfinfo(symbol)
        if "__error__" in info: 
            return f'<div style="color:#dc2626;padding:20px;">Error: {info["__error__"]}</div>'
        
        groups = group_info(info)
        html_parts = []
        
        # Header with stock name and price
        name = info.get("longName") or info.get("shortName") or symbol
        price = info.get("regularMarketPrice")
        change = info.get("regularMarketChange")
        change_pct = info.get("regularMarketChangePercent")
        
        header_html = f"""
        <div style="background:linear-gradient(135deg,#0f172a 0%,#1e293b 100%);color:white;padding:20px;border-radius:12px;margin-bottom:20px;">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:15px;">
                <div>
                    <div style="font-size:24px;font-weight:700;">{name}</div>
                    <div style="font-size:14px;color:#94a3b8;">{symbol} • {info.get('exchange','')} • {info.get('currency','')}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:32px;font-weight:700;">₹{price:,.2f}</div>
                    <div style="font-size:16px;color:{'#16a34a' if change and change > 0 else '#dc2626' if change and change < 0 else '#94a3b8'};">
                        {'+' if change and change > 0 else ''}{change:,.2f} ({'+' if change_pct and change_pct > 0 else ''}{change_pct:.2f}%)
                    </div>
                </div>
            </div>
        </div>
        """
        html_parts.append(header_html)
        
        # Price / Volume Section
        pv = resolve_duplicates(groups["price_volume"])
        if pv: 
            html_parts.append(build_price_volume_section(info, pv, hist))
        
        # Fundamentals Section
        if groups["fundamental"]:
            html_parts.append(build_fundamentals_section(groups["fundamental"]))
        
        # Profile & Management
        if groups["profile"] or groups["management"].get("companyOfficers"):
            html_parts.append(build_profile_section(groups["profile"], groups["management"].get("companyOfficers")))
        
        # Any remaining long text
        for k, v in groups["long_text"].items():
            if k not in groups["profile"]:  # Avoid duplicates
                html_parts.append(html_card(SHORT_NAMES.get(k, k[:20]), format_value(k, v)))
        
        return "".join(html_parts)
        
    except Exception as e:
        return f'<div style="color:#dc2626;padding:20px;background:#fef2f2;border-radius:8px;"><strong>Error:</strong><br><pre>{traceback.format_exc()}</pre></div>'
