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


# -------------------------
# Main Router Function
# -------------------------
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


# -------------------------
# UI
# -------------------------
with gr.Blocks() as iface:

    # HuggingFace-compatible label-removal + compact toolbar CSS
    gr.HTML("""
    <style>
    /* Remove all labels everywhere */
    .gr-block label,
    label,
    .gr-form > div > label,
    .gr-input > label,
    .gr-textbox > label,
    .gr-dropdown > label {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Remove HF Spaces extra label containers */
    .svelte-1ipelgc label,
    .svelte-1ipelgc > label {
        display: none !important;
        height: 0 !important;
    }

    /* Remove top padding */
    .gradio-container {
        padding-top: 0 !important;
    }

    /* Compact row */
    #topbar {
        margin: 0 !important;
        padding: 0 !important;
        height: 34px !important;
        min-height: 34px !important;
        display: flex;
        align-items: center;
    }

    /* Shrink inputs */
    #topbar input, #topbar select {
        height: 28px !important;
        padding: 0 6px !important;
        font-size: 14px !important;
    }

    /* Shrink buttons */
    #topbar button {
        height: 30px !important;
        padding: 0 10px !important;
        font-size: 14px !important;
        margin-left: 5px !important;
    }
    </style>
    """)

    # ------------------
    # Compact top bar
    # ------------------
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
                "index", "info", "intraday", "daily", "qresult",
                "result", "balance", "cashflow",
                "dividend", "split", "other"
            ],
            value="info",
            scale=2
        )

        btn = gr.Button("Submit", scale=1)
        clear_btn = gr.Button("Clear", scale=1)

    # Output area
    output = gr.HTML()

    # Actions
    btn.click(fetch_data, [symbol, req_type], output)
    clear_btn.click(lambda: "", None, output)


# Launch
if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=7860)