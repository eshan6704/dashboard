import gradio as gr
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd

def fetch_data(symbol, req_type):
    try:
        ticker = yf.Ticker(symbol)

        if req_type.lower() == "info":
            info = ticker.info
            rows = "".join(
                f"<tr><td><b>{key}</b></td><td>{value}</td></tr>"
                for key, value in info.items()
            )
            html_response = f"""
            <h1>Ticker Info for {symbol}</h1>
            <table border="1" cellpadding="5" cellspacing="0">
              {rows}
            </table>
            """
            return html_response, None

        elif req_type.lower() == "daily":
            df = yf.download(symbol, period="1y", interval="1d").round(2)
            if df.empty:
                return f"<h1>No daily data for {symbol}</h1>", None

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
                title=f"Daily Candlestick Chart for {symbol}",
                xaxis_title="Date",
                yaxis_title="Price",
                yaxis2=dict(title="Volume", overlaying="y", side="right", showgrid=False),
                xaxis_rangeslider_visible=False,
                height=600
            )

            table_html = df.tail(30).to_html(classes="dataframe", border=1)
            chart_html = fig.to_html(full_html=False)

            html_response = f"""
            <h1>Daily Data for {symbol}</h1>
            {chart_html}
            <h2>Recent Daily Data (last 30 rows)</h2>
            {table_html}
            """

            return html_response, fig

        elif req_type.lower() == "intraday":
            df = yf.download(symbol, period="1d", interval="5m").round(2)
            if df.empty:
                return f"<h1>No intraday data for {symbol}</h1>", None

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
                title=f"Intraday Candlestick Chart for {symbol}",
                xaxis_title="Time",
                yaxis_title="Price",
                yaxis2=dict(title="Volume", overlaying="y", side="right", showgrid=False),
                xaxis_rangeslider_visible=False,
                height=600
            )

            table_html = df.tail(50).to_html(classes="dataframe", border=1)
            chart_html = fig.to_html(full_html=False)

            html_response = f"""
            <h1>Intraday Data for {symbol}</h1>
            {chart_html}
            <h2>Recent Intraday Data (last 50 rows)</h2>
            {table_html}
            """

            return html_response, fig

        else:
            return f"<h1>No handler for {req_type}</h1>", None

    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p>", None


iface = gr.Interface(
    fn=fetch_data,
    inputs=[gr.Textbox(label="Stock Symbol", value="PNB"),
            gr.Textbox(label="Request Type", value="info")],
    outputs=[gr.HTML(label="Full HTML Output"), gr.Plot(label="Chart")],
    title="Stock Data API (Full)",
    description="Fetch data from NSE and yfinance",
    api_name="fetch_data"
)

if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=7860)
