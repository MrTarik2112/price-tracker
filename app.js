const FILES = {
  acik: "acik.json",
  kapali: "kapali.json"
};

const REFRESH_MS = 10000;

// =========================
// FETCH JSON (CACHE SAFE)
// =========================
async function getJSON(file) {
  try {
    const res = await fetch(file + "?v=" + Date.now());

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
    console.error("❌ HTML element yok:", elementId);
    return;
  }

  if (!data) {
    el.innerHTML = "❌ Veri yüklenemedi";
    return;
  }

  if (!data.current || !data.stats) {
    console.log("BROKEN JSON:", data);
    el.innerHTML = "❌ JSON format hatalı";
    return;
  }

  const c = data.current;
  const s = data.stats;
  const p = data.product;

  el.innerHTML = `
    <div class="price">${c.price ?? "-"} TL</div>

    <div class="meta">
      <div>📦 Ürün: ${p?.name ?? "-"}</div>
      <div>📊 Durum: ${c.status ?? "-"}</div>
      <div>📈 Trend: ${s.trend ?? "-"}</div>

      <div style="margin-top:10px">
        🔻 Min: ${s.min_price ?? "-"} TL<br>
        🔺 Max: ${s.max_price ?? "-"} TL<br>
        🔁 Değişim: ${s.total_changes ?? 0}
      </div>

      <div style="margin-top:10px;opacity:0.7">
        🕒 Son güncelleme:<br>
        ${p?.last_update ?? "-"}
      </div>
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
  loadAll();
  setInterval(loadAll, REFRESH_MS);
}

// =========================
start();