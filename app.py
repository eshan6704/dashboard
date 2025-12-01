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
from index import fetch_index


def fetch_data(symbol, req_type):
    req_type = req_type.lower()
    if req_type == "index":
        return fetch_index()
    elif req_type == "daily":
        return fetch_daily(symbol, "NSE")
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
    return f"<h1>No handler for {req_type}</h1>"


with gr.Blocks() as iface:

    # REMOVE labels and shrink input heights
    gr.HTML("""
    <style>
        /* Remove label spaces entirely */
        .gr-form > div > label, 
        .gr-input label, 
        .gr-textbox label, 
        .gr-dropdown label {
            display: none !important;
        }

        /* Shrink components height */
        input, select, button {
            height: 28px !important;
            padding: 0 6px !important;
            font-size: 14px !important;
        }

        /* Tight row */
        #topbar {
            margin: 0;
            padding: 0;
            height: 30px !important;
        }

        #topbar > * {
            margin: 0 !important;
        }

        /* Smaller dropdown arrow */
        .gr-dropdown select {
            height: 28px !important;
        }
    </style>
    """)

    with gr.Row(elem_id="topbar"):

        symbol = gr.Textbox(
            label="",
            placeholder="Symbol",
            value="PNB",
            scale=2
        )

        req_type = gr.Dropdown(
            label="",
            choices=[
                "index","info","intraday","daily","qresult",
                "result","balance","cashflow","dividend","split","other"
            ],
            value="info",
            scale=2
        )

        btn = gr.Button("Submit", scale=1)
        clear_btn = gr.Button("Clear", scale=1)

    output = gr.HTML()

    btn.click(fetch_data, [symbol, req_type], output)
    clear_btn.click(lambda: "", None, output)


if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=7860)