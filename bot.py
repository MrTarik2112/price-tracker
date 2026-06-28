import requests
import json
import re
from datetime import datetime

URLS = {
    "acik": {
        "name": "Anycubic Kobra 3 V2 Combo",
        "url": "https://www.domirobot.com/anycubic-kobra-3-v2-combo-3d-yazici-pmu7732",
        "file": "acik.json"
    },
    "kapali": {
        "name": "Anycubic Kobra S1 Combo",
        "url": "https://www.domirobot.com/anycubic-kobra-s1-combo-3d-yazici-pmu7374",
        "file": "kapali.json"
    }
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
    "Accept-Language": "tr-TR,tr;q=0.9"
}

# =========================
def now():
    return datetime.now().strftime("%Y-%m-%d -- %H:%M:%S")

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

    m = re.search(r'"price"\s*:\s*"([0-9.]+)"', html)
    if m:
        return float(m.group(1))

    m = re.search(r'data-price="([0-9.,]+)"', html)
    if m:
        return float(m.group(1).replace(",", "."))

    return None

# =========================
def stock_check(html):
    if not html:
        return "unknown"

    t = html.lower()
    if "stokta yok" in t or "tükendi" in t:
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
        "history": []
    }

# =========================
def add_snapshot(db, price, status):
    last_price = db["current"]["price"]

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

    if not price:
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

    print("💰 fiyat:", price)
    print("📦 status:", status)

    if price != last_price:
        print("🔥 CHANGE DETECTED")
    else:
        print("⏸ no change")

    print("📊 trend:", trend(db))

    save(info["file"], db)

# =========================
def main():
    print("\n🚀 PRO PRICE TRACKER STARTED\n")

    for k, v in URLS.items():
        process(k, v)

    print("\n✔ DONE")

# =========================
if __name__ == "__main__":
    main()