# app.py
import gradio as gr
from daily import fetch_daily
from intraday import fetch_intraday
from info import fetch_info
from qresult import fetch_qresult
from result import fetch_result
from balance import fetch_balance
from cashflow import fetch_cashflow
from dividend import fetch_dividend
from split import fetch_split
from other import fetch_other

# --- Main UI function ---
def fetch_data(symbol, req_type):
    req_type = req_type.lower()
    if req_type == "daily":
        return fetch_daily(symbol,"NSE")
    elif req_type == "intraday":
        return fetch_intraday(symbol)
    elif req_type == "info":
        return fetch_info(symbol)
    elif req_type == "qresult":
        return fetch_qresult(symbol)
    elif req_type == "result":
        return fetch_result(symbol)
    elif req_type == "balance":
        return fetch_balance(symbol)
    elif req_type == "cashflow":
        return fetch_cashflow(symbol)
    elif req_type == "dividend":
        return fetch_dividend(symbol)
    elif req_type == "split":
        return fetch_split(symbol)
    elif req_type == "other":
        return fetch_other(symbol)
    else:
        return f"<h1>No handler for {req_type}</h1>"

# --- Gradio Interface ---
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
    description="Fetch NSE stock data with charts and indicators",
    api_name="fetch_data"
)

if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=7860)
