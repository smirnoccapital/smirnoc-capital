#!/usr/bin/env python3
"""Fetch US grain futures quotes from Yahoo Finance and write them to
assets/data/futures.json for the sidebar widget to read."""

import datetime
import json
import sys
import urllib.request

SYMBOLS = {
    "corn": {"symbol": "ZC=F", "label": "Corn", "unit": "¢/bu"},
    "soybeans": {"symbol": "ZS=F", "label": "Soybeans", "unit": "¢/bu"},
    "soymeal": {"symbol": "ZM=F", "label": "Soybean Meal", "unit": "$/ton"},
    "soyoil": {"symbol": "ZL=F", "label": "Soybean Oil", "unit": "¢/lb"},
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

OUTPUT_PATH = "assets/data/futures.json"


def fetch(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.load(resp)

    meta = data["chart"]["result"][0]["meta"]
    price = meta.get("regularMarketPrice")
    prev_close = meta.get("previousClose") or meta.get("chartPreviousClose")

    change = None
    change_pct = None
    if price is not None and prev_close:
        change = price - prev_close
        change_pct = (change / prev_close) * 100

    return {
        "price": price,
        "previous_close": prev_close,
        "change": change,
        "change_pct": change_pct,
        "market_time": meta.get("regularMarketTime"),
    }


def main():
    out = {
        "updated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "quotes": {},
    }

    failures = []
    for key, info in SYMBOLS.items():
        try:
            quote = fetch(info["symbol"])
        except Exception as exc:  # noqa: BLE001 - report and keep going
            failures.append(f"{info['symbol']}: {exc}")
            continue
        quote.update(symbol=info["symbol"], label=info["label"], unit=info["unit"])
        out["quotes"][key] = quote

    with open(OUTPUT_PATH, "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")

    if failures:
        print("Some symbols failed to fetch:\n" + "\n".join(failures), file=sys.stderr)
        if not out["quotes"]:
            sys.exit(1)


if __name__ == "__main__":
    main()
