function render(data, elementId) {
  const el = document.getElementById(elementId);

  if (!data || !data.current) {
    el.innerHTML = "❌ veri yok";
    return;
  }

  const c = data.current;
  const s = data.stats || {};
  const p = data.product || {};

  let trendClass = "stable";
  if (s.trend === "up") trendClass = "up";
  if (s.trend === "down") trendClass = "down";

  el.innerHTML = `
    <div class="price">${c.price} TL</div>

    <div class="badge ${trendClass}">
      ${s.trend ?? "stable"}
    </div>

    <div class="meta">
      📦 ${p.name}<br>
      📊 ${c.status}<br><br>

      🔻 Min: ${s.min_price} TL<br>
      🔺 Max: ${s.max_price} TL<br>
      🔁 Değişim: ${s.total_changes}
    </div>

    <div class="meta" style="opacity:0.6;margin-top:10px">
      🕒 ${p.last_update}
    </div>
  `;
}