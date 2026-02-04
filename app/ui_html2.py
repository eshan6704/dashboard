HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Stock / Index UI</title>
</head>
<body>

<select id="mode">
  <option value="stock">stock</option>
  <option value="index">index</option>
  <option value="screener">screener</option>
</select>

<select id="req_type"></select>
<select id="name"></select>

<input id="date_start" placeholder="dd-mm-yyyy">
<input id="date_end" placeholder="dd-mm-yyyy">

<button onclick="fetchData()">Fetch</button>

<div id="response">Loading...</div>

<script>
const API="/api/fetch";
let META={stock:[],index:[],screener:[]};

async function init(){
  const r=await fetch(API,{
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({mode:"list"})
  });
  const html=await r.text();
  const doc=new DOMParser().parseFromString(html,"text/html");

  doc.querySelectorAll("li").forEach(li=>{
    META[li.dataset.mode].push({
      type:li.dataset.type,
      names:(li.dataset.names||"").split(",").filter(Boolean)
    });
  });
  updateReq();
}

function updateReq(){
  req_type.innerHTML="";
  META[mode.value].forEach(x=>{
    let o=document.createElement("option");
    o.value=x.type;o.text=x.type;
    req_type.appendChild(o);
  });

  if(mode.value==="stock") req_type.value="info";
  if(mode.value==="index") req_type.value="indices";
  if(mode.value==="screener") req_type.value="from-high";
  updateName();
}

function updateName(){
  name.innerHTML="";
  const r=META[mode.value].find(x=>x.type===req_type.value);
  if(r && r.names.length){
    r.names.forEach(n=>{
      let o=document.createElement("option");
      o.value=n;o.text=n;
      name.appendChild(o);
    });
  } else {
    name.innerHTML="<option></option>";
  }
}

async function fetchData(){
  const p={
    mode:mode.value,
    req_type:req_type.value,
    name:name.value,
    date_start:date_start.value,
    date_end:date_end.value
  };
  const r=await fetch(API,{
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify(p)
  });
  response.innerHTML=await r.text();
}

mode.onchange=updateReq;
req_type.onchange=updateName;
init();
</script>
</body>
</html>
"""
