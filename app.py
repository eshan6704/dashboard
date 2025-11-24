import gradio as gr
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd

def fetch_data(symbol, req_type):
    try:
        ticker = yf.Ticker(symbol)

        # Info block
        if req_type.lower() == "info":
            info = ticker.info
            rows = "".join(
                f"<tr><td><b>{key}</b></td><td>{value}</td></tr>"
                for key, value in info.items()
            )
            table_style = """
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
            </style>
            """
            html_response = f"""
            {table_style}
            <table class="styled-table">
              {rows}
            </table>
            """
            return html_response

        # Daily block
        elif req_type.lower() == "daily":
            df = yf.download(symbol, period="1y", interval="1d").round(2)
            if df.empty:
                return f"<h1>No daily data for {symbol}</h1>"

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            close_min = df["Close"].min()
            close_max = df["Close"].max()
            price_range = close_max - close_min

            # Reserve band for volume
            vol_band_min = close_min - (price_range / 5)
            vol_band_max = close_min
            vol_max = df["Volume"].max()
            vol_scale = (vol_band_max - vol_band_min) / vol_max if vol_max > 0 else 1

            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                name="Price"
            ))
            fig.add_trace(go.Bar(
                x=df.index,
                y=df["Volume"] * vol_scale + vol_band_min,
                name="Volume",
                marker_color="lightblue"
            ))
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Price",
                yaxis=dict(range=[vol_band_min, close_max]),
                xaxis_rangeslider_visible=False,
                height=600
            )

            chart_html = fig.to_html(full_html=False)
            table_html = df.tail(30).to_html(classes="styled-table", border=0)

            table_style = """
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
            </style>
            """

            return f"""
            {chart_html}
            <h2>Recent Daily Data (last 30 rows)</h2>
            {table_style}
            {table_html}
            """

        # Intraday block
        elif req_type.lower() == "intraday":
            df = yf.download(symbol, period="1d", interval="5m").round(2)
            if df.empty:
                return f"<h1>No intraday data for {symbol}</h1>"

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            close_min = df["Close"].min()
            close_max = df["Close"].max()
            price_range = close_max - close_min

            # Reserve band for volume
            vol_band_min = close_min - (price_range / 5)
            vol_band_max = close_min
            vol_max = df["Volume"].max()
            vol_scale = (vol_band_max - vol_band_min) / vol_max if vol_max > 0 else 1

            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                name="Price"
            ))
            fig.add_trace(go.Bar(
                x=df.index,
                y=df["Volume"] * vol_scale + vol_band_min,
                name="Volume",
                marker_color="orange"
            ))
            fig.update_layout(
                xaxis_title="Time",
                yaxis_title="Price",
                yaxis=dict(range=[vol_band_min, close_max]),
                xaxis_rangeslider_visible=False,
                height=600
            )

            chart_html = fig.to_html(full_html=False)
            table_html = df.tail(50).to_html(classes="styled-table", border=0)

            table_style = """
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
            </style>
            """

            return f"""
            {chart_html}
            <h2>Recent Intraday Data (last 50 rows)</h2>
            {table_style}
            {table_html}
            """

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
