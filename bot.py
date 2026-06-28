import requests
import json
import re
from datetime import datetime
from urllib.parse import urlparse

PRODUCTS_FILE = "products.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
    "Accept-Language": "tr-TR,tr;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
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
def get_fetch_url(url):
    try:
        parsed = urlparse(url)
        if parsed.hostname and parsed.hostname.endswith("porima3d.com") and parsed.path.startswith("/products/") and not parsed.path.endswith(".json"):
            return f"{url.rstrip('/')}.json"
    except:
        pass
    return url

# =========================
def fetch(url):
    try:
        source_url = get_fetch_url(url)
        r = requests.get(source_url, headers=HEADERS, timeout=12)
        return r.text if r.status_code == 200 else None
    except:
        return None

# =========================
def normalize_price(value):
    if value is None:
        return None

    value = str(value).strip()
    value = value.replace("\u00A0", "").replace("\u202F", "").replace(" ", "")

    if "." in value and "," in value:
        # Most likely: 29.990,99 or 1.234.567,89
        if value.rfind(".") < value.rfind(","):
            value = value.replace(".", "").replace(",", ".")
        else:
            value = value.replace(",", "")
    elif "," in value:
        value = value.replace(",", ".")

    try:
        return float(value)
    except:
        return None


def best_price(candidates):
    candidates = [p for p in candidates if isinstance(p, (int, float)) and p > 0]
    if not candidates:
        return None
    return min(candidates)


def extract_json_price(text):
    try:
        data = json.loads(text)
    except:
        return None

    if isinstance(data, dict):
        # Shopify-style product JSON payload
        product = data.get("product") or data
        if isinstance(product, dict):
            variants = product.get("variants") or []
            if variants and isinstance(variants, list):
                first = variants[0]
                if isinstance(first, dict):
                    return first.get("price") or first.get("compare_at_price")
            if "price" in product:
                return product.get("price")

        # Generic JSON price key lookup
        for key in ("price", "amount", "price_amount", "price_value"):
            if key in data:
                return data.get(key)

    return None


def parse_price_robotistan(html):
    patterns = [
        r'KDV Dahil Fiyat.*?<span[^>]*class=["\']product-price["\'][^>]*>([0-9.,]+)</span>',
        r'İndirimli Fiyat.*?<span[^>]*class=["\']product-price["\'][^>]*>([0-9.,]+)</span>',
        r'KDV Dahil Fiyat.*?<span[^>]*class=["\']product-price-not-discounted["\'][^>]*>([0-9.,]+)</span>',
        r'Fiyat.*?<span[^>]*class=["\']product-price-not-vat["\'][^>]*>([0-9.,]+)</span>',
    ]
    candidates = []
    for pattern in patterns:
        for m in re.finditer(pattern, html, re.I | re.S):
            price = normalize_price(m.group(1))
            if price is not None:
                candidates.append(price)

    if candidates:
        return best_price(candidates)

    for m in re.finditer(r'<span[^>]*class=["\']product-price[^"\']*["\']?[^>]*>([0-9.,]+)</span>', html, re.I | re.S):
        price = normalize_price(m.group(1))
        if price is not None:
            candidates.append(price)

    return best_price(candidates) or parse_price_generic(html)


def parse_price_3dcim(html):
    keys = [
        "indirimliFiyatiStr",
        "satisFiyatiStr",
        "urunSepetFiyatiStr",
        "urunFiyatiOrjinalStr",
        "urunFiyatiOrjinalKurHaricStr",
    ]
    candidates = []
    for key in keys:
        pattern = rf'{key}"\s*:\s*"([0-9.,]+)\s*₺"'
        for m in re.finditer(pattern, html, re.I):
            price = normalize_price(m.group(1))
            if price is not None:
                candidates.append(price)

    if candidates:
        return best_price(candidates)

    for m in re.finditer(r'<span[^>]*class=["\']?money["\']?[^>]*>([0-9.,]+)\s*₺</span>', html, re.I | re.S):
        price = normalize_price(m.group(1))
        if price is not None:
            candidates.append(price)

    return best_price(candidates) or parse_price_generic(html)


def parse_price_porima3d(html):
    json_price = extract_json_price(html)
    if json_price is not None:
        price = normalize_price(json_price)
        if price is not None:
            return price

    candidates = []
    for m in re.finditer(r'<span[^>]*class=["\']?money["\']?[^>]*>([0-9.,]+)\s*TL</span>', html, re.I | re.S):
        price = normalize_price(m.group(1))
        if price is not None:
            candidates.append(price)

    if candidates:
        return best_price(candidates)

    return parse_price_generic(html)


def parse_price_generic(html):
    json_price = extract_json_price(html)
    if json_price is not None:
        price = normalize_price(json_price)
        if price is not None:
            return price

    patterns = [
        r'"price"\s*:\s*"([0-9.,]+)"',
        r'"price"\s*:\s*([0-9]+(?:[.,][0-9]{2})?)',
        r'data-price=["\']([0-9.,]+)["\']',
        r'Fiyat[\s\u00A0\u202F]*[:\-]?[\s\u00A0\u202F]*([0-9]+(?:[.,][0-9]{2})?)\s*(?:TL|₺)',
        r'([0-9]+(?:[.,][0-9]{2})?)\s*(?:TL|₺)',
    ]
    candidates = []
    for pattern in patterns:
        for m in re.finditer(pattern, html, re.I):
            price = normalize_price(m.group(1))
            if price is not None:
                candidates.append(price)

    return best_price(candidates)


def parse_price(html, url=None):
    if not html:
        return None

    hostname = ""
    if url:
        try:
            hostname = urlparse(url).hostname or ""
        except:
            hostname = ""

    if hostname.endswith("robotistan.com"):
        return parse_price_robotistan(html)
    if hostname.endswith("3dcim.com"):
        return parse_price_3dcim(html)
    if hostname.endswith("porima3d.com"):
        return parse_price_porima3d(html)

    return parse_price_generic(html)

# =========================

def stock_check_meta(html):
    m = re.search(r'property=["\']product:availability["\'][^>]*content=["\']([^"\']+)["\']', html, re.I)
    if m:
        value = m.group(1).strip().lower()
        if "in stock" in value:
            return "in_stock"
        if "out of stock" in value:
            return "out_of_stock"
    return None


def stock_check_robotistan(html):
    status = stock_check_meta(html)
    if status:
        return status

    if re.search(r'"available"\s*:\s*false', html, re.I):
        return "out_of_stock"
    if re.search(r'"available"\s*:\s*true', html, re.I):
        return "in_stock"

    text = html.lower()
    for phrase in ["stokta yok", "stok yok", "tükendi", "tukendi", "stokta kalmadı", "tükenmiş"]:
        if phrase in text:
            return "out_of_stock"
    for phrase in ["stoktan teslimat", "stokta", "stok var", "mevcut", "sepete ekle"]:
        if phrase in text:
            return "in_stock"

    return None


def stock_check_3dcim(html):
    status = stock_check_meta(html)
    if status:
        return status

    text = html.lower()
    if "stoktan teslimat" in text or "yarın kargoda" in text or "stoktan" in text:
        return "in_stock"
    if "stokta yok" in text or "stok yok" in text or "tükendi" in text:
        return "out_of_stock"
    return None


def stock_check_generic(html):
    if not html:
        return "unknown"

    status = stock_check_meta(html)
    if status:
        return status

    def extract_json_stock(text):
        try:
            data = json.loads(text)
        except:
            return None

        if isinstance(data, dict):
            if data.get("available") is False:
                return "out_of_stock"
            if data.get("available") is True:
                return "in_stock"

            if "inventory_quantity" in data:
                qty = data.get("inventory_quantity")
                if isinstance(qty, int) and qty <= 0:
                    return "out_of_stock"
                if isinstance(qty, int) and qty > 0:
                    return "in_stock"

            product = data.get("product") or data
            if isinstance(product, dict):
                variants = product.get("variants") or []
                if variants and isinstance(variants, list):
                    first = variants[0]
                    if isinstance(first, dict):
                        if first.get("available") is False:
                            return "out_of_stock"
                        if first.get("available") is True:
                            return "in_stock"
                        qty = first.get("inventory_quantity")
                        if isinstance(qty, int) and qty <= 0:
                            return "out_of_stock"
                        if isinstance(qty, int) and qty > 0:
                            return "in_stock"
        return None

    status = extract_json_stock(html)
    if status:
        return status

    if re.search(r'"available"\s*:\s*false', html, re.I):
        return "out_of_stock"
    if re.search(r'"available"\s*:\s*true', html, re.I):
        return "in_stock"
    if re.search(r'"inventory_quantity"\s*:\s*0', html, re.I):
        return "out_of_stock"

    t = html.lower()
    for phrase in ["stokta yok", "stok yok", "tükendi", "tukendi", "stokta kalmadı", "tükenmiş"]:
        if phrase in t:
            return "out_of_stock"
    for phrase in ["stoktan teslimat", "stokta", "stok var", "mevcut", "sepete ekle"]:
        if phrase in t:
            return "in_stock"

    return "in_stock"


def stock_check(html, url=None):
    if not html:
        return "unknown"

    hostname = ""
    if url:
        try:
            hostname = urlparse(url).hostname or ""
        except:
            hostname = ""

    if hostname.endswith("robotistan.com"):
        status = stock_check_robotistan(html)
        if status:
            return status
    if hostname.endswith("3dcim.com"):
        status = stock_check_3dcim(html)
        if status:
            return status

    return stock_check_generic(html)

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
    price = parse_price(html, info["url"])
    status = stock_check(html, info["url"])

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