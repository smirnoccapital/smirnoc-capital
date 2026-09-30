"""
Proxy 45Z scores for US ethanol plants exporting into Canada, from ECCC's approved-CI list,
plus reverse-engineering implied 45Z scores from public 45Z dollar disclosures.
Rev. 3 addendum to 2026-09-28-cfr-multiplier-45z-equalization.py (2026-09-30).

Input: "List of Carbon Intensities Under the Clean Fuel Regulations.csv" (ECCC, updated Sept. 30, 2025)
Usage: python _research/2026-09-30-cfr-ci-list-45z-proxy.py   (run from the SC Project root; chart lands in cwd)

Logic
  CFR CI (g CO2e/MJ, Fuel LCA Model, cradle-to-grave, NO indirect land use change)
    -> proxy 45Z rate (kg CO2e/mmBtu) = CI * 1.055056
    -> 45Z value/gal = amount * (50 - rate)/50, floored at zero   (2026 amount $1.09)
  Parity multiplier, same formula as the 09-28 script:
    M = 1 + (45Z value per litre, CAD) / (CFR value per litre at the Canadian plant's CI, CAD)
  The Canada model has no ILUC, which 45Z also dropped for fuel produced after 2025, so no ILUC
  subtraction is applied (unlike the IRFA/CA-GREET scores in the 09-28 script).
"""
import re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CSV = "_research/List of Carbon Intensities Under the Clean Fuel Regulations.csv"
L_PER_GAL, FX = 3.785411784, 1.414
CI_REF, ED_ETH = 80.1, 23.419e-6
AMT_2026, AMT_2025 = 1.09, 1.06          # 1.00 x 1.0929 (2026); 1.00 x 1.0611 (2025, Form 7218 instr.)
K = 1.055056                             # g/MJ -> kg/mmBtu

def usd_gal(rate, amt=AMT_2026): return max(0.0, amt * (50 - rate) / 50)
def cad_l(rate, amt=AMT_2026): return usd_gal(rate, amt) / L_PER_GAL * FX
def cfr_l(ci, price, ref=CI_REF): return (ref - ci) * ED_ETH * price
def mult(rate, ci_can, price, ref=CI_REF): return 1 + cad_l(rate) / cfr_l(ci_can, price, ref)

# ---- 1. Load and clean --------------------------------------------------
df = pd.read_csv(CSV, skiprows=6, encoding="utf-8-sig")
df.columns = ["app", "fac", "loc", "fuel", "feed", "origin", "type", "scope", "ci", "date", "model", "status"]
eth = df[df.fuel.str.contains("thanol", na=False)].copy()
eth["country"] = eth["loc"].str.extract(r",\s*([A-Z]{2})\s*$")[0]
eth["ci_num"] = pd.to_numeric(eth.ci, errors="coerce")
eth["date"] = pd.to_datetime(eth.date, format="%d-%m-%Y", errors="coerce")
print("Ethanol rows:", len(eth), "| by status:", eth.status.value_counts().to_dict())
print("Country:", eth.country.value_counts(dropna=False).to_dict())

act = eth[(eth.status == "ACTIVE") & eth.ci_num.notna()]
# latest approved numeric CI per facility + feedstock (some plants have several entries)
act = act.sort_values("date").groupby(["fac", "feed"], as_index=False).tail(1)
us = act[act.country == "US"].copy()
ca = act[act["loc"].isin(["Aylmer, CA", "Havelock, CA", "Mooretown, CA"]) & (act.feed == "Corn")].copy()  # Ontario corn plants
conf = eth[(eth.country == "US") & (eth.status == "ACTIVE") & eth.ci_num.isna()].fac.nunique()
pend = eth[(eth.country == "US") & (eth.status == "PENDING APPROVAL")].fac.nunique()
print(f"\nUS plants with an active numeric CI: {us.fac.nunique()}  | active but CONFIDENTIAL CI: {conf}"
      f" | facilities with a pending entry: {pend}")
print(f"Ontario corn plants with an active numeric CI: {ca.fac.tolist()} = {ca.ci_num.tolist()}")
ci_can_mean = ca.ci_num.mean()

# ---- 2. Proxy 45Z value ---------------------------------------------------
us["rate"] = us.ci_num * K
us["usd_gal"] = us.rate.apply(usd_gal)
us["cad_c_l"] = us.rate.apply(cad_l) * 100
us["M300"] = us.rate.apply(lambda r: mult(r, 38, 300))
IOWA = ["Dyersville", "Albert City", "Charles City", "Fort Dodge", "Hartley", "Shenandoah", "Galva", "Marcus", "Fairbank", "Arthur"]
us["state"] = np.where(us["loc"].str.split(",").str[0].isin(IOWA), "IA", "other")
us = us.sort_values("ci_num")
pd.set_option("display.width", 200, "display.max_rows", 200)
print("\n== US plants, active numeric CFR CI (latest entry) ==")
print(us[["fac", "loc", "ci_num", "model", "rate", "usd_gal", "M300"]].round(3).to_string(index=False))

s = us.ci_num
print(f"\nCFR CI (g/MJ): n={len(s)} mean {s.mean():.1f} median {s.median():.1f} min {s.min():.0f} max {s.max():.0f}")
print(f"Proxy 45Z rate (kg/mmBtu): mean {us.rate.mean():.1f}, median {us.rate.median():.1f}")
print(f"Proxy 45Z value US$/gal: mean {us.usd_gal.mean():.3f}, median {us.usd_gal.median():.3f}, "
      f"p10 {us.usd_gal.quantile(.1):.3f}, p90 {us.usd_gal.quantile(.9):.3f}")
print("Share of plants with proxy score < 50 (earns any 45Z):", f"{(us.rate < 50).mean():.0%}")

# Average-plant multiplier: M of the average 45Z value (linear, so = mean of M)
prices = [200, 300, 350, 400]
print("\n== Multiplier at the mean / median / p90 proxy score (Canadian CI 38 | Ontario corn mean %.1f) ==" % ci_can_mean)
for lab, r in [("mean", us.rate.mean()), ("median", us.rate.median()),
               ("p90 (best 10%)", us.rate.quantile(.1)), ("best plant", us.rate.min())]:
    print(f"{lab:16} rate {r:5.1f} ${usd_gal(r):.3f}/gal  M@CI38:", [float(round(mult(r, 38, p), 2)) for p in prices],
          " M@CI%.0f:" % ci_can_mean, [float(round(mult(r, ci_can_mean, p), 2)) for p in prices])

# Differential CFR credits: US plant's own CI earns fewer/more credits than the Canadian plant.
# Exact parity: M_i = (CFR_US_i + 45Z_i) / CFR_CAN
print("\n== Exact per-plant parity, CAD 300 (US plant earns CFR at its own CI) ==")
us["M_exact"] = [(cfr_l(c, 300) + cad_l(r)) / cfr_l(38, 300) for c, r in zip(us.ci_num, us.rate)]
print("mean M_exact %.2f, median %.2f (vs %.2f same-CFR)" % (us.M_exact.mean(), us.M_exact.median(), us.M300.mean()))

# ---- 3. Sensitivity: how wrong can the CFR -> 45Z mapping be? -------------
print("\n== Sensitivity: proxy rate = CFR CI*1.055 + offset (offset captures model differences) ==")
for off in (-5, -2.5, 0, 2.5, 5, 10):
    r = us.rate + off
    v = r.apply(usd_gal)
    print(f"offset {off:+5.1f}: mean rate {r.mean():5.1f}  mean 45Z ${v.mean():.3f}/gal  "
          f"share earning>0 {(r<50).mean():.0%}  M(mean value)@300 = {1 + (v.mean()/L_PER_GAL*FX)/cfr_l(38,300):.2f}")
print("Break-even offset (mean proxy rate -> 50):", round(50 - us.rate.mean(), 1), "kg/mmBtu")

# IRFA-based benchmark from the 09-28 article, for comparison
print("\nComparison: article's Iowa-average 51 kg/mmBtu -> $%.2f/gal; CFR-list mean %.1f -> $%.2f/gal"
      % (usd_gal(51), us.rate.mean(), usd_gal(us.rate.mean())))
ia = us[us.state.isin(["IA"])]
print("Iowa plants in list:", ia.fac.tolist(), "mean CFR CI", round(ia.ci_num.mean(), 1) if len(ia) else None,
      "-> rate", round(ia.rate.mean(), 1) if len(ia) else None)

# ---- 4. Reverse-engineering 45Z scores from public dollar disclosures -------
print("\n== Implied 45Z rate from public disclosures: rate = 50*(1 - credit_per_gal / amount) ==")
def implied(label, usd, gal_m, amt, disc=0.0):
    per = usd / (gal_m * 1e6) / (1 - disc)
    return label, per, 50 * (1 - per / amt)
cases = [
    # Highwater (FYE Oct 31 2025): $10.4M recognized; 70.2M gal annual production rate; credit only from Jan 1, 2025 (10 of 12 months)
    ("Highwater FY25, 12 mo gallons", 10.4e6, 70.2, AMT_2025, 0.0),
    ("Highwater FY25, 10 mo gallons", 10.4e6, 70.2 * 10 / 12, AMT_2025, 0.0),
    # Green Plains H1 2026: $113.9M net of discounts; 334.896M gal produced
    ("Green Plains H1-26, 0% discount", 113.9e6, 334.896, AMT_2026, 0.0),
    ("Green Plains H1-26, 10% discount", 113.9e6, 334.896, AMT_2026, 0.10),
    ("Green Plains Q2-26, 0% discount", 58.7e6, 160.7, AMT_2026, 0.0),
]
for c in cases:
    lab, per, rate = implied(*c)
    print(f"{lab:36} ${per:.3f}/gal -> implied rate {rate:5.1f} kg/mmBtu (= {rate/K:5.1f} g/MJ)")

# ---- 5. Chart: distribution of proxy 45Z value -------------------------------
INK, MUTED, GRID, C1, C2 = "#1f2933", "#6b7280", "#e5e7eb", "#1b6ca8", "#c2571a"
fig, ax = plt.subplots(figsize=(8.2, 6.0), dpi=200)
y = np.arange(len(us))
ax.barh(y, us.usd_gal, color=C1, height=0.72)
ax.set_yticks(y)
ax.set_yticklabels([f"{f.replace('POET Bioprocessing', 'POET').replace(', LLC', '').replace(' LLC', '')[:34]} ({l.split(',')[0]})"
                    for f, l in zip(us.fac, us["loc"])], fontsize=6.5, color=INK)
ax.axvline(us.usd_gal.mean(), color=INK, lw=1.2)
ax.text(us.usd_gal.mean() + 0.006, len(us) - 1, r"Mean of 28 plants: US\$%.2f" % us.usd_gal.mean(), color=INK, fontsize=8.5, va="center")
ax.text(0.335, len(us) - 5.5, r"Earlier Iowa-average" "\n" r"benchmark (score 51)" "\n" r"earns US\$0.00", color=C2, fontsize=8, va="center", ha="right")
ax.set_xlim(0, 0.36)
ax.set_xlabel(r"Proxy 45Z value, US\$ per gallon (CFR CI x 1.055; 2026 amount US\$1.09)", color=MUTED, fontsize=9)
fig.text(0.02, 0.965, "US plants with approved CFR carbon intensities: implied 45Z value", fontsize=11, color=INK, fontweight="bold", ha="left")
ax.grid(axis="x", color=GRID, lw=0.8); ax.set_axisbelow(True)
for sp in ("top", "right"): ax.spines[sp].set_visible(False)
for sp in ("left", "bottom"): ax.spines[sp].set_color(GRID)
ax.tick_params(axis="x", colors=MUTED, labelsize=8.5)
ax.tick_params(axis="y", length=0)
fig.subplots_adjust(left=0.36, top=0.93, bottom=0.08, right=0.97)
fig.savefig("cfr-ci-list-45z-proxy.png", facecolor="white")
print("chart saved")

# ---- 6. Gevo North Dakota (Richardton, capture-equipped) -- added after review ----
# 2025: US$52M of credits sold, ~69M gal produced (Q4-25 call). 2026 guide ~US$0.90/gal (~$0.10 above 2025).
print("\n== Gevo ND implied ==")
per25 = 52e6 / 69e6
print(f"2025 sold/gal ${per25:.3f} -> implied rate {50*(1-per25/AMT_2025):.1f}; mgmt-derived $0.80 -> {50*(1-0.80/AMT_2025):.1f}")
print(f"2026 guide $0.90/gal -> implied rate {50*(1-0.90/AMT_2026):.1f}; parity M @CAD200/300/400:",
      [round(1 + 0.90 / L_PER_GAL * FX / cfr_l(38, p), 2) for p in (200, 300, 400)])
