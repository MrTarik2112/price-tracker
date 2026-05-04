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
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/120",
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

    m = re.search(r"(\d{4,6})", html)
    if m:
        return float(m.group(1))

    return None

# =========================
def stock_check(html):
    if not html:
        return "unknown"

    if "stokta yok" in html.lower() or "tükendi" in html.lower():
        return "out_of_stock"

    return "in_stock"

# =========================
def load(file):
    try:
        return json.load(open(file))
    except:
        return None

# =========================
def save(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

# =========================
def new_db(name, url, price, status):
    return {
        "product": {
            "name": name,
            "url": url,
            "last_update": now()
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
def duration(start, end):
    try:
        t1 = datetime.strptime(start, "%Y-%m-%d -- %H:%M:%S")
        t2 = datetime.strptime(end, "%Y-%m-%d -- %H:%M:%S")
        d = t2 - t1
        return f"{d.days}g {d.seconds//3600}s {(d.seconds%3600)//60}dk"
    except:
        return "?"

# =========================
def update_stats(db):
    prices = [h["price"] for h in db["history"]] + [db["current"]["price"]]

    db["stats"]["min_price"] = min(prices)
    db["stats"]["max_price"] = max(prices)
    db["stats"]["total_changes"] = len(db["history"])

    if len(prices) > 1:
        if prices[-1] > prices[0]:
            db["stats"]["trend"] = "up"
        elif prices[-1] < prices[0]:
            db["stats"]["trend"] = "down"
        else:
            db["stats"]["trend"] = "stable"

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

    # first run
    if not db:
        db = new_db(info["name"], info["url"], price, status)
        save(info["file"], db)
        print("📌 ilk kayıt oluşturuldu")
        return

    last_price = db["current"]["price"]

    # same price
    if price == last_price:
        print("⏸ değişim yok")
        db["product"]["last_update"] = now()
        db["current"]["status"] = status
        save(info["file"], db)
        return

    # PRICE CHANGE
    print("🔥 FİYAT DEĞİŞTİ")
    print(f"📦 eski: {last_price}")
    print(f"💰 yeni: {price}")

    db["history"].append({
        "price": last_price,
        "start": db["product"]["last_update"],
        "end": now(),
        "duration": duration(db["product"]["last_update"], now())
    })

    db["current"]["price"] = price
    db["current"]["status"] = status
    db["product"]["last_update"] = now()

    update_stats(db)

    save(info["file"], db)

    print("📊 stats güncellendi")

# =========================
def main():
    print("\n🚀 ULTRA JSON ENGINE STARTED\n")

    for k, v in URLS.items():
        process(k, v)

    print("\n✔ DONE")

# =========================
if __name__ == "__main__":
    main()