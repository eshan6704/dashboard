import gradio as gr
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd

STYLE_BLOCK = """
<style>
.styled-table {
  border-collapse: collapse;
  margin: 10px 0;
  font-size: 0.9em;
  font-family: sans-serif;
  width: 100%;
  box-shadow: 0 0 10px rgba(0,0,0,0.1);
}
.styled-table th, .styled-table td {
  padding: 8px 10px;
  border: 1px solid #ddd;
}
.styled-table tbody tr:nth-child(even) {
  background-color: #f9f9f9;
}
.card {
  display: block; /* Ensures each card is on its own line */
  width: 95%;     /* Make card take up most of the width */
  margin: 10px auto; /* Center the cards and add margin */
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  background: #fafafa;
}
.card-category-title {
  font-size: 1.1em; /* Slightly larger heading for category */
  color: #222;
  margin: 0 0 8px; /* Adjusted margin */
  border-bottom: 1px solid #eee; /* Add a separator */
  padding-bottom: 5px;
}
.card-content-grid {
  display: flex;
  flex-wrap: wrap; /* Allow items to wrap to the next line */
  gap: 15px; /* Space between individual key-value items */
}
.key-value-pair {
  flex: 1 1 calc(33% - 15px); /* For 3 items in a row, considering gap */
  box-sizing: border-box; /* Include padding and border in the width */
  min-width: 250px; /* Prevent items from becoming too narrow */
  background: #fff;
  padding: 10px;
  border: 1px solid #e0e0e0;
  border-radius: 5px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.key-value-pair h3 {
  font-size: 0.95em; /* Smaller heading for the key */
  color: #444;
  margin: 0 0 5px 0;
  border-bottom: none;
  padding-bottom: 0;
}
.key-value-pair p {
  font-size: 0.9em; /* Smaller paragraph for the value */
  color: #555;
  margin: 0;
  font-weight: bold; /* Make values stand out */
}
.big-box {
  width:95%;
  margin:20px auto;
  padding:20px;
  border:1px solid #ccc;
  border-radius:8px;
  background:#fff;
  box-shadow:0 2px 8px rgba(0,0,0,0.1);
  font-size:0.95em;
  line-height:1.4em;
  max-height:400px;
  overflow-y:auto;
}
</style>
"""

def fetch_data(symbol, req_type):
    yfsymbol=symbol+".NS"
    try:
        ticker = yf.Ticker(yfsymbol)

        content_html = ""

        # Info block as cards + big boxes
        if req_type.lower() == "info":
            info = ticker.info
            if not info:
                content_html = "<h1>No info available</h1>"
            else:
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

                long_summary = info.pop("longBusinessSummary", None)
                officers = info.pop("companyOfficers", None)

                categorized_html = ""
                for category_name, keys in info_categories.items():
                    category_key_value_html = "" # Collect key-value pairs for this category
                    for key in keys:
                        if key in info and info[key] is not None and info[key] != []:
                            value = info[key]
                            # Format values as appropriate
                            if isinstance(value, (int, float)) and key not in ['longName', 'symbol', 'exchange', 'quoteType', 'sector', 'industry', 'website', 'address1', 'city', 'state', 'zip', 'country', 'phone', 'longBusinessSummary', 'recommendationKey']:
                                if 'marketCap' in key.lower() or 'value' in key.lower() or 'volume' in key.lower():
                                    value = f"{value:,.0f}" # Format large numbers
                                elif 'percent' in key.lower() or 'ratio' in key.lower() or 'yield' in key.lower() or 'beta' in key.lower() or 'payoutRatio' in key.lower():
                                    value = f"{value:.2%}" # Format percentages
                                elif 'price' in key.lower() or 'dividend' in key.lower() or 'average' in key.lower():
                                    value = f"{value:.2f}" # Format currency/prices

                            category_key_value_html += f"<div class='key-value-pair'><h3>{key.replace('_', ' ').title()}</h3><p>{value}</p></div>"

                    if category_key_value_html: # Only add category header and card if there is content in it
                        categorized_html += f"<h2>{category_name}</h2><div class='card'><div class='card-content-grid'>{category_key_value_html}</div></div>"

                extra_sections = ""
                if long_summary:
                    extra_sections += f"<div class='big-box'><h2>Business Summary</h2><p>{long_summary}</p></div>"
                if officers:
                    officer_rows = "".join(
                        f"<tr><td>{o.get('name','')}"f"</td><td>{o.get('title','')}"f"</td><td>{o.get('age','')}"f"</td></tr>"
                        for o in officers
                    )
                    officer_table = f"<table class='styled-table'><tr><th>Name</th><th>Title</th><th>Age</th></tr>{officer_rows}</table>"
                    extra_sections += f"<div class='big-box'><h2>Company Officers</h2>{officer_table}</div>"
                content_html = f"{categorized_html}{extra_sections}"

        # Daily chart
        elif req_type.lower() == "daily":
            df = yf.download(yfsymbol, period="1y", interval="1d").round(2)
            if df.empty:
                content_html = f"<h1>No daily data for {symbol}</h1>"
            else:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)

                low_price = df["Low"].min()
                high_price = df["High"].max()
                price_range = high_price - low_price
                vol_band_min = low_price - (price_range / 5)
                vol_band_max = low_price
                vol_max = df["Volume"].max()
                vol_scale = (vol_band_max - vol_band_min) / vol_max if vol_max > 0 else 1

                fig = go.Figure()
                fig.add_trace(go.Candlestick(
                    x=df.index, open=df["Open"], high=df["High"],
                    low=df["Low"], close=df["Close"], name="Price"
                ))
                fig.add_trace(go.Bar(
                    x=df.index,
                    y=df["Volume"] * vol_scale + vol_band_min,
                    name="Volume", marker_color="lightblue",
                    customdata=df["Volume"],
                    hovertemplate="Volume: %{customdata}<extra></extra>"
                ))
                fig.update_layout(
                    xaxis_title="Date", yaxis_title="Price",
                    yaxis=dict(range=[vol_band_min, high_price]),
                    xaxis_rangeslider_visible=False, height=600
                )
                chart_html = fig.to_html(full_html=False)
                table_html = df.tail(30).to_html(classes="styled-table", border=0)
                content_html = f"{chart_html}<h2>Recent Daily Data (last 30 rows)</h2>{table_html}"

        # Intraday chart
        elif req_type.lower() == "intraday":
            df = yf.download(yfsymbol, period="1d", interval="5m").round(2)
            if df.empty:
                content_html = f"<h1>No intraday data for {symbol}</h1>"
            else:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)

                low_price = df["Low"].min()
                high_price = df["High"].max()
                price_range = high_price - low_price
                vol_band_min = low_price - (price_range / 5)
                vol_band_max = low_price
                vol_max = df["Volume"].max()
                vol_scale = (vol_band_max - vol_band_min) / vol_max if vol_max > 0 else 1

                fig = go.Figure()
                fig.add_trace(go.Candlestick(
                    x=df.index, open=df["Open"], high=df["High"],
                    low=df["Low"], close=df["Close"], name="Price"
                ))
                fig.add_trace(go.Bar(
                    x=df.index,
                    y=df["Volume"] * vol_scale + vol_band_min,
                    name="Volume", marker_color="orange",
                    customdata=df["Volume"],
                    hovertemplate="Volume: %{customdata}<extra></extra>"
                ))
                fig.update_layout(
                    xaxis_title="Time", yaxis_title="Price",
                    yaxis=dict(range=[vol_band_min, high_price]),
                    xaxis_rangeslider_visible=False, height=600
                )
                chart_html = fig.to_html(full_html=False)
                table_html = df.tail(50).to_html(classes="styled-table", border=0)
                content_html = f"{chart_html}<h2>Recent Intraday Data (last 50 rows)</h2>{table_html}"

        # Financial sections
        elif req_type.lower() == "qresult":
            df = ticker.quarterly_financials
            content_html = f"<h2>Quarterly Results</h2>{df.to_html(classes='styled-table', border=0)}" if not df.empty else "<h1>No quarterly results available</h1>"

        elif req_type.lower() == "result":
            df = ticker.financials
            content_html = f"<h2>Annual Results</h2>{df.to_html(classes='styled-table', border=0)}" if not df.empty else "<h1>No annual results available</h1>"

        elif req_type.lower() == "balance":
            df = ticker.balance_sheet
            content_html = f"<h2>Balance Sheet</h2>{df.to_html(classes='styled-table', border=0)}" if not df.empty else "<h1>No balance sheet available</h1>"

        elif req_type.lower() == "cashflow":
            df = ticker.cashflow
            content_html = f"<h2>Cash Flow</h2>{df.to_html(classes='styled-table', border=0)}" if not df.empty else "<h1>No cashflow available</h1>"

        elif req_type.lower() == "dividend":
            s = ticker.dividends
            content_html = f"<h2>Dividend History</h2>{s.to_frame('Dividend').to_html(classes='styled-table', border=0)}" if not s.empty else "<h1>No dividend history available</h1>"

        elif req_type.lower() == "split":
            s = ticker.splits
            content_html = f"<h2>Split History</h2>{s.to_frame('Split').to_html(classes='styled-table', border=0)}" if not s.empty else "<h1>No split history available</h1>"

        elif req_type.lower() == "other":
            df = ticker.earnings
            content_html = f"<h2>Earnings</h2>{df.to_html(classes='styled-table', border=0)}" if not df.empty else "<h1>No earnings data available</h1>"

        else:
            content_html = f"<h1>No handler for {req_type}</h1>"

    except Exception as e:
        content_html = f"<h1>Error</h1><p>{str(e)}</p>"

    # Wrap the content_html in a complete HTML document structure
    full_html_output = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Stock Data for {symbol}</title>
    {STYLE_BLOCK}
</head>
<body>
    {content_html}
</body>
</html>
"""
    return full_html_output


iface = gr.Interface(
    fn=fetch_data,
    inputs=[
        gr.Textbox(label="Stock Symbol", value="PNB"),
        gr.Dropdown(
            label="Request Type",
            choices=[
                "info",
                "intraday",
                "daily",
                "qresult",
                "result",
                "balance",
                "cashflow",
                "dividend",
                "split",
                "other"
            ],
            value="info"
        )
    ],
    outputs=gr.HTML(label="Full HTML Output"),
    title="Stock Data API (Full)",
    description="Fetch data from NSE and yfinance",
    api_name="fetch_data"
)

if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=7860)