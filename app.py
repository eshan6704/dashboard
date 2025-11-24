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
  display:inline-block;
  width:250px;
  margin:10px;
  padding:15px;
  border:1px solid #ddd;
  border-radius:8px;
  box-shadow:0 2px 5px rgba(0,0,0,0.1);
  vertical-align:top;
  background:#fafafa;
}
.card h3 { margin:0 0 10px; font-size:1em; color:#333; }
.card p { margin:0; font-size:0.9em; color:#555; word-wrap:break-word; }
</style>
"""

def fetch_data(symbol, req_type):
    try:
        ticker = yf.Ticker(symbol)

        # Info block as cards
        if req_type.lower() == "info":
            info = ticker.info
            if not info:
                return "<h1>No info available</h1>"
            cards = "".join(
                f"<div class='card'><h3>{key}</h3><p>{value}</p></div>"
                for key, value in info.items()
            )
            return f"{STYLE_BLOCK}{cards}"

        # Daily chart
        elif req_type.lower() == "daily":
            df = yf.download(symbol, period="1y", interval="1d").round(2)
            if df.empty:
                return f"<h1>No daily data for {symbol}</h1>"
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
            return f"{chart_html}<h2>Recent Daily Data (last 30 rows)</h2>{STYLE_BLOCK}{table_html}"

        # Intraday chart
        elif req_type.lower() == "intraday":
            df = yf.download(symbol, period="1d", interval="5m").round(2)
            if df.empty:
                return f"<h1>No intraday data for {symbol}</h1>"
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
            return f"{chart_html}<h2>Recent Intraday Data (last 50 rows)</h2>{STYLE_BLOCK}{table_html}"

        # Financial sections
        elif req_type.lower() == "qresult":
            df = ticker.quarterly_financials
            return f"<h2>Quarterly Results</h2>{STYLE_BLOCK}{df.to_html(classes='styled-table', border=0)}" if not df.empty else "<h1>No quarterly results available</h1>"

        elif req_type.lower() == "result":
            df = ticker.financials
            return f"<h2>Annual Results</h2>{STYLE_BLOCK}{df.to_html(classes='styled-table', border=0)}" if not df.empty else "<h1>No annual results available</h1>"

        elif req_type.lower() == "balance":
            df = ticker.balance_sheet
            return f"<h2>Balance Sheet</h2>{STYLE_BLOCK}{df.to_html(classes='styled-table', border=0)}" if not df.empty else "<h1>No balance sheet available</h1>"

        elif req_type.lower() == "cashflow":
            df = ticker.cashflow
            return f"<h2>Cash Flow</h2>{STYLE_BLOCK}{df.to_html(classes='styled-table', border=0)}" if not df.empty else "<h1>No cashflow available</h1>"

        elif req_type.lower() == "dividend":
            s = ticker.dividends
            return f"<h2>Dividend History</h2>{STYLE_BLOCK}{s.to_frame('Dividend').to_html(classes='styled-table', border=0)}" if not s.empty else "<h1>No dividend history available</h1>"

        elif req_type.lower() == "split":
            s = ticker.splits
            return f"<h2>Split History</h2>{STYLE_BLOCK}{s.to_frame('Split').to_html(classes='styled-table', border=0)}" if not s.empty else "<h1>No split history available</h1>"

        elif req_type.lower() == "other":
            df = ticker.earnings
            return f"<h2>Earnings</h2>{STYLE_BLOCK}{df.to_html(classes='styled-table', border=0)}" if not df.empty else "<h1>No earnings data available</h1>"

        else:
            return f"<h1>No handler for {req_type}</h1>"

    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p>"

iface = gr.Interface(
    fn=fetch_data,
    inputs=[
        gr.Textbox(label="Stock Symbol", value="PNB.NS"),
        gr.Dropdown(
            label="Request Type",
            choices=["info","intraday","daily","qresult","result","balance","cashflow","dividend","split","other"],
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
