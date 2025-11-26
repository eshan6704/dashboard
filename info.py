# info.py
import yfinance as yf
from common import format_large_number, format_timestamp_to_date, wrap_html, STYLE_BLOCK

def fetch_info(symbol):
    yfsymbol = f"{symbol}.NS"
    try:
        ticker = yf.Ticker(yfsymbol)
        info = ticker.info
        if not info:
            content_html = "<h1>No info available</h1>"
        else:
            long_summary = info.pop("longBusinessSummary", None)
            officers = info.pop("companyOfficers", None)
            
            # Categories
            info_categories = {
                "Company Overview": [
                    "longName", "symbol", "exchange", "quoteType", "sector", "industry",
                    "fullTimeEmployees", "website", "address1", "city", "state", "zip", "country", "phone"
                ],
                "Valuation Metrics": [
                    "marketCap", "enterpriseValue", "trailingPE", "forwardPE", "pegRatio",
                    "priceToSalesTrailing12Months", "enterpriseToRevenue", "enterpriseToEbitda"
                ],
                "Key Financials": [
                    "fiftyTwoWeekHigh", "fiftyTwoWeekLow", "fiftyDayAverage", "twoHundredDayAverage",
                    "trailingAnnualDividendRate", "trailingAnnualDividendYield", "dividendRate", "dividendYield",
                    "exDividendDate", "lastSplitFactor", "lastSplitDate", "lastDividendValue", "payoutRatio",
                    "beta", "sharesOutstanding", "impliedSharesOutstanding"
                ],
                "Operational Details": [
                    "auditRisk", "boardRisk", "compensationRisk", "shareHolderRightsRisk", "overallRisk",
                    "governanceEpochDate", "compensationAsOfEpochDate"
                ],
                "Trading Information": [
                    "open", "previousClose", "dayLow", "dayHigh", "volume", "averageVolume", "averageVolume10days",
                    "fiftyTwoWeekChange", "SandP52WeekChange", "currency", "regularMarketDayLow",
                    "regularMarketDayHigh", "regularMarketOpen", "regularMarketPreviousClose",
                    "regularMarketPrice", "regularMarketVolume", "regularMarketChange", "regularMarketChangePercent"
                ],
                "Analyst & Target": [
                    "targetMeanPrice", "numberOfAnalystOpinions", "recommendationKey", "recommendationMean"
                ]
            }

            categorized_html = ""
            for category_name, keys in info_categories.items():
                category_key_value_html = ""
                for key in keys:
                    if key in info and info[key] is not None and info[key] != []:
                        value = info[key]
                        if key in ["exDividendDate", "lastSplitDate", "governanceEpochDate", "compensationAsOfEpochDate"]:
                            value = format_timestamp_to_date(value)
                        elif key in ["marketCap", "enterpriseValue", "fullTimeEmployees", "volume", "averageVolume", 
                                     "averageVolume10days", "sharesOutstanding", "impliedSharesOutstanding", "regularMarketVolume"]:
                            value = format_large_number(value)
                        elif isinstance(value, (int, float)):
                            if 'percent' in key.lower() or 'ratio' in key.lower() or 'yield' in key.lower() or 'beta' in key.lower() or 'payoutRatio' in key.lower():
                                value = f"{value:.2%}"
                            elif 'price' in key.lower() or 'dividend' in key.lower() or 'average' in key.lower():
                                value = f"{value:.2f}"
                            else:
                                value = f"{value:,.0f}"
                        category_key_value_html += f"<div class='key-value-pair'><h3>{key.replace('_',' ').title()}</h3><p>{value}</p></div>"
                if category_key_value_html:
                    categorized_html += f"<h2>{category_name}</h2><div class='card'><div class='card-content-grid'>{category_key_value_html}</div></div>"

            extra_sections = ""
            if long_summary:
                extra_sections += f"<div class='big-box'><h2>Business Summary</h2><p>{long_summary}</p></div>"
            if officers:
                officer_rows = "".join(
                    f"<tr><td>{o.get('name','')}</td><td>{o.get('title','')}</td><td>{o.get('age','')}</td></tr>"
                    for o in officers
                )
                officer_table = f"<table class='styled-table'><tr><th>Name</th><th>Title</th><th>Age</th></tr>{officer_rows}</table>"
                extra_sections += f"<div class='big-box'><h2>Company Officers</h2>{officer_table}</div>"

            content_html = f"{categorized_html}{extra_sections}"

    except Exception as e:
        content_html = f"<h1>Error</h1><p>{str(e)}</p>"

    return wrap_html(f"Company Info for {symbol}", content_html)
