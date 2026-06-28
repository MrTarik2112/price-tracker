const REFRESH_MS = 10000;

// =========================
// SAFE FETCH
// =========================
async function getJSON(file) {
  try {
    const path = file.endsWith(".json")
      ? `./${file}?v=${Date.now()}`
      : `./${file}.json?v=${Date.now()}`;

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

function formatValue(value) {
  return value === undefined || value === null ? "-" : value;
}

// =========================
// RENDER CARD (WITH LINK)
// =========================
function renderCard(product, data) {
  if (!data || !data.current) {
    return `
      <h2>📦 ${product.name}</h2>
      <div>❌ veri yok / json hatalı</div>
      <div style="margin-top:12px">
        <a href="${product.url}" target="_blank" class="button">🔗 Ürüne Git</a>
      </div>
    `;
  }

  const c = data.current;
  const s = data.stats || {};
  const p = data.product || {};

  return `
    <h2>📦 ${formatValue(p.name ?? product.name)}</h2>

    <div style="font-size:30px;font-weight:700;color:#00ff9d">
      ${formatValue(c.price)} TL
    </div>

    <div style="margin-top:8px">
      📊 Durum: ${formatValue(c.status)}<br>
      📈 Trend: ${formatValue(s.trend)}
    </div>

    <div style="margin-top:10px">
      🔻 Min: ${formatValue(s.min_price)} TL<br>
      🔺 Max: ${formatValue(s.max_price)} TL<br>
      🔁 Değişim: ${formatValue(s.total_changes)}
    </div>

    <div style="margin-top:12px">
      <a href="${formatValue(p.url ?? product.url)}" target="_blank" class="button">🔗 Ürüne Git</a>
    </div>

    <div style="margin-top:10px;opacity:0.6">
      🕒 Son: ${formatValue(p.last_seen ?? p.last_update)}
    </div>
  `;
}

// =========================
// LOAD ALL DATA
// =========================
async function loadAll() {
  const productsResponse = await getJSON("products");
  const products = productsResponse?.products || [];
  const grid = document.getElementById("products-grid");

  if (!grid) {
    console.error("❌ DIV YOK: products-grid");
    return;
  }

  if (!products.length) {
    grid.innerHTML = "<div class='empty'>❌ products.json yüklenemedi</div>";
    return;
  }

  grid.innerHTML = "";

  for (const product of products) {
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `<h2>📦 ${product.name}</h2><div class="loading">Yükleniyor...</div>`;
    grid.appendChild(card);

    const data = await getJSON(product.file);
    card.innerHTML = renderCard(product, data);
  }
}

// =========================
// INIT
// =========================
function start() {
  console.log("🚀 PRICE TRACKER DASHBOARD STARTED");

  loadAll();
  setInterval(loadAll, REFRESH_MS);
}

// =========================
start();