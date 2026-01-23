# import all modules you need for stock/index/screener
from .. import stock, eq_html as eq, indices_html as indices
from .. import index_live_html as live, preopen_html as pre
from .. import bhavcopy_html as bhav, build_nse_fno as fno
from .. import nsepythonmodified as ns, yahooinfo, screener, daily
from .. import common

def handle_stock(req):
    t = req.req_type.lower()
    if t == "info": return yahooinfo.fetch_info(req.name)
    if t == "intraday": return stock.fetch_intraday(req.name)
    if t == "daily": return daily.fetch_daily(req.name, req.end_date, req.start_date)
    if t == "nse_eq": return eq.build_eq_html(req.name)
    if t == "qresult": return stock.fetch_qresult(req.name)
    if t == "result": return stock.fetch_result(req.name)
    if t == "balance": return stock.fetch_balance(req.name)
    if t == "cashflow": return stock.fetch_cashflow(req.name)
    if t == "dividend": return stock.fetch_dividend(req.name)
    if t == "split": return stock.fetch_split(req.name)
    if t == "other": return stock.fetch_other(req.name)
    if t == "stock_hist": return ns.nse_stock_hist(req.start_date, req.end_date, req.name).to_html()
    return common.wrap(f"<h3>Unhandled stock req_type: {t}</h3>")

def handle_index(req):
    t = req.req_type.lower()
    if t == "indices": return indices.build_indices_html()
    if t == "open": return live.build_index_live_html(req.name)
    if t == "preopen": return pre.build_preopen_html(req.name)
    if t == "fno": return fno.nse_fno_html(req.end_date, req.name)
    if t == "fiidii": return ns.nse_fiidii()
    if t == "events": return ns.nse_events()
    if t == "index_highlow": return ns.nse_highlow(req.end_date)
    if t == "stock_highlow": return ns.stock_highlow(req.end_date)
    if t == "bhav": return bhav.build_bhavcopy_html(req.end_date)
    if t == "largedeals": return ns.nse_largedeals()
    if t == "bulkdeals": return ns.nse_bulkdeals()
    if t == "blockdeals": return ns.nse_blockdeals()
    if t == "most_active": return ns.nse_most_active()
    if t == "index_history": return ns.index_history("NIFTY", req.start_date, req.end_date)
    if t == "hlargedeals": return ns.nse_largedeals_historical(req.start_date, req.end_date)
    if t == "pe_pb": return ns.index_pe_pb_div("NIFTY", req.start_date, req.end_date)
    if t == "total_returns": return ns.index_total_returns("NIFTY", req.start_date, req.end_date)
    return common.wrap(f"<h3>Unhandled index req_type: {t}</h3>")

def handle_screener(req):
    return screener.fetch_screener(req.req_type.lower())
