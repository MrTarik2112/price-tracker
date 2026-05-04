const FILES = {
  acik: "acik",
  kapali: "kapali"
};

const REFRESH_MS = 10000;

// =========================
// SAFE FETCH (GITHUB PAGES FIXED)
// =========================
async function getJSON(file) {
  try {
    // 🔥 KRİTİK FIX: always .json + relative safe path
    const path = `./${file}.json?v=${Date.now()}`;

    const res = await fetch(path);

    if (!res.ok) {
      console.log("❌ HTTP ERROR:", path, res.status);
      return null;
    }

    return await res.json();

  } catch (err) {
    console.log("❌ FETCH ERROR:", file, err);
    return null;
  }
}

// =========================
// RENDER SAFE UI
// =========================
function render(data, elementId) {
  const el = document.getElementById(elementId);

  if (!el) return;

  if (!data || !data.current) {
    el.innerHTML = "❌ veri yok / json hatalı";
    return;
  }

  const c = data.current;
  const s = data.stats || {};
  const p = data.product || {};

  el.innerHTML = `
    <div style="font-size:30px;font-weight:700;color:#00ff9d">
      ${c.price ?? "-"} TL
    </div>

    <div style="margin-top:8px">
      📦 ${p.name ?? "-"}<br>
      📊 Durum: ${c.status ?? "-"}<br>
      📈 Trend: ${s.trend ?? "-"}
    </div>

    <div style="margin-top:10px">
      🔻 Min: ${s.min_price ?? "-"} TL<br>
      🔺 Max: ${s.max_price ?? "-"} TL<br>
      🔁 Değişim: ${s.total_changes ?? 0}
    </div>

    <!-- 💥 LINK EKLENDİ -->
    <div style="margin-top:12px">
      <a href="${p.url ?? "#"}"
         target="_blank"
         style="
           display:inline-block;
           padding:8px 12px;
           background:#00ff9d;
           color:#000;
           font-weight:bold;
           border-radius:8px;
           text-decoration:none;
         ">
        🔗 Ürüne Git
      </a>
    </div>

    <div style="margin-top:10px;opacity:0.6">
      🕒 Son: ${p.last_update ?? "-"}
    </div>
  `;
}

// =========================
// LOAD ALL DATA
// =========================
async function loadAll() {
  const acik = await getJSON(FILES.acik);
  const kapali = await getJSON(FILES.kapali);

  render(acik, "acik");
  render(kapali, "kapali");
}

// =========================
// INIT SYSTEM
// =========================
function start() {
  console.log("🚀 PRICE DASHBOARD STARTED");

  loadAll();
  setInterval(loadAll, REFRESH_MS);
}

// =========================
start();