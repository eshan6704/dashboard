# ui_html.py
from . import screener

def build_frontend_html():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Stock / Index Backend UI</title>

<style>
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 10px;
}
.controls {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}
select, input, button {
    padding: 6px;
    font-size: 14px;
}
#response {
    margin-top: 15px;
    padding: 10px;
    border: 1px solid #ccc;
    height: calc(100vh - 120px);
    overflow: auto;
}
</style>
</head>

<body>

<h2>Stock / Index Fetcher</h2>

<div class="controls">
    <select id="mode">
        <option value="stock">stock</option>
        <option value="index">index</option>
        <option value="screener">screener</option>
    </select>

    <select id="req_type"></select>
    <select id="name"></select>

    <input id="date_start" placeholder="YYYY-MM-DD">
    <input id="date_end" placeholder="YYYY-MM-DD">

    <button onclick="fetchData()">Fetch</button>
</div>

<div id="response">Loading req_type list...</div>

<script>
const API_URL = "/api/fetch";
let REQ_MAP = {};

/* ---------------- LOAD LIST ---------------- */
async function loadReqTypes() {
    const res = await fetch(API_URL, {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ mode: "list" })
    });

    const html = await res.text();
    const doc = new DOMParser().parseFromString(html, "text/html");

    REQ_MAP = { stock: [], index: [], screener: [] };

    doc.querySelectorAll("li").forEach(li => {
        const mode = li.dataset.mode;
        const type = li.dataset.type;
        const names = (li.dataset.names || "").split(",").filter(Boolean);

        if (mode && type) {
            REQ_MAP[mode].push({ type, names });
        }
    });

    updateReqType();
}

/* ---------------- REQ TYPE ---------------- */
function updateReqType() {
    const mode = document.getElementById("mode").value;
    const sel = document.getElementById("req_type");
    sel.innerHTML = "";

    REQ_MAP[mode].forEach(r => {
        const o = document.createElement("option");
        o.value = r.type;
        o.textContent = r.type;
        sel.appendChild(o);
    });

    if (mode === "stock") sel.value = "info";
    if (mode === "index") sel.value = "indices";
    if (mode === "screener") sel.value = "from-high";

    updateName();
}

/* ---------------- NAME ---------------- */
function updateName() {
    const mode = document.getElementById("mode").value;
    const rt = document.getElementById("req_type").value;
    const sel = document.getElementById("name");
    sel.innerHTML = "";

    const entry = REQ_MAP[mode].find(r => r.type === rt);

    if (entry && entry.names.length) {
        entry.names.forEach(n => {
            const o = document.createElement("option");
            o.value = n;
            o.textContent = n;
            sel.appendChild(o);
        });
    } else {
        const o = document.createElement("option");
        o.value = "";
        o.textContent = "-- none --";
        sel.appendChild(o);
    }

    if (mode === "stock") sel.value = "ITC";
    if (mode === "index") sel.value = "NIFTY 50";
}

/* ---------------- FETCH ---------------- */
async function fetchData() {
    const payload = {
        mode: mode.value,
        req_type: req_type.value,
        name: name.value,
        date_start: date_start.value,
        date_end: date_end.value
    };

    const res = await fetch(API_URL, {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify(payload)
    });

    document.getElementById("response").innerHTML = await res.text();
}

/* EVENTS */
mode.addEventListener("change", updateReqType);
req_type.addEventListener("change", updateName);

loadReqTypes();
</script>

</body>
</html>
"""
