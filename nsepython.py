import os, sys, requests, pandas as pd, json, random, datetime, time, logging, re, urllib.parse
from collections import Counter

mode = 'local'

# ------------------------- NSE FETCH -------------------------
if mode == "vpn":
    def nsefetch(payload):
        def encode(url): return url if "%26" in url or "%20" in url else urllib.parse.quote(url, safe=":/?&=")
        def refresh_cookies():
            os.popen(f'curl -c cookies.txt "https://www.nseindia.com" {curl_headers}').read()
            os.popen(f'curl -b cookies.txt -c cookies.txt "https://www.nseindia.com/option-chain" {curl_headers}').read()

        if not os.path.exists("cookies.txt"): refresh_cookies()
        encoded = encode(payload)
        cmd = f'curl -b cookies.txt "{encoded}" {curl_headers}'
        raw = os.popen(cmd).read()
        try: return json.loads(raw)
        except:
            refresh_cookies()
            raw = os.popen(cmd).read()
            try: return json.loads(raw)
            except: return {}

if mode == 'local':
    def nsefetch(payload):
        try:
            s = requests.Session()
            s.get("https://www.nseindia.com", headers=headers, timeout=10)
            s.get("https://www.nseindia.com/option-chain", headers=headers, timeout=10)
            return s.get(payload, headers=headers, timeout=10).json()
        except:
            return {}

# ------------------------- HEADERS -------------------------
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9,en-IN;q=0.8,en-GB;q=0.7",
    "cache-control": "max-age=0",
    "priority": "u=0, i",
    "sec-ch-ua": '"Microsoft Edge";v="129","Not=A?Brand";v="8","Chromium";v="129"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"
}

niftyindices_headers = {
    'Connection': 'keep-alive',
    'sec-ch-ua': '"Not;A Brand";v="99","Google Chrome";v="91","Chromium";v="91"',
    'Accept': 'application/json,text/javascript,*/*;q=0.01',
    'DNT': '1',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0',
    'Content-Type': 'application/json; charset=UTF-8',
    'Origin': 'https://niftyindices.com',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://niftyindices.com/reports/historical-data',
    'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8'
}

curl_headers = ''' -H "authority: beta.nseindia.com" -H "cache-control: max-age=0" -H "dnt: 1" -H "upgrade-insecure-requests: 1" -H "user-agent: Mozilla/5.0" -H "sec-fetch-user: ?1" -H "accept: */*" -H "sec-fetch-site: none" -H "accept-language: en-US,en;q=0.9" --compressed'''

run_time = datetime.datetime.now()
indices = ['NIFTY','FINNIFTY','BANKNIFTY']

# ------------------------- HELPERS -------------------------
def nsesymbolpurify(s): return s.replace('&','%26')

def flatten_dict(d, parent="", sep="."):
    items={}
    for k,v in d.items():
        nk = f"{parent}{sep}{k}" if parent else k
        if isinstance(v, dict): items.update(flatten_dict(v, nk, sep))
        else: items[nk] = v
    return items

def flatten_nested(d, prefix=""):
    flat={}
    for k,v in d.items():
        nk = f"{prefix}{k}" if prefix=="" else f"{prefix}.{k}"
        if isinstance(v, dict):
            flat.update(flatten_nested(v, nk))
        elif isinstance(v, list):
            if v and isinstance(v[0], dict):
                for i,x in enumerate(v): flat.update(flatten_nested(x, f"{nk}.{i}"))
            else: flat[nk]=v
        else: flat[nk]=v
    return flat

def rename_col(cols):
    child=[c.split('.')[-1] for c in cols]
    cnt=Counter(child)
    new=[]
    for c,ch in zip(cols,child):
        if cnt[ch]==1: new.append(ch)
        else:
            p=c.split('.')
            new.append(f"{p[-1]}_{p[-2]}" if len(p)>=2 else p[-1])
    return new

def df_from_data(data):
    rows=[ flatten_nested(x) if isinstance(x,dict) else {"value":x} for x in data ]
    df=pd.DataFrame(rows)
    df.columns=rename_col(df.columns)
    return df

# ------------------------- API FUNCTIONS -------------------------
def indices():
    p=nsefetch("https://www.nseindia.com/api/allIndices")
    return {"data":pd.DataFrame(p.pop("data")), "dates":pd.DataFrame([p.pop("dates")]), "indices":pd.DataFrame([p])}

def eq(symbol):
    symbol=nsesymbolpurify(symbol)
    df=nsefetch(f'https://www.nseindia.com/api/quote-equity?symbol={symbol}')
    pre=df.pop('preOpenMarket')
    out={
        "securityInfo": pd.DataFrame([df["securityInfo"]]),
        "priceInfo": pd.DataFrame([flatten_dict(df["priceInfo"])]),
        "industryInfo": pd.DataFrame([df["industryInfo"]]),
        "pdSectorIndAll": pd.DataFrame([df["metadata"].pop("pdSectorIndAll")]),
        "metadata": pd.DataFrame([df["metadata"]]),
        "info": pd.DataFrame([df["info"]]),
        "preOpen": pd.DataFrame(pre.pop('preopen')),
        "preOpenMarket": pd.DataFrame([pre])
    }
    return out

def eq_fno(): return nsefetch('https://www.nseindia.com/api/equity-stockIndices?index=SECURITIES%20IN%20F%26O')
def eq_der(symbol): return nsefetch('https://www.nseindia.com/api/quote-derivative?symbol='+nsesymbolpurify(symbol))
def index_chain(symbol): return nsefetch('https://www.nseindia.com/api/option-chain-indices?symbol='+nsesymbolpurify(symbol))
def eq_chain(symbol): return nsefetch('https://www.nseindia.com/api/option-chain-equities?symbol='+nsesymbolpurify(symbol))
def nse_holidays(t="trading"): return nsefetch('https://www.nseindia.com/api/holiday-master?type='+t)

def nse_results(index="equities",period="Quarterly"):
    if index in ["equities","debt","sme"] and period in ["Quarterly","Annual","Half-Yearly","Others"]:
        return pd.json_normalize(nsefetch(f'https://www.nseindia.com/api/corporates-financial-results?index={index}&period={period}'))
    print("Invalid Input")

def nse_events(): return pd.json_normalize(nsefetch('https://www.nseindia.com/api/event-calendar'))
def nse_past_results(symbol): return nsefetch('https://www.nseindia.com/api/results-comparision?symbol='+nsesymbolpurify(symbol))
def nse_blockdeal(): return nsefetch('https://nseindia.com/api/block-deal')
def nse_marketStatus(): return nsefetch('https://nseindia.com/api/marketStatus')
def nse_circular(mode="latest"):
    return nsefetch('https://www.nseindia.com/api/latest-circular' if mode=="latest" else 'https://www.nseindia.com/api/circulars')

def nse_fiidii(mode="pandas"):
    try:
        p=nsefetch('https://www.nseindia.com/api/fiidiiTradeReact')
        return pd.DataFrame(p) if mode=="pandas" else p
    except:
        return nsefetch('https://www.nseindia.com/api/fiidiiTradeReact')

def nsetools_get_quote(symbol):
    p=nsefetch('https://www.nseindia.com/api/equity-stockIndices?index=SECURITIES%20IN%20F%26O')
    for x in p['data']:
        if x['symbol']==symbol.upper(): return x

def nse_index():
    p=nsefetch('https://iislliveblob.niftyindices.com/jsonfiles/LiveIndicesWatch.json')
    return pd.DataFrame(p['data'])

def index_history(sym,sd,ed):
    d={'cinfo':f"{{'name':'{sym}','startDate':'{sd}','endDate':'{ed}','indexName':'{sym}'}}"}
    p=json.loads(requests.post('https://niftyindices.com/Backpage.aspx/getHistoricaldatatabletoString', headers=niftyindices_headers, json=d).json()["d"])
    return pd.DataFrame.from_records(p)

def index_pe_pb_div(sym,sd,ed):
    d={'cinfo':f"{{'name':'{sym}','startDate':'{sd}','endDate':'{ed}','indexName':'{sym}'}}"}
    p=json.loads(requests.post('https://niftyindices.com/Backpage.aspx/getpepbHistoricaldataDBtoString', headers=niftyindices_headers, json=d).json()["d"])
    return pd.DataFrame.from_records(p)

def index_total_returns(sym,sd,ed):
    d={'cinfo':f"{{'name':'{sym}','startDate':'{sd}','endDate':'{ed}','indexName':'{sym}'}}"}
    p=json.loads(requests.post('https://niftyindices.com/Backpage.aspx/getTotalReturnIndexString', headers=niftyindices_headers, json=d).json()["d"])
    return pd.DataFrame.from_records(p)

def get_bhavcopy(d): return pd.read_csv("https://archives.nseindia.com/products/content/sec_bhavdata_full_"+d.replace("-","")+".csv")
def get_bulkdeals(): return pd.read_csv("https://archives.nseindia.com/content/equities/bulk.csv")
def get_blockdeals(): return pd.read_csv("https://archives.nseindia.com/content/equities/block.csv")

def nse_preopen(key="NIFTY"):
    p=nsefetch("https://www.nseindia.com/api/market-data-pre-open?key="+key)
    return {"data":df_from_data(p.pop("data")), "rem":df_from_data([p])}

def nse_most_active(t="securities",s="value"):
    return pd.DataFrame(nsefetch(f"https://www.nseindia.com/api/live-analysis-most-active-{t}?index={s}")["data"])

def nse_eq_symbols():
    return pd.read_csv('https://archives.nseindia.com/content/equities/EQUITY_L.csv')['SYMBOL'].tolist()

def nse_price_band_hitters(b="both",v="AllSec"):
    p=nsefetch("https://www.nseindia.com/api/live-analysis-price-band-hitter")
    return {"data":pd.DataFrame(p[b][v]["data"]), "count":pd.DataFrame([p['count']])}

def nse_largedeals(mode="bulk_deals"):
    p=nsefetch('https://www.nseindia.com/api/snapshot-capital-market-largedeal')
    return pd.DataFrame(p["BULK_DEALS_DATA" if mode=="bulk_deals" else "SHORT_DEALS_DATA" if mode=="short_deals" else "BLOCK_DEALS_DATA"])

def nse_largedeals_historical(f,t,mode="bulk_deals"):
    m = "bulk-deals" if mode=="bulk_deals" else "short-selling" if mode=="short_deals" else "block-deals"
    p=nsefetch(f'https://www.nseindia.com/api/historical/{m}?from={f}&to={t}')
    return pd.DataFrame(p["data"])

def stock_hist(f,t,symbol,series="ALL"):
    url=f"https://www.nseindia.com/api/historical/securityArchives?from={f}&to={t}&symbol={symbol.upper()}&dataType=priceVolumeDeliverable&series={series}"
    return pd.DataFrame(nsefetch(url)['data'])

def nse_index_live(name="NIFTY 50"):
    p=nsefetch(f"https://www.nseindia.com/api/equity-stockIndices?index={name.replace(' ','%20')}")
    return {"data":df_from_data(p.pop("data")) if "data" in p else pd.DataFrame(), "rem":df_from_data([p])}
