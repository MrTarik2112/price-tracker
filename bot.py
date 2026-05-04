import requests
import json
import re
from datetime import datetime

URL = "https://www.domirobot.com/anycubic-kobra-3-v2-combo-3d-yazici-pmu7732"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/120",
    "Accept-Language": "tr-TR,tr;q=0.9"
}

# =========================
def now():
    return datetime.now().isoformat()

# =========================
def fetch():
    try:
        r = requests.get(URL, headers=HEADERS, timeout=15)
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
def load_db():
    try:
        data = json.load(open("price.json"))
        return data if isinstance(data, list) else []
    except:
        return []

# =========================
def save_db(db):
    with open("price.json", "w") as f:
        json.dump(db, f, indent=2)

# =========================
def duration(start, end):
    try:
        t1 = datetime.fromisoformat(start)
        t2 = datetime.fromisoformat(end)
        d = t2 - t1

        h = d.seconds // 3600
        m = (d.seconds % 3600) // 60

        return f"{d.days}d {h}h {m}m"
    except:
        return "?"

# =========================
def stats(db):
    prices = [x["price"] for x in db]
    return {
        "min": min(prices) if prices else 0,
        "max": max(prices) if prices else 0,
        "count": len(db)
    }

# =========================
def trend(db):
    if len(db) < 2:
        return "stable"

    first = db[0]["price"]
    last = db[-1]["price"]

    if last > first:
        return "📈 yükseliyor"
    elif last < first:
        return "📉 düşüyor"
    return "➡ stabil"

# =========================
def main():
    print("\n🚀 ULTRA PRICE ENGINE STARTED\n")

    html = fetch()
    price = parse_price(html)
    db = load_db()

    if not price:
        print("❌ fiyat okunamadı")
        return

    print("💰 Güncel:", price, "TL")

    # first run
    if not db:
        db.append({
            "price": price,
            "start": now(),
            "end": now()
        })
        save_db(db)
        print("📌 ilk kayıt")
        return

    last = db[-1]

    # same price
    if price == last["price"]:
        print("⏸ değişim yok")
        print("📊 Trend:", trend(db))
        return

    # close previous period
    last["end"] = now()

    print("\n🔥 FİYAT DEĞİŞTİ!")
    print(f"📦 eski: {last['price']} TL")
    print(f"⏳ süre: {duration(last['start'], last['end'])}")

    # new entry
    db.append({
        "price": price,
        "start": now(),
        "end": now()
    })

    save_db(db)

    # analytics
    s = stats(db)

    print("\n📊 ANALİZ")
    print(f"🔻 min: {s['min']} TL")
    print(f"🔺 max: {s['max']} TL")
    print(f"🔁 değişim sayısı: {s['count']}")
    print(f"📈 trend: {trend(db)}")

# =========================
if __name__ == "__main__":
    main()