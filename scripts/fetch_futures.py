#!/usr/bin/env python3
"""Fetch US grain futures data from Yahoo Finance for the sidebar widget.

Two modes, run on separate schedules so the small, frequently-updated
quote file doesn't get dragged down by the much larger 1-year history:

    python fetch_futures.py quotes   -> assets/data/futures.json
    python fetch_futures.py history  -> assets/data/futures_history.json
"""

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

QUOTES_PATH = "assets/data/futures.json"
HISTORY_PATH = "assets/data/futures_history.json"


def fetch_chart(symbol, params=""):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}{params}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.load(resp)["chart"]["result"][0]


def fetch_quote(symbol):
    meta = fetch_chart(symbol)["meta"]
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


def fetch_history(symbol):
    result = fetch_chart(symbol, "?range=1y&interval=1d")
    dates = []
    closes = []
    timestamps = result.get("timestamp") or []
    closes_raw = result.get("indicators", {}).get("quote", [{}])[0].get("close") or []
    for ts, close in zip(timestamps, closes_raw):
        if close is None:
            continue
        day = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).date()
        dates.append(day.isoformat())
        closes.append(round(close, 4))
    return {"dates": dates, "closes": closes}


def run(mode, fetch_one, path):
    out = {
        "updated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        mode: {},
    }

    failures = []
    for key, info in SYMBOLS.items():
        try:
            item = fetch_one(info["symbol"])
        except Exception as exc:  # noqa: BLE001 - report and keep going
            failures.append(f"{info['symbol']}: {exc}")
            continue
        item.update(symbol=info["symbol"], label=info["label"], unit=info["unit"])
        out[mode][key] = item

    with open(path, "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")

    if failures:
        print("Some symbols failed to fetch:\n" + "\n".join(failures), file=sys.stderr)
        if not out[mode]:
            sys.exit(1)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "quotes"
    if mode == "quotes":
        run("quotes", fetch_quote, QUOTES_PATH)
    elif mode == "history":
        run("history", fetch_history, HISTORY_PATH)
    else:
        sys.exit(f"Unknown mode: {mode!r} (expected 'quotes' or 'history')")


if __name__ == "__main__":
    main()
