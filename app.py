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
from io import BytesIO
from datetime import datetime
import boto3
import os

# ======================================================
# Backblaze B2 Setup
# ======================================================
S3_ENDPOINT = "https://s3.us-east-005.backblazeb2.com"
BUCKET_NAME = "eshanhf"
AWS_KEY_ID = "005239ca03b31af0000000001"
AWS_SECRET_KEY = "K005uGFZkrtYa4Hg1GliFUQohs/BTk4"

s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=AWS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_KEY,
)

LOG_FILE = "fetch_log.csv"  # CSV log in bucket

def b2_file(file_path=None, bucket_name=BUCKET_NAME, upload=True, download_path=None):
    """
    Universal upload/download function for Backblaze B2.
    """
    try:
        if upload:
            if not file_path or not os.path.isfile(file_path):
                raise ValueError("Valid local file_path must be provided for upload")
            with open(file_path, "rb") as f:
                data = f.read()
            file_name = os.path.basename(file_path)
            s3.put_object(Bucket=bucket_name, Key=file_name, Body=data)
            return True
        else:
            if not file_path:
                raise ValueError("Bucket file name must be provided for download")
            if not download_path:
                raise ValueError("download_path must be provided for download")
            obj = s3.get_object(Bucket=bucket_name, Key=file_path)
            data = obj['Body'].read()
            with open(download_path, "wb") as f:
                f.write(data)
            return True
    except Exception as e:
        print(f"Error in B2 operation: {e}")
        return False

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

# ======================================================
# Date helpers
# ======================================================
def today_str():
    return datetime.date.today().strftime("%d-%m-%Y")

def yesterday_str():
    return (datetime.date.today() - datetime.timedelta(days=1)).strftime("%d-%m-%Y")

def last_year_date(d):
    dt = datetime.datetime.strptime(d, "%d-%m-%Y")
    new_dt = dt.replace(year=dt.year - 1)
    return new_dt.strftime("%d-%m-%Y")

# ======================================================
# HTML wrapper
# ======================================================
def wrap(html):
    if html is None:
        return "<h3>No Data</h3>"
    return SCROLL_WRAP.replace("{{HTML}}", html)

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
# Data Fetcher
# ======================================================
def fetch_data(mode, req_type, name, date_str):
    mode = mode or "stock"
    req_type = req_type.lower() if req_type else "info"
    name = name.strip() if name else "ITC"
    date_str = date_str.strip() if date_str else yesterday_str()
    date_start = last_year_date(date_str)
    client = "gradio"

    # =====================
    # INDEX MODE
    # =====================
    if mode == "index":
        if req_type == "indices":
            result = build_indices_html()
        elif req_type == "nse_open":
            result = build_index_live_html()
        elif req_type == "nse_preopen":
            result = build_preopen_html()
        elif req_type == "nse_fno":
            result = wrap(nse_fno(name))
        elif req_type == "nse_events":
            result = nse_events().to_html()
        elif req_type == "nse_fiidii":
            result = nse_fiidii().to_html()
        elif req_type == "nse_future":
            result = wrap(nse_future(name))
        elif req_type == "nse_highlow":
            result = wrap(nse_highlow())
        elif req_type == "nse_bhav":
            result = build_bhavcopy_html(date_str)
        elif req_type == "nse_largedeals":
            result = nse_largedeals().to_html()
        elif req_type == "nse_bulkdeals":
            result = nse_bulkdeals().to_html()
        elif req_type == "nse_blockdeals":
            result = nse_blockdeals().to_html()
        elif req_type == "nse_most_active":
            result = nse_most_active().to_html()
        elif req_type == "index_history":
            result = index_history("NIFTY 50", date_start, date_str).to_html()
        elif req_type == "largedeals_historical":
            result = nse_largedeals_historical(date_start, date_str).to_html()
        elif req_type == "index_pe_pb_div":
            result = index_pe_pb_div("NIFTY 50", date_start, date_str).to_html()
        elif req_type == "index_total_returns":
            result = index_total_returns("NIFTY 50", date_start, date_str).to_html()
        else:
            result = wrap(f"<h3>No handler for {req_type}</h3>")

    # =====================
    # STOCK MODE
    # =====================
    elif mode == "stock":
        if req_type == "daily":
            result = wrap(fetch_daily(name))
        elif req_type == "nse_eq":
            result = build_eq_html(name)
        elif req_type == "intraday":
            result = wrap(fetch_intraday(name))
        elif req_type == "info":
            result = wrap(fetch_info(name))
        elif req_type == "qresult":
            result = wrap(fetch_qresult(name))
        elif req_type == "result":
            result = wrap(fetch_result(name))
        elif req_type == "balance":
            result = wrap(fetch_balance(name))
        elif req_type == "cashflow":
            result = wrap(fetch_cashflow(name))
        elif req_type == "dividend":
            result = wrap(fetch_dividend(name))
        elif req_type == "split":
            result = wrap(fetch_split(name))
        elif req_type == "other":
            result = wrap(fetch_other(name))
        elif req_type == "stock_hist":
            result = nse_stock_hist(date_start, date_str, name).to_html()
        else:
            result = wrap(f"<h3>No handler for {req_type}</h3>")

    else:
        result = wrap(f"<h3>No valid mode: {mode}</h3>")

    # =====================
    # Log fetch AFTER serving API
    # =====================
    try:
        # Read existing log
        try:
            obj = s3.get_object(Bucket=BUCKET_NAME, Key=LOG_FILE)
            data = obj['Body'].read()
            df = pd.read_csv(BytesIO(data))
        except Exception:
            df = pd.DataFrame(columns=["Sr","Datetime","Client","Mode","Req_Type","Name","Date"])

        # Append new row
        df = df.append({
            "Sr": len(df)+1,
            "Datetime": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "Client": client,
            "Mode": mode,
            "Req_Type": req_type,
            "Name": name,
            "Date": date_str
        }, ignore_index=True)

        # Save back to B2
        csv_buffer = BytesIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        s3.put_object(Bucket=BUCKET_NAME, Key=LOG_FILE, Body=csv_buffer.getvalue())
        print("Fetch logged successfully.")
    except Exception as e:
        print(f"Error logging fetch: {e}")

    return result

# ======================================================
# UI
# ======================================================
with gr.Blocks(title="Stock / Index App") as iface:
    gr.Markdown("### **Stock / Index Data Fetcher**")

    with gr.Row():
        mode_input = gr.Radio(["stock", "index"], label="Mode", value="stock", scale=1)
        name_input = gr.Textbox(label="Symbol / Index Name", placeholder="Enter symbol or index", scale=2)
        req_type_input = gr.Dropdown(label="Request Type", choices=STOCK_REQ, value="info", allow_custom_value=True, scale=2)
        date_input = gr.Textbox(label="Date (DD-MM-YYYY)", placeholder="Leave empty = yesterday", scale=1)
        fetch_btn = gr.Button("Fetch", scale=1)

    output = gr.HTML(label="Output")

    # =====================
    # Only Fetch triggers data
    # =====================
    fetch_btn.click(fetch_data, inputs=[mode_input, req_type_input, name_input, date_input], outputs=output)

# ======================================================
# Launch
# ======================================================
if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=7860)
