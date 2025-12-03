import gradio as gr

from nse import *
from stock import *


# ======================================================
# Scrollable HTML wrapper for all table-based output
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
    """Wrap returned HTML inside scrollable container"""
    if html is None:
        return "<h3>No Data</h3>"
    return SCROLL_WRAP.replace("{{HTML}}", html)


# ======================================================
# Data Fetcher
# ======================================================
def fetch_data(mode, req_type, name):
    req_type = req_type.lower()
    symbol = name

    if mode == "index":

        if req_type == "nse_indices":
            return wrap(nse_indices())

        elif req_type == "nse_open":
            return wrap(nse_open(name))

        elif req_type == "nse_preopen":
            return wrap(nse_preopen(name))

        elif req_type == "nse_fno":
            return wrap(nse_fno(name))

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

        mode_input = gr.Textbox(
            label="Mode",
            value="stock",
            placeholder="stock / index",
            scale=1
        )

        symbol = gr.Textbox(
            label="Symbol / Index Name",
            value="PNB",
            placeholder="Enter symbol",
            scale=2
        )

        req_type = gr.Dropdown(
            label="Request Type",
            choices=[
                "info","intraday","daily","qresult","result","balance","cashflow",
                "dividend","split","nse_indices","nse_open","nse_preopen","nse_fno","nse_future","nse_bhav","nse_highlow"
            ],
            value="info",
            scale=2
        )

        btn = gr.Button("Fetch", scale=1)

    # Output box (scroll handled by wrapper)
    output = gr.HTML(label="Output")

    btn.click(fetch_data, inputs=[mode_input, req_type, symbol], outputs=output)


# ======================================================
# Launch
# ======================================================
if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=7860)
