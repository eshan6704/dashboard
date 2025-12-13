from common import *
import gradio as gr
from stock import *
from indices_html import *
from index_live_html import *
from preopen_html import *
from eq_html import *
import pandas as pd
from bhavcopy_html import *
from nsepython import *
from yahooinfo import fetch_info
import datetime


# ======================================================
# Request Type Options
# ======================================================
STOCK_REQ = [
    "info", "intraday", "daily", "nse_eq", "qresult", "result",
    "balance", "cashflow", "dividend", "split", "other", "stock_hist"
]

INDEX_REQ = [
    "indices", "nse_open", "nse_preopen", "nse_fno", "nse_fiidii",
    "nse_events", "nse_future", "nse_bhav", "nse_highlow",
    "index_history", "nse_largedeals", "nse_most_active",
    "largedeals_historical", "nse_bulkdeals", "nse_blockdeals",
    "index_pe_pb_div", "index_total_returns"
]

# ======================================================
# Update UI based on mode
# ======================================================
def update_on_mode(mode):
    if mode == "stock":
        return (
            gr.update(choices=STOCK_REQ, value="info"),
            gr.update(value="ITC"),
            gr.update(value=yesterday_str())
        )

    elif mode == "index":
        return (
            gr.update(choices=INDEX_REQ, value="indices"),
            gr.update(value="NIFTY 50"),
            gr.update(value=yesterday_str())
        )

    return (
        gr.update(choices=[], value=""),
        gr.update(value=""),
        gr.update(value="")
    )

# ======================================================
# Data Fetcher (API logic untouched)
# ======================================================
def fetch_data(mode, req_type, name, date_str):
    req_type = req_type.lower()
    name = name.strip()
    date_str = date_str.strip()

    # ✅ Frontend may send empty date → auto yesterday
    if not date_str:
        date_str = yesterday_str()

    date_start = last_year_date(date_str)

    if mode == "index":

        if req_type == "indices":
            return build_indices_html()

        elif req_type == "nse_open":
            return build_index_live_html()

        elif req_type == "nse_preopen":
            return build_preopen_html()

        elif req_type == "nse_fno":
            return wrap(nse_fno(name))

        elif req_type == "nse_events":
            return nse_events().to_html()

        elif req_type == "nse_fiidii":
            return nse_fiidii().to_html()

        elif req_type == "nse_future":
            return wrap(nse_future(name))

        elif req_type == "nse_highlow":
            return wrap(nse_highlow())

        elif req_type == "nse_bhav":
            return build_bhavcopy_html(date_str)

        elif req_type == "nse_largedeals":
            return nse_largedeals().to_html()

        elif req_type == "nse_bulkdeals":
            return nse_bulkdeals().to_html()

        elif req_type == "nse_blockdeals":
            return nse_blockdeals().to_html()

        elif req_type == "nse_most_active":
            return nse_most_active().to_html()

        elif req_type == "index_history":
            return index_history("NIFTY 50", date_start, date_str).to_html()

        elif req_type == "largedeals_historical":
            return nse_largedeals_historical(date_start, date_str).to_html()

        elif req_type == "index_pe_pb_div":
            return index_pe_pb_div("NIFTY 50", date_start, date_str).to_html()

        elif req_type == "index_total_returns":
            return index_total_returns("NIFTY 50", date_start, date_str).to_html()

        else:
            return wrap(f"<h3>No handler for {req_type}</h3>")

    elif mode == "stock":

        if req_type == "daily":
            return wrap(fetch_daily(name))

        elif req_type == "nse_eq":
            return build_eq_html(name)

        elif req_type == "intraday":
            return wrap(fetch_intraday(name))

        elif req_type == "info":
            return wrap(fetch_info(name))

        elif req_type == "qresult":
            return wrap(fetch_qresult(name))

        elif req_type == "result":
            return wrap(fetch_result(name))

        elif req_type == "balance":
            return wrap(fetch_balance(name))

        elif req_type == "cashflow":
            return wrap(fetch_cashflow(name))

        elif req_type == "dividend":
            return wrap(fetch_dividend(name))

        elif req_type == "split":
            return wrap(fetch_split(name))

        elif req_type == "other":
            return wrap(fetch_other(name))

        elif req_type == "stock_hist":
            return nse_stock_hist(date_start, date_str, name).to_html()

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

        name_input = gr.Textbox(
            label="Symbol / Index Name",
            scale=2
        )

        req_type_input = gr.Dropdown(
            label="Request Type",
            allow_custom_value=True,
            scale=2
        )

        date_input = gr.Textbox(
            label="Date (DD-MM-YYYY)",
            placeholder="Leave empty = yesterday",
            scale=1
        )

        fetch_btn = gr.Button("Fetch", scale=1)

    output = gr.HTML(label="Output")

    # Mode change → auto defaults
    mode_input.change(
        update_on_mode,
        inputs=mode_input,
        outputs=[req_type_input, name_input, date_input]
    )

    # Initial load defaults
    iface.load(
        update_on_mode,
        inputs=mode_input,
        outputs=[req_type_input, name_input, date_input]
    )

    # Fetch
    fetch_btn.click(
        fetch_data,
        inputs=[mode_input, req_type_input, name_input, date_input],
        outputs=output
    )

# ======================================================
# Launch
# ======================================================
if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=7860)