import requests
import json
import re
import time
from datetime import datetime

URL = "https://www.domirobot.com/anycubic-kobra-3-v2-combo-3d-yazici-pmu7732"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
}

# =========================
# UTIL: FORMAT PRICE
# =========================
def format_price(p):
    try:
        p = float(p)
        return f"{p:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return str(p)

# =========================
# FETCH WITH RETRY
# =========================
def fetch_html(retries=3):
    for i in range(retries):
        try:
            r = requests.get(URL, headers=HEADERS, timeout=15)
            if r.status_code == 200:
                return r.text
        except:
            time.sleep(2)
    return None

# =========================
# PARSE PRICE (SMART)
# =========================
def extract_price(html):
    if not html:
        return None

    # 1) JSON-LD (EN GÜVENLİ)
    match = re.search(r'"price"\s*:\s*"([0-9.]+)"', html)
    if match:
        return float(match.group(1))

    # 2) fallback: meta / data-layer
    match = re.search(r'data-price="([0-9.,]+)"', html)
    if match:
        return float(match.group(1).replace(",", "."))

    # 3) brute fallback
    match = re.search(r"(\d{4,6})", html)
    if match:
        return float(match.group(1))

    return None

# =========================
# FILE STORAGE
# =========================
def load_last():
    try:
        return json.load(open("price.json"))["price"]
    except:
        return None

def save(price):
    json.dump({
        "price": price,
        "time": datetime.now().isoformat()
    }, open("price.json", "w"), indent=2)

# =========================
# CHANGE ANALYSIS
# =========================
def analyze_change(old, new):
    if not old:
        return None

    diff = new - old
    percent = (diff / old) * 100

    return {
        "diff": diff,
        "percent": percent
    }

# =========================
# MAIN ENGINE
# =========================
def main():
    print("\n🚀 PRICE TRACKER ENGINE STARTED\n")

    html = fetch_html()
    price = extract_price(html)
    old = load_last()

    if price:
        print("💰 Güncel Fiyat:", format_price(price), "TL")

        if old:
            print("📦 Eski Fiyat:", format_price(old), "TL")

            change = analyze_change(old, price)
            if change:
                sign = "📈" if change["diff"] > 0 else "📉"
                print(f"{sign} Değişim: {change['diff']:.2f} TL ({change['percent']:.2f}%)")

                # büyük değişim alert
                if abs(change["percent"]) > 5:
                    print("🔥 ÖNEMLİ FİYAT DEĞİŞİMİ!")

        save(price)

    else:
        print("❌ Fiyat çekilemedi (site yapısı değişmiş olabilir)")

    print("\n✔ Done at:", datetime.now().isoformat())

# =========================
if __name__ == "__main__":
    main()
