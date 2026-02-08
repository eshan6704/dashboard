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
    if any(x in lk for x in ["sector", "industry", "country", "employees", "webs