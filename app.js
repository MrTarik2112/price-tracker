async function loadData(file, elementId) {
  try {
    const res = await fetch(file + "?t=" + new Date().getTime());
    const data = await res.json();

    const el = document.getElementById(elementId);

    const current = data.current.price;
    const status = data.current.status;

    el.innerHTML = `
      <div class="price">${current} TL</div>
      <div class="small">Durum: ${status}</div>
      <div class="small">Trend: ${data.stats.trend}</div>
      <div class="small">Min: ${data.stats.min_price} TL</div>
      <div class="small">Max: ${data.stats.max_price} TL</div>
      <div class="small">Değişim: ${data.stats.total_changes}</div>
      <div class="small">Son: ${data.product.last_update}</div>
    `;
  } catch (e) {
    document.getElementById(elementId).innerHTML = "❌ veri yok";
  }
}

function refresh() {
  loadData("acik", "acik");
  loadData("kapali", "kapali");
}

refresh();
setInterval(refresh, 15000); // 15 saniye refresh