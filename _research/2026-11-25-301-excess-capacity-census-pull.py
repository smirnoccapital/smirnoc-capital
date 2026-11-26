"""Pull US imports for consumption by HTS10 x country from the Census API.
Usage: python -I pull_census.py OUTDIR   (key read from env CENSUS_KEY)
Pulls: annual 2024 and 2025 (YR vars at Dec), plus each 2026 month available (MO vars).
"""
import os, sys, json, time, urllib.request, urllib.parse, pathlib
import pandas as pd

KEY = os.environ["CENSUS_KEY"]
OUT = pathlib.Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
BASE = "https://api.census.gov/data/timeseries/intltrade/imports/hs"
CTY = {  # Census country codes
    "China": "5700", "EU": "0003", "Japan": "5880", "Korea": "5800", "Taiwan": "5830",
    "Switzerland": "4419", "Singapore": "5590", "India": "5330", "Vietnam": "5520",
    "Thailand": "5490", "Malaysia": "5570", "Indonesia": "5600", "Cambodia": "5550",
    "Bangladesh": "5380",
}

def get(params):
    params = dict(params, key=KEY)
    url = BASE + "?" + urllib.parse.urlencode(params, safe=",")
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=180) as r:
                body = r.read().decode()
            if not body.strip():
                return None
            rows = json.loads(body)
            return pd.DataFrame(rows[1:], columns=rows[0])
        except urllib.error.HTTPError as e:
            if e.code == 204:
                return None
            if attempt == 3: raise
        except Exception:
            if attempt == 3: raise
        time.sleep(3 * (attempt + 1))

def pull(period, suffix):
    frames = []
    for name, code in CTY.items():
        df = get({"get": f"CTY_CODE,CTY_NAME,I_COMMODITY,CON_VAL_{suffix},DUT_VAL_{suffix},CAL_DUT_{suffix}",
                  "time": period, "COMM_LVL": "HS10", "CTY_CODE": code})
        if df is None:
            print(period, name, "no data"); return None
        df["economy"] = name
        frames.append(df)
        print(period, name, len(df), "rows")
    return pd.concat(frames)

for yr in ("2024", "2025"):
    d = pull(f"{yr}-12", "YR")
    d.to_csv(OUT / f"hs10_{yr}_annual.csv", index=False)

for m in range(1, 13):
    per = f"2026-{m:02d}"
    if (OUT / f"hs10_{per}.csv").exists():
        continue
    d = pull(per, "MO")
    if d is None:
        break
    d.to_csv(OUT / f"hs10_{per}.csv", index=False)
