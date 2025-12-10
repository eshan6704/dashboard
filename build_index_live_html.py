from nsepython import *
def build_index_live_html(name):
    p = nse_index_live(name)

    full_df = p["data"]
    rem_df  = p["rem"]
    print(full_df)
    main_df = full_df.iloc[[0]] if len(full_df) else pd.DataFrame()
    cons_df = full_df.iloc[1:] if len(full_df) > 1 else pd.DataFrame()

    rem_json  = json.dumps(rem_df.to_dict(orient="records"), ensure_ascii=False)
    main_json = json.dumps(main_df.to_dict(orient="records"), ensure_ascii=False)
    cons_json = json.dumps(cons_df.to_dict(orient="records"), ensure_ascii=False)

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">

<style>
    body {{ font-family: Arial; margin:0; padding:15px; background:#f5f5f5; }}
    h2 {{ margin-top:0; }}
    .section {{ background:white; padding:10px; margin-bottom:20px;
                border-radius:6px; box-shadow:0 2px 4px rgba(0,0,0,0.1); }}

    button {{
        padding:5px 12px; margin:5px 0; cursor:pointer;
        background:#222; color:white; border:none; border-radius:4px;
    }}

    table {{
        width:100%; border-collapse:collapse; margin-top:10px;
        font-size:14px;
    }}
    th, td {{
        padding:6px 8px; border:1px solid #ccc; text-align:left;
    }}
    th {{ background:#333; color:white; }}

    .filter-box {{ margin-bottom:10px; }}
</style>

</head>
<body>

<h2>{name} — Live Index Data</h2>

<!-- ===================== INDEX INFO ==================== -->
<div class="section">
    <h3>Index Info</h3>
    <button onclick="toggle('remTable')">Show / Hide</button>
    <table id="remTable"></table>
</div>

<!-- ===================== MAIN INDEX ROW ==================== -->
<div class="section">
    <h3>Main Index Data</h3>
    <button onclick="toggle('mainTable')">Show / Hide</button>
    <table id="mainTable"></table>
</div>

<!-- ===================== CONSTITUENTS ==================== -->
<div class="section">
    <h3>Constituent Stocks</h3>

    <div class="filter-box">
        <label>Filter by Column:</label>
        <select id="filterCol"></select>

        <label>Value:</label>
        <select id="filterVal"></select>

        <button onclick="applyFilter()">Apply</button>
        <button onclick="resetFilter()">Reset</button>
    </div>

    <button onclick="toggle('consTable')">Show / Hide</button>
    <table id="consTable"></table>
</div>

<script>
    const remData  = {rem_json};
    const mainData = {main_json};
    const consData = {cons_json};
    let consFiltered = [...consData];

    function toggle(id) {{
        const t = document.getElementById(id);
        t.style.display = t.style.display === "none" ? "table" : "none";
    }}

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
    fillTable("mainTable", mainData);
    fillTable("consTable", consFiltered);

    // -------------------- DROPDOWN FILTER --------------------
    const filterCol = document.getElementById("filterCol");
    const filterVal = document.getElementById("filterVal");

    function loadFilterOptions() {{
        if (!consData.length) return;

        let keys = Object.keys(consData[0]);
        filterCol.innerHTML = "";
        keys.forEach(k => filterCol.innerHTML += `<option>${{k}}</option>`);

        updateValues();
    }}

    function updateValues() {{
        let col = filterCol.value;
        let setVals = [...new Set(consData.map(r => r[col]))];
        filterVal.innerHTML = "";
        setVals.forEach(v => filterVal.innerHTML += `<option>${{v}}</option>`);
    }}

    filterCol.onchange = updateValues;
    loadFilterOptions();

    function applyFilter() {{
        let col = filterCol.value;
        let val = filterVal.value;
        consFiltered = consData.filter(r => String(r[col]) === String(val));
        fillTable("consTable", consFiltered);
    }}

    function resetFilter() {{
        consFiltered = [...consData];
        fillTable("consTable", consFiltered);
    }}
</script>

</body>
</html>
"""
    return html
