import json
import pandas as pd
from nsepython import *

def build_indices_html():

    p = indices()

    data_df = p["data"]
    dates_df = p["dates"]

    data_json = json.dumps(data_df.to_dict(orient="records"), ensure_ascii=False)
    dates_json = json.dumps(dates_df.to_dict(orient="records"), ensure_ascii=False)

    DEFAULT_KEY = "INDICES ELIGIBLE IN DERIVATIVES"
    DEFAULT_SYMBOL = "NIFTY 50"

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>NSE Indices Dashboard</title>

<style>
body {{
    font-family: Arial, sans-serif;
    padding: 20px;
}}

button {{
    padding: 7px 14px;
    margin-bottom: 10px;
    cursor: pointer;
}}

.scroll-table {{
    width: 100%;
    overflow: auto;
    border: 1px solid #ccc;
    max-height: 450px;
    margin-bottom: 20px;
}}

table {{
    border-collapse: collapse;
    width: max-content;
    min-width: 100%;
}}

th, td {{
    border: 1px solid #ddd;
    padding: 8px;
    white-space: nowrap;
}}

th {{
    background-color: #007bff;
    color: white;
    position: sticky;
    top: 0;
    z-index: 5;
}}

.chart-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 200px 200px;
    gap: 20px;
}}

.chart-box {{
    width: 100%;
    height: 100%;
    border: 1px solid #ccc;
}}

#chart365 {{
    grid-column: 1 / 3;
}}

select {{
    padding: 6px;
    margin: 8px 0;
}}
</style>

</head>
<body>

<h2>NSE Indices Dashboard</h2>

<script>
const records = {data_json};
const dates = {dates_json};
const DEFAULT_KEY = "{DEFAULT_KEY}";
const DEFAULT_SYMBOL = "{DEFAULT_SYMBOL}";
</script>

<!-- MAIN TABLE -->
<h3>Main Full Indices Table</h3>
<button onclick="toggleMainTable()">Show / Hide Main Table</button>

<div id="mainTableSection" class="scroll-table" style="display:none;">
    <table id="mainTable"></table>
</div>

<hr>

<!-- FILTERED TABLE -->
<h3>Filter Table by Category</h3>

<label><b>Select Index Category:</b></label>
<select id="keyDropdown"></select>

<div id="altTableSection" class="scroll-table">
    <table id="altTable"></table>
</div>

<hr>

<!-- CHARTS -->
<h3>Charts Based on Index</h3>

<label><b>Select Index:</b></label>
<select id="chartDropdown"></select>

<div class="chart-grid">
    <iframe id="chartToday" class="chart-box"></iframe>
    <iframe id="chart30" class="chart-box"></iframe>
    <iframe id="chart365" class="chart-box"></iframe>
</div>

<script>

// ================= MAIN TABLE =================

function buildMainTable() {{
    const table = document.getElementById("mainTable");
    const cols = Object.keys(records[0]);

    let header = "<tr>";
    cols.forEach(c => header += `<th>${{c}}</th>`);
    header += "</tr>";

    let rows = "";
    records.forEach(r => {{
        rows += "<tr>";
        cols.forEach(c => rows += `<td>${{r[c]}}</td>`);
        rows += "</tr>";
    }});

    table.innerHTML = header + rows;
}}

function toggleMainTable() {{
    const sec = document.getElementById("mainTableSection");
    sec.style.display = sec.style.display === "none" ? "block" : "none";
}}

buildMainTable();


// ================= FILTERED TABLE =================

const keyDropdown = document.getElementById("keyDropdown");
const chartDropdown = document.getElementById("chartDropdown");

const keyList = [...new Set(records.map(r => r.key))];
keyList.forEach(k => {{
    const opt = document.createElement("option");
    opt.value = k;
    opt.textContent = k;
    if (k === DEFAULT_KEY) opt.selected = true;
    keyDropdown.appendChild(opt);
}});

function buildAltTable(keyName) {{
    const table = document.getElementById("altTable");

    const filtered = records.filter(r => r.key === keyName);

    if (!filtered.length) {{
        table.innerHTML = "<tr><td>No Data</td></tr>";
        return;
    }}

    const hiddenCols = [
        "key","chartTodayPath","chart30dPath","chart30Path","chart365dPath",
        "date365dAgo","date30dAgo","previousDay","oneWeekAgo","oneMonthAgoVal",
        "oneWeekAgoVal","oneYearAgoVal","index","indicativeClose"
    ];

    const cols = Object.keys(filtered[0]).filter(c => !hiddenCols.includes(c));

    let header = "<tr>";
    cols.forEach(c => header += `<th>${{c}}</th>`);
    header += "</tr>";

    let rows = "";
    filtered.forEach(obj => {{
        rows += "<tr>";
        cols.forEach(c => rows += `<td>${{obj[c]}}</td>`);
        rows += "</tr>";
    }});

    table.innerHTML = header + rows;
}}


// ================= CHARTS =================

function populateChartDropdown(keyVal) {{
    chartDropdown.innerHTML = "";

    records.filter(r => r.key === keyVal).forEach(r => {{
        const opt = document.createElement("option");
        opt.value = r.indexSymbol;
        opt.textContent = r.index;
        chartDropdown.appendChild(opt);
    }});

    // auto select default
    [...chartDropdown.options].forEach(opt => {{
        if (opt.textContent.toUpperCase().includes(DEFAULT_SYMBOL.toUpperCase()))
            opt.selected = true;
    }});
}}

function loadCharts(symbol) {{
    const row = records.find(r => r.indexSymbol === symbol);
    if (!row) return;

    document.getElementById("chartToday").src = row.chartTodayPath;
    document.getElementById("chart30").src = row.chart30dPath || row.chart30Path;
    document.getElementById("chart365").src = row.chart365dPath;
}}


// ================= EVENT HANDLERS =================

keyDropdown.addEventListener("change", () => {{
    const keyVal = keyDropdown.value;
    buildAltTable(keyVal);
    populateChartDropdown(keyVal);
    loadCharts(chartDropdown.value);
}});

chartDropdown.addEventListener("change", () => {{
    loadCharts(chartDropdown.value);
}});


// ================= INITIAL LOAD =================

buildAltTable(DEFAULT_KEY);
populateChartDropdown(DEFAULT_KEY);

let initial = records.find(
    r => r.index.toUpperCase().includes(DEFAULT_SYMBOL.toUpperCase())
);

if (!initial) initial = records[0];

loadCharts(initial.indexSymbol);

</script>

</body>
</html>
"""
    return html
