const FILES = {
  acik: "acik",
  kapali: "kapali"
};

const REFRESH = 10000;

// =========================
async function getJSON(file) {
  try {
    const res = await fetch(`./${file}.json?v=${Date.now()}`);
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

// =========================
function getBadge(trend){
  if(trend === "up") return `<span class="badge up">📈 Artıyor</span>`;
  if(trend === "down") return `<span class="badge down">📉 Düşüyor</span>`;
  return `<span class="badge stable">➡ Stabil</span>`;
}

// =========================
function render(data, id){

  const el = document.getElementById(id);
  if(!el) return;

  if(!data){
    el.innerHTML = "❌ veri yok";
    return;
  }

  const c = data.current;
  const s = data.stats || {};
  const p = data.product || {};

  el.innerHTML = `
    <div class="price">${c.price} TL</div>

    ${getBadge(s.trend)}

    <div class="meta">
      📦 ${p.name}<br>
      📊 ${c.status}<br><br>

      🔻 Min: ${s.min_price} TL<br>
      🔺 Max: ${s.max_price} TL<br>
      🔁 Değişim: ${s.total_changes}<br><br>

      🕒 Son: ${p.last_update}
    </div>
  `;
}

// =========================
async function load(){
  render(await getJSON(FILES.acik), "acik");
  render(await getJSON(FILES.kapali), "kapali");
}

// =========================
load();
setInterval(load, REFRESH);