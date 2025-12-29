import requests
import pandas as pd
from bs4 import BeautifulSoup
from typing import List, Tuple

from . import persist


# ===============================
# Screener name → URL mapping
# ===============================
SCREENER_MAP = {
    "top_gainers": "https://www.screener.in/screens/3355081/from-high/",
    "top_losers": "https://www.screener.in/screens/7055/top-losers/",
    "high_volume": "https://www.screener.in/screens/3352/high-volume-stocks/",
    "breakout_stocks": "https://www.screener.in/screens/1849/breakout-stocks/",
    "fifty_two_wk_high": "https://www.screener.in/screens/3588/52-week-high/",
    "fifty_two_wk_low": "https://www.screener.in/screens/3589/52-week-low/",
    "new_highs": "https://www.screener.in/screens/4921/new-highs/",
    "new_lows": "https://www.screener.in/screens/4922/new-lows/",
    "rsi_oversold": "https://www.screener.in/screens/1751/rsi-oversold-stocks/",
    "rsi_overbought": "https://www.screener.in/screens/1750/rsi-overbought-stocks/",
    "price_above_sma": "https://www.screener.in/screens/1764/price-above-sma/",
    "large_cap": "https://www.screener.in/screens/3360/large-cap-stocks/",
    "mid_cap": "https://www.screener.in/screens/3361/mid-cap-stocks/",
    "small_cap": "https://www.screener.in/screens/3362/small-cap-stocks/",
}


# ===============================
# Public API
# ===============================
def fetch_screener(screen_name: str) -> str:
    """
    Returns a fully styled HTML table for a given screener name.
    Uses disk persistence (HTML primary, CSV secondary).
    """

    if screen_name not in SCREENER_MAP:
        return _error_html(f"Invalid screener: {screen_name}")

    cache_name = f"SCREENER_{screen_name.upper()}"

    # 1️⃣ Cache hit
    if persist.exists(cache_name, "html"):
        return persist.load(cache_name, "html")

    # 2️⃣ Fetch live
    headers, rows = _fetch_table(SCREENER_MAP[screen_name])

    if not headers or not rows:
        return _error_html("No data available")

    # 3️⃣ Build outputs
    html = _build_html(headers, rows)
    csv_df = pd.DataFrame(rows, columns=headers)

    # 4️⃣ Persist
    persist.save(cache_name, html, "html")
    persist.save(cache_name, csv_df, "csv")

    return html


# ===============================
# Internal helpers
# ===============================
def _fetch_table(url: str) -> Tuple[List[str], List[List[str]]]:
    r = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=15
    )
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table")
    if not table:
        return [], []

    thead = table.find("thead")
    header_row = thead.find("tr") if thead else table.find("tr")
    headers = [th.get_text(strip=True) for th in header_row.find_all("th")]

    rows = []
    for tr in table.find_all("tr")[1:]:
        cells = tr.find_all("td")
        if cells:
            rows.append([td.get_text(strip=True) for td in cells])

    return headers, rows


def _build_html(headers: List[str], rows: List[List[str]]) -> str:
    style = """
    <style>
        .screener-wrap {
            width: 100%;
            overflow-x: auto;
            font-family: Arial, sans-serif;
        }
        table.screener {
            border-collapse: collapse;
            width: 100%;
            min-width: 900px;
            font-size: 13px;
        }
        table.screener th {
            position: sticky;
            top: 0;
            background: #1e293b;
            color: #ffffff;
            padding: 8px;
            border: 1px solid #334155;
            white-space: nowrap;
        }
        table.screener td {
            padding: 6px 8px;
            border: 1px solid #e5e7eb;
            white-space: nowrap;
        }
        table.screener tr:nth-child(even) {
            background: #f8fafc;
        }
        table.screener tr:hover {
            background: #e0f2fe;
        }
    </style>
    """

    html = [style, "<div class='screener-wrap'>", "<table class='screener'>"]

    html.append("<tr>")
    for h in headers:
        html.append(f"<th>{h}</th>")
    html.append("</tr>")

    for row in rows:
        html.append("<tr>")
        for cell in row:
            html.append(f"<td>{cell}</td>")
        html.append("</tr>")

    html.append("</table></div>")
    return "".join(html)


def _error_html(msg: str) -> str:
    return f"""
    <div style="
        color:#b91c1c;
        background:#fee2e2;
        padding:12px;
        border-radius:6px;
        font-family:Arial;
    ">
        ❌ {msg}
    </div>
    """