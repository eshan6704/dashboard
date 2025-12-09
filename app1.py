import gradio as gr

from stock import *
from nsepython import *
import pandas as pd

# ======================================================
# Scrollable HTML wrapper
# ======================================================
SCROLL_WRAP = """
<div style="
    max-height: 80vh;
    overflow-y: auto;
    overflow-x: auto;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 6px;
">
{{HTML}}
</div>
"""

def wrap(html):
    if html is None:
        return "<h3>No Data</h3>"
    return SCROLL_WRAP.replace("{{HTML}}", html)


# ======================================================
# Request Type Options
# ======================================================
STOCK_REQ = [
    "info", "intraday", "daily", "qresult", "result", "balance",
    "cashflow", "dividend", "split", "other"
]

INDEX_REQ = [
    "indices", "nse_open", "nse_preopen", "nse_fno",
    "nse_future", "nse_bhav", "nse_highlow"
]


# ======================================================
# Update Dropdown + Symbol
# ======================================================
def update_on_mode(mode):
    if mode == "stock":
        return (
            gr.update(choices=STOCK_REQ, value="info"),
            gr.update(value="ITC", placeholder="Enter stock symbol")
        )
    elif mode == "index":
        return (
            gr.update(choices=INDEX_REQ, value="indices"),
            gr.update(value="NIFTY 50", placeholder="Enter index name or leave blank for today bhavcopy")
        )
    return gr.update(visible=False), gr.update(value="")


# ======================================================
# Data Fetcher
# ======================================================
def fetch_data(mode, req_type, symbol, date_str):
    req_type = req_type.lower()
    symbol = symbol.strip()
    date_str = date_str.strip()

    if mode == "index":
        if req_type == "indices":
            return build_indices_html()
        elif req_type == "nse_open":
            return wrap(nse_open(symbol))
        elif req_type == "nse_preopen":
            return wrap(nse_preopen(symbol))
        elif req_type == "nse_fno":
            return wrap(nse_fno(symbol))
        elif req_type == "nse_future":
            return wrap(nse_future(symbol))
        elif req_type == "nse_bhav":
            # Use date if provided, else today
            date_input = date_str or pd.Timestamp.today().strftime("%d-%m-%Y")
            return wrap(nse_bhav(date_input))
        elif req_type == "nse_highlow":
            return wrap(nse_highlow())
        else:
            return wrap(f"<h3>No handler for {req_type}</h3>")

    elif mode == "stock":
        if req_type == "daily":
            return wrap(fetch_daily(symbol))
        elif req_type == "intraday":
            return wrap(fetch_intraday(symbol))
        elif req_type == "info":
            return wrap(fetch_info(symbol))
        elif req_type == "qresult":
            return wrap(fetch_qresult(symbol))
        elif req_type == "result":
            return wrap(fetch_result(symbol))
        elif req_type == "balance":
            return wrap(fetch_balance(symbol))
        elif req_type == "cashflow":
            return wrap(fetch_cashflow(symbol))
        elif req_type == "dividend":
            return wrap(fetch_dividend(symbol))
        elif req_type == "split":
            return wrap(fetch_split(symbol))
        elif req_type == "other":
            return wrap(fetch_other(symbol))
        else:
            return wrap(f"<h3>No handler for {req_type}</h3>")

    return wrap(f"<h3>No valid mode: {mode}</h3>")


# ======================================================
# UI
# ======================================================
with gr.Blocks(title="Stock / Index App") as iface:

    gr.Markdown("### **Stock / Index Data Fetcher**")

    with gr.Row():

        mode_input = gr.Radio(
            ["stock", "index"],
            label="Mode",
            value="stock",
            scale=1
        )

        symbol = gr.Textbox(
            label="Symbol / Index Name",
            value="ITC",
            placeholder="Enter stock symbol",
            scale=2
        )

        req_type = gr.Dropdown(
            label="Request Type",
            choices=STOCK_REQ,
            value="info",
            scale=2
        )

        date_field = gr.Textbox(
            label="Date",
            value="",
            placeholder="DD-MM-YYYY",
            scale=1
        )

        btn = gr.Button("Fetch", scale=1)

    output = gr.HTML(label="Output")

    # Mode change updates dropdown + symbol
    mode_input.change(
        update_on_mode,
        inputs=mode_input,
        outputs=[req_type, symbol]
    )

    # Request type change does not hide date anymore (always visible)
    # Fetch button
    btn.click(fetch_data, inputs=[mode_input, req_type, symbol, date_field], outputs=output)


# ======================================================
# Launch
# ======================================================
if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=7860)
