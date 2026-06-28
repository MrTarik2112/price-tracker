import json
from bot import fetch, parse_price, stock_check, load_products


def main():
    products = load_products()
    if not products:
        print("products.json bulunamadı veya ürün listesi boş")
        return

    failures = 0
    print("\n🔎 PRICE CHECK STARTED\n")
    for product in products:
        key = product.get("id", "unknown")
        url = product.get("url")
        print(f"-- {key} --")
        html = fetch(url)
        if not html:
            print("  ❌ sayfa alınamadı")
            failures += 1
            continue

        price = parse_price(html, url)
        status = stock_check(html, url)

        if price is None:
            print("  ❌ fiyat: null")
            print(f"  url: {url}")
            failures += 1
        else:
            print(f"  ✅ fiyat: {price}")
            print(f"  📦 status: {status}")

    print(f"\n✔ CHECK DONE — {failures} problem bulundu")


if __name__ == "__main__":
    main()
