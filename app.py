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
            html_response = f"""
            <style>
            table.info-table {{
              border-collapse: collapse;
              width: 100%;
              font-family: sans-serif;
              font-size: 0.9em;
              box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }}
            table.info-table th, table.info-table td {{
              border: 1px solid #ddd;
              padding: 8px;
            }}
            table.info-table tr:nth-child(even) {{ background-color: #f9f9f9; }}
            table.info-table tr:hover {{ background-color: #f1f1f1; }}
            </style>
            <h2>Ticker Info for {symbol}</h2>
            <table class="info-table">
              {rows}
            </table>
            """
            return html_response

        # Daily data
        elif req_type.lower() == "daily":
            df = yf.download(symbol, period="1y", interval="1d").round(2)
            if df.empty:
                return f"<h1>No daily data for {symbol}</h1>"

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

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
                y=df["Volume"],
                name="Volume",
                marker_color="lightblue",
                yaxis="y2"
            ))
            fig.update_layout(
                #title=f"Daily Candlestick Chart for {symbol}",
                xaxis_title="Date",
                yaxis_title="Price",
                yaxis2=dict(title="Volume", overlaying="y", side="right", showgrid=False),
                xaxis_rangeslider_visible=False,
                height=600
            )

            chart_html = fig.to_html(full_html=False)

            # Styled table
            table_style = """
            <style>
            .styled-table {
              border-collapse: collapse;
              margin: 20px 0;
              font-size: 0.9em;
              font-family: sans-serif;
              width: 100%;
              box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            .styled-table thead tr {
              background-color: #009879;
              color: #ffffff;
              text-align: left;
            }
            .styled-table th, .styled-table td {
              padding: 12px 15px;
              border: 1px solid #ddd;
            }
            .styled-table tbody tr:nth-child(even) {
              background-color: #f3f3f3;
            }
            </style>
            """
            table_html = df.tail(30).to_html(classes="styled-table", border=0)

            return f"""
            {chart_html}
            <h2>Recent Daily Data (last 30 rows)</h2>
            {table_style}
            {table_html}
            """

        # Intraday data
        elif req_type.lower() == "intraday":
            df = yf.download(symbol, period="1d", interval="5m").round(2)
            if df.empty:
                return f"<h1>No intraday data for {symbol}</h1>"

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

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
                y=df["Volume"],
                name="Volume",
                marker_color="orange",
                yaxis="y2"
            ))
            fig.update_layout(
                #title=f"Intraday Candlestick Chart for {symbol}",
                xaxis_title="Time",
                yaxis_title="Price",
                yaxis2=dict(title="Volume", overlaying="y", side="right", showgrid=False),
                xaxis_rangeslider_visible=False,
                height=600
            )

            chart_html = fig.to_html(full_html=False)

            # Styled table
            table_style = """
            <style>
            .styled-table {
              border-collapse: collapse;
              margin: 20px 0;
              font-size: 0.9em;
              font-family: sans-serif;
              width: 100%;
              box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            .styled-table thead tr {
              background-color: #ff9800;
              color: #ffffff;
              text-align: left;
            }
            .styled-table th, .styled-table td {
              padding: 12px 15px;
              border: 1px solid #ddd;
            }
            .styled-table tbody tr:nth-child(even) {
              background-color: #f9f9f9;
            }
            </style>
            """
            table_html = df.tail(50).to_html(classes="styled-table", border=0)

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
