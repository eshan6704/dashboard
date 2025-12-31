
# -------------------------------------------------------
# Local modules
# -------------------------------------------------------
from . import common
from . import stock
from . import indices_html as indices
from . import index_live_html as live
from . import preopen_html as pre
from . import eq_html as eq
from . import bhavcopy_html as bhav
from . import build_nse_fno as fno
from . import nsepythonmodified as ns
from . import yahooinfo
from . import screener   # screener owns its map


# -------------------------------------------------------
# REQ TYPE MAP (stock & index only)
# -------------------------------------------------------
REQ_TYPE_MAP = {
    "stock": [
        "info", "intraday", "daily", "nse_eq", "qresult",
        "result", "balance", "cashflow", "dividend",
        "split", "other", "stock_hist"
    ],
    "index": [
        "indices", "open", "preopen", "fno",
        "fiidii", "events",
        "index_highlow", "stock_highlow", "bhav",
        "largedeals", "bulkdeals", "blockdeals",
        "most_active", "index_history",
        "Hlargedeals", "pe_pb",
        "total_returns"
    ],
}

# ===============================
# Screener name → URL mapping
# ===============================
SCREENER_MAP = {
    "from_high": "https://www.screener.in/screens/3355081/from-high/",
    "sales_wise": "https://www.screener.in/screens/880780/sales_wise/",
    "fii_buying": "https://www.screener.in/screens/343087/fii-buying/",
    "debt_reduction": "https://www.screener.in/screens/126864/debt-reduction/",
    "magic_formula": "https://www.screener.in/screens/59/magic-formula/",

}

# -------------------------------------------------------
# STOCK handler
# -------------------------------------------------------
def handle_stock(req: FetchRequest):
    t = req.req_type.lower()

    if t == "info":
        return yahooinfo.fetch_info(req.name)
    if t == "intraday":
        return stock.fetch_intraday(req.name)
    if t == "daily":
        return stock.fetch_daily(req.name, req.date_end)
    if t == "nse_eq":
        return eq.build_eq_html(req.name)
    if t == "qresult":
        return stock.fetch_qresult(req.name)
    if t == "result":
        return stock.fetch_result(req.name)
    if t == "balance":
        return stock.fetch_balance(req.name)
    if t == "cashflow":
        return stock.fetch_cashflow(req.name)
    if t == "dividend":
        return stock.fetch_dividend(req.name)
    if t == "split":
        return stock.fetch_split(req.name)
    if t == "other":
        return stock.fetch_other(req.name)
    if t == "stock_hist":
        return ns.nse_stock_hist(
            req.date_start, req.date_end, req.name
        ).to_html()

    return common.wrap(f"<h3>Unhandled stock req_type: {t}</h3>")


# -------------------------------------------------------
# INDEX handler
# -------------------------------------------------------
def handle_index(req: FetchRequest):
    t = req.req_type.lower()

    if t == "indices":
        return indices.build_indices_html()
    if t == "open":
        return live.build_index_live_html()
    if t == "preopen":
        return pre.build_preopen_html()
    if t == "fno":
        return fno.nse_fno_html(req.date_end, req.name)
    if t == "fiidii":
        return ns.nse_fiidii()
    if t == "events":
        return ns.nse_events()

    if t == "index_highlow":
        return ns.nse_highlow(req.date_end)
    if t == "stock_highlow":
        return ns.stock_highlow(req.date_end)
    if t == "bhav":
        return bhav.build_bhavcopy_html(req.date_end)
    if t == "largedeals":
        return ns.nse_largedeals()
    if t == "bulkdeals":
        return ns.nse_bulkdeals()
    if t == "blockdeals":
        return ns.nse_blockdeals()
    if t == "most_active":
        return ns.nse_most_active()
    if t == "index_history":
        return ns.index_history("NIFTY", req.date_start, req.date_end)
    if t == "Hlargedeals":
        return ns.nse_largedeals_historical(
            req.date_start, req.date_end
        )
    if t == "pe_pb":
        return ns.index_pe_pb_div(
            "NIFTY", req.date_start, req.date_end
        )
    if t == "total_returns":
        return ns.index_total_returns(
            "NIFTY", req.date_start, req.date_end
        )

    return common.wrap(f"<h3>Unhandled index req_type: {t}</h3>")


# -------------------------------------------------------
# SCREENER handler
# -------------------------------------------------------
def handle_screener(req: FetchRequest):
    return screener.fetch_screener(req.req_type.lower())



# -------------------------------------------------------
# HTML builder for req_type discovery
# -------------------------------------------------------
def build_req_type_list_html():
    html = ["<div id='req_type_list'>"]

    # STOCK & INDEX
    for mode, items in REQ_TYPE_MAP.items():
        html.append(f"<h3>{mode.upper()}</h3><ul>")
        for it in items:
            html.append(
                f"<li class='{mode}-req' data-mode='{mode}'>{it}</li>"
            )
        html.append("</ul>")

    # SCREENER (keys extracted from screener.py)
    html.append("<h3>SCREENER</h3><ul>")
    for key in SCREENER_MAP.keys():
        html.append(
            f"<li class='screener-req' data-mode='screener'>{key}</li>"
        )
    html.append("</ul></div>")

    return "".join(html)
