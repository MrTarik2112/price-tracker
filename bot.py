import requests
import json
import re
from datetime import datetime

PRODUCTS_FILE = "products.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
    "Accept-Language": "tr-TR,tr;q=0.9"
}

# =========================
def now():
    return datetime.now().strftime("%Y-%m-%d -- %H:%M:%S")

# =========================
def load_products():
    try:
        data = json.load(open(PRODUCTS_FILE, encoding="utf-8"))
        return data.get("products", [])
    except:
        return []

# =========================
def fetch(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        return r.text if r.status_code == 200 else None
    except:
        return None

# =========================
def parse_price(html):
    if not html:
        return None

    def normalize(value):
        value = value.strip().replace(".", "").replace(",", ".")
        return float(value)

    patterns = [
        r'"price"\s*:\s*"([0-9.,]+)"',
        r'data-price=["\']([0-9.,]+)["\']',
        r'([0-9]+(?:\.[0-9]{3})*(?:,[0-9]{2})?)\s*(?:TL|₺)',
    ]

    for pattern in patterns:
        m = re.search(pattern, html)
        if m:
            try:
                return normalize(m.group(1))
            except:
                continue

    return None

# =========================
def stock_check(html):
    if not html:
        return "unknown"

    t = html.lower()
    out_phrases = [
        "stokta yok",
        "stok yok",
        "tükendi",
        "tukendi",
        "stokta kalmadı",
        "stokta yok",
        "tükenmiş",
    ]

    for phrase in out_phrases:
        if phrase in t:
            return "out_of_stock"

    return "in_stock"

# =========================
def load(file):
    try:
        data = json.load(open(file))

        if isinstance(data, list):
            return migrate_legacy(data)

        return data
    except:
        return None

# =========================
def save(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

# =========================
def migrate_legacy(old):
    prices = [x.get("price", 0) for x in old]

    return {
        "product": {},
        "current": {
            "price": prices[-1] if prices else 0,
            "status": "unknown"
        },
        "history": old
    }

# =========================
def new_db(name, url, price, status):
    return {
        "product": {
            "name": name,
            "url": url,
            "first_seen": now(),
            "last_seen": now()
        },
        "current": {
            "price": price,
            "status": status
        },
        "stats": {
            "min_price": price,
            "max_price": price,
            "total_changes": 0,
            "trend": "stable",
            "avg_hold_time": "0"
        },
        "history": []
    }

# =========================
def compute_stats(db):
    history = db.get("history", [])
    prices = [entry.get("price") for entry in history if isinstance(entry.get("price"), (int, float))]

    if not prices:
        current_price = db.get("current", {}).get("price")
        return {
            "min_price": current_price,
            "max_price": current_price,
            "total_changes": 0,
            "trend": "stable",
            "avg_hold_time": "0"
        }

    min_price = min(prices)
    max_price = max(prices)
    total_changes = sum(1 for entry in history if entry.get("changed"))

    trend_value = "stable"
    if len(prices) >= 2:
        first = prices[0]
        last = prices[-1]
        if last > first:
            trend_value = "up"
        elif last < first:
            trend_value = "down"

    return {
        "min_price": min_price,
        "max_price": max_price,
        "total_changes": total_changes,
        "trend": trend_value,
        "avg_hold_time": "0"
    }

# =========================
def add_snapshot(db, price, status):
    last_price = db["current"].get("price")

    snapshot = {
        "time": now(),
        "price": price,
        "status": status,
        "changed": price != last_price
    }

    db["history"].append(snapshot)

    # keep only last 500 logs (performance)
    db["history"] = db["history"][-500:]

    return last_price

# =========================
def trend(db):
    h = db["history"]
    if len(h) < 2:
        return "stable"

    first = h[0]["price"]
    last = h[-1]["price"]

    if last > first:
        return "up"
    if last < first:
        return "down"
    return "stable"

# =========================
def process(key, info):
    print(f"\n================ {key.upper()} ================")

    html = fetch(info["url"])
    price = parse_price(html)
    status = stock_check(html)

    if price is None:
        print("❌ fiyat alınamadı")
        return

    db = load(info["file"])

    if not db:
        db = new_db(info["name"], info["url"], price, status)

    last_price = add_snapshot(db, price, status)

    # update current always
    db["current"]["price"] = price
    db["current"]["status"] = status
    db["product"]["last_seen"] = now()
    db["stats"] = compute_stats(db)

    print("💰 fiyat:", price)
    print("📦 status:", status)

    if price != last_price:
        print("🔥 CHANGE DETECTED")
    else:
        print("⏸ no change")

    print("📊 trend:", db["stats"]["trend"])

    save(info["file"], db)

# =========================
def main():
    print("\n🚀 PRO PRICE TRACKER STARTED\n")

    products = load_products()

    if not products:
        print("❌ products.json bulunamadı veya ürün listesi boş")
        return

    for product in products:
        process(product.get("id", "unknown"), product)

    print("\n✔ DONE")

# =========================
if __name__ == "__main__":
    main()