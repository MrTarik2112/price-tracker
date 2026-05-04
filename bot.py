import requests
import json
import re

URL = "https://www.domirobot.com/anycubic-kobra-3-v2-combo-3d-yazici-pmu7732"

HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_price():
    r = requests.get(URL, headers=HEADERS, timeout=20)
    html = r.text

    match = re.search(r'"price"\s*:\s*"([0-9.]+)"', html)
    return float(match.group(1)) if match else None

def load_price():
    try:
        return json.load(open("price.json"))["price"]
    except:
        return None

def save_price(p):
    json.dump({"price": p}, open("price.json", "w"))

price = get_price()
old = load_price()

print("Fiyat:", price)

if price:
    if old and old != price:
        print("DEĞİŞİM:", old, "→", price)

    save_price(price)
