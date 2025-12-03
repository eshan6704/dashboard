import gradio as gr

from nse import *
from stock import *




# -----------------------------
# Data fetch function
# -----------------------------
def fetch_data(mode, req_type, name):
    req_type = req_type.lower()
    symbol = name
    if mode=="index":
        if req_type=="indices":
            return indices()
        elif req_type=="open":
            return open(name)
        elif req_type=="preopen":
            return preopen(name)
        elif req_type=="fno":
            return fno(name)
    
    elif mode=="stock":
        
        if req_type == "daily":
            return fetch_daily(symbol)
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


# -----------------------------
# UI
# -----------------------------
with gr.Blocks(title="Stock / Index App") as iface:

    gr.Markdown("### **Stock / Index Data Fetcher**")

    # ----- Top bar -----
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
                "dividend","split","index","open","preopen","fno","future","bhav","highlow"
            ],
            value="info",
            scale=2
        )

        btn = gr.Button("Fetch", scale=1)

    # ----- Output -----
    output = gr.HTML(label="Output")

    btn.click(fetch_data, inputs=[mode_input, req_type, symbol], outputs=output)


# -----------------------------
# Launch
# -----------------------------
if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=7860)
