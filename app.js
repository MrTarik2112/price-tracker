const CONFIG = {
  acik: "acik.json",
  kapali: "kapali.json",
  refreshMs: 10000
};

// =========================
async function fetchJSON(file) {
  try {
    const res = await fetch(file + "?t=" + Date.now()); // cache breaker
    if (!res.ok) throw new Error("HTTP " + res.status);
    return await res.json();
  } catch (err) {
    console.log("Fetch error:", file, err);
    return null;
  }
}

// =========================
function formatTime(t) {
  if (!t) return "-";
  return t;
}

// =========================
function renderCard(data, el) {
  if (!data || !data.current) {
    el.innerHTML = `
      <div class="error">❌ Veri yok / JSON hatalı</div>
    `;
    return;
  }

  const c = data.current;
  const s = data.stats || {};
  const p = data.product || {};

  el.innerHTML = `
    <div class="price">${c.price ?? "-"} TL</div>

    <div class="info">
      <div>📦 Durum: ${c.status ?? "-"}</div>
      <div>📈 Trend: ${s.trend ?? "-"}</div>
      <div>🔻 Min: ${s.min_price ?? "-"}</div>
      <div>🔺 Max: ${s.max_price ?? "-"}</div>
      <div>🔁 Değişim: ${s.total_changes ?? 0}</div>
      <div>🕒 Son: ${formatTime(p.last_update)}</div>
    </div>
  `;
}

// =========================
async function loadAll() {
  const acikData = await fetchJSON(CONFIG.acik);
  const kapaliData = await fetchJSON(CONFIG.kapali);

  renderCard(acikData, document.getElementById("acik"));
  renderCard(kapaliData, document.getElementById("kapali"));
}

// =========================
function start() {
  loadAll();
  setInterval(loadAll, CONFIG.refreshMs);
}

// =========================
start();