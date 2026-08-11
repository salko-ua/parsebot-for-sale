import requests
from flask import Flask

app = Flask(__name__)

LISTING = "https://www.olx.ua/d/uk/obyavlenie/arenda-3-komnatnogo-doma-na-ul-izvilistaya-tsna-znizhena-do-60-000-ID10YI6N.html"


@app.route("/")
def probe():
    lines = []
    try:
        info = requests.get("https://ipinfo.io/json", timeout=15).json()
        lines.append(f"host IP: {info.get('ip')} | {info.get('org')} | {info.get('country')}")
    except Exception as e:
        lines.append(f"ipinfo failed: {e}")

    for name, url in [("OLX homepage", "https://www.olx.ua/"), ("OLX listing", LISTING)]:
        try:
            r = requests.get(url, timeout=20)
            verdict = "UNBLOCKED ✅" if r.status_code == 200 else f"BLOCKED ❌"
            lines.append(f"{name}: {r.status_code} {verdict}")
        except Exception as e:
            lines.append(f"{name}: request failed: {e}")

    return "<pre>" + "\n".join(lines) + "</pre>"
