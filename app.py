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

def fetch_data(mode, req_type, name):
    req_type = req_type.lower()
    symbol = name

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
    else:
        return f"<h1>No handler for {req_type}</h1>"

with gr.Blocks() as iface:

    # CSS for horizontal top bar, spacing, full visibility
    gr.HTML(
    # Top inputs in horizontal block (use Blocks, not Block)
    with gr.Blocks(elem_id="topblock"):
        mode_input = gr.Textbox(label="Mode", value="stock", scale=2, placeholder="Mode")
        symbol = gr.Textbox(label="Stock symbol", value="PNB", scale=2, placeholder="Symbol")
        req_type = gr.Dropdown(
            label="req_type",
            choices=[
                "info","intraday","daily","qresult","result","balance","cashflow",
                "dividend","split","index","open","preopen","ce","pe","future","bhav","highlow"
            ],
            value="info",
            scale=3
        )
        btn = gr.Button("Submit", scale=2)

    # Output area
    output = gr.HTML()

    # Click event
    btn.click(fetch_data, inputs=[mode_input, req_type, symbol], outputs=output)

if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=7860)
