const FILES = {
  acik: "acik.json",
  kapali: "kapali.json"
};

const REFRESH_MS = 10000;

// =========================
// SAFE FETCH (GITHUB PAGES FIXED)
// =========================
async function getJSON(file) {
  try {
    // 🔥 FIX: relative root + cache breaker
    const path = "./" + file + "?v=" + Date.now();

    const res = await fetch(path);

    if (!res.ok) {
      console.log("HTTP ERROR:", file, res.status);
      return null;
    }

    const data = await res.json();

    console.log("LOADED:", file, data);
    return data;

  } catch (err) {
    console.log("FETCH ERROR:", file, err);
    return null;
  }
}

// =========================
// RENDER CARD
// =========================
function render(data, elementId) {
  const el = document.getElementById(elementId);

  if (!el) {
    console.error("❌ DIV YOK:", elementId);
    return;
  }

  if (!data || !data.current) {
    el.innerHTML = "❌ veri yok / json hatalı";
    return;
  }

  const c = data.current;
  const s = data.stats || {};
  const p = data.product || {};

  el.innerHTML = `
    <div style="font-size:28px;font-weight:bold;color:#00ff9d">
      ${c.price ?? "-"} TL
    </div>

    <div style="margin-top:10px">
      📦 ${p.name ?? "-"}<br>
      📊 Durum: ${c.status ?? "-"}<br>
      📈 Trend: ${s.trend ?? "-"}<br>
    </div>

    <div style="margin-top:10px">
      🔻 Min: ${s.min_price ?? "-"}<br>
      🔺 Max: ${s.max_price ?? "-"}<br>
      🔁 Değişim: ${s.total_changes ?? 0}
    </div>

    <div style="margin-top:10px;opacity:0.6">
      🕒 Son: ${p.last_update ?? "-"}
    </div>
  `;
}

// =========================
// LOAD ALL
// =========================
async function loadAll() {
  const acik = await getJSON(FILES.acik);
  const kapali = await getJSON(FILES.kapali);

  render(acik, "acik");
  render(kapali, "kapali");
}

// =========================
// INIT
// =========================
function start() {
  console.log("🚀 DASHBOARD START");

  loadAll();
  setInterval(loadAll, REFRESH_MS);
}

// =========================
start();