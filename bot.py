import requests
import json
import re
from datetime import datetime

URLS = {
    "acik": "https://www.domirobot.com/anycubic-kobra-3-v2-combo-3d-yazici-pmu7732",
    "kapali": "https://www.domirobot.com/anycubic-kobra-s1-combo-3d-yazici-pmu7374"
}

FILES = {
    "acik": "acik.json",
    "kapali": "kapali.json"
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

    # JSON-LD
    m = re.search(r'"price"\s*:\s*"([0-9.]+)"', html)
    if m:
        return float(m.group(1))

    # data-price
    m = re.search(r'data-price="([0-9.,]+)"', html)
    if m:
        return float(m.group(1).replace(",", "."))

    # fallback
    m = re.search(r"(\d{4,6})", html)
    if m:
        return float(m.group(1))

    return None

# =========================
def is_out_of_stock(html):
    if not html:
        return True

    keywords = [
        "stokta yok",
        "tükendi",
        "out of stock",
        "sold out"
    ]

    return any(k.lower() in html.lower() for k in keywords)

# =========================
def load(file):
    try:
        data = json.load(open(file))
        return data if isinstance(data, list) else []
    except:
        return []

# =========================
def save(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

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
def process(name, url, file):
    print(f"\n================ {name.upper()} =================")

    html = fetch(url)

    if is_out_of_stock(html):
        print("⚠️ STOKTA YOK")
        return

    price = parse_price(html)
    db = load(file)

    if not price:
        print("❌ fiyat okunamadı")
        return

    print("💰 fiyat:", price)

    if not db:
        db.append({
            "price": price,
            "start": now(),
            "end": now()
        })
        save(file, db)
        print("📌 ilk kayıt")
        return

    last = db[-1]

    if price == last["price"]:
        print("⏸ değişim yok")
        return

    # close old
    last["end"] = now()

    print("🔥 FİYAT DEĞİŞTİ")
    print("📦 eski:", last["price"])
    print("⏳ süre:", duration(last["start"], last["end"]))

    db.append({
        "price": price,
        "start": now(),
        "end": now()
    })

    save(file, db)

# =========================
def main():
    print("\n🚀 DUAL PRICE TRACKER STARTED\n")

    process("ACIK KASA", URLS["acik"], FILES["acik"])
    process("KAPALI KASA", URLS["kapali"], FILES["kapali"])

    print("\n✔ DONE")

# =========================
if __name__ == "__main__":
    main()