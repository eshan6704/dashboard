from nsepython import *
import pandas as pd
import json

def build_index_live_html(name=""):
    # Fetch live index data
    p = nse_index_live()  # default if name=""

    full_df = p.get("data", pd.DataFrame())
    rem_df  = p.get("rem", pd.DataFrame())
    print(full_df)
    print(rem_df)
    # Convert DataFrames to JSON
    rem_json  = json.dumps(rem_df.to_dict(orient="records"), ensure_ascii=False)
    full_json = json.dumps(full_df.to_dict(orient="records"), ensure_ascii=False)
    print(rem_json)
    print(full_json)
    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
body {{ font-family: Arial; margin:15px; background:#f5f5f5; }}
table {{ border-collapse: collapse; width: 100%; margin-bottom:20px; }}
th, td {{ border:1px solid #ccc; padding:6px 8px; text-align:left; }}
th {{ background:#333; color:white; }}
</style>
</head>
<body>

<h2>Live Index Data: {name or 'Default Index'}</h2>

<h3>Index Info (rem)</h3>
<table id="remTable"></table>

<h3>Index Data (full)</h3>
<table id="fullTable"></table>

<script>
const remData = {rem_json};
const fullData = {full_json};

function fillTable(id, rows) {{
    const table = document.getElementById(id);
    if (!rows.length) {{
        table.innerHTML = "<tr><td>No data</td></tr>";
        return;
    }}
    let keys = Object.keys(rows[0]);
    let thead = "<tr>";
    keys.forEach(k => thead += `<th>${{k}}</th>`);
    thead += "</tr>";

    let tbody = "";
    rows.forEach(r => {{
        tbody += "<tr>";
        keys.forEach(k => tbody += `<td>${{r[k]}}</td>`);
        tbody += "</tr>";
    }});

    table.innerHTML = thead + tbody;
}}

fillTable("remTable", remData);
fillTable("fullTable", fullData);
</script>

</body>
</html>
"""
    return html
