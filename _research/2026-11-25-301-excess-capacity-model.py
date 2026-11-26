"""Effective US tariff rates: current (post-Jul-24-2026) vs proposed Section 301 excess-capacity action.

Inputs (BUILD dir): census/hs10_*.csv, annex_codes.csv
Line-level logic
  current rate  r0 = CAL_DUT / CON_VAL observed in Aug+Sep 2026 (captures MFN/FTA, 2018 China 301,
                  forced-labor (FL) 301, Section 232, actual exemptions as entered)
  base rate     m  = CAL_DUT / CON_VAL in 2024 (pre-2025 = MFN/FTA applied rate; China incl. 2018 301)
  coverage      c  = share of the line subject to the new action (0 = exempt, 1 = covered)
  increment     d  = new duty added by the proposal on covered value
  proposed      r1 = r0 + c * d
"""
import sys, pathlib
import numpy as np, pandas as pd

B = pathlib.Path(sys.argv[1])
C = B / "census"

# ---------------------------------------------------------------- policy parameters
FL = {  # forced-labor 301 (July 24 2026): (rate, capped_incl_MFN)
    "China": (12.5, False), "Singapore": (12.5, False), "Vietnam": (12.5, False), "Thailand": (12.5, False),
    "India": (10, False), "Malaysia": (10, False), "Indonesia": (10, False), "Cambodia": (10, False),
    "Bangladesh": (10, False), "EU": (10, True), "Taiwan": (10, True), "Japan": (12.5, True),
    "Korea": (12.5, True), "Switzerland": (12.5, True),
}
# proposed excess-capacity (EC) levels: (level, net_of_MFN). Level is the TOTAL of FL + EC add-on
# (net_of_MFN=True: all-in incl. MFN). China handled separately.
SCEN = {
    "headline": {"Vietnam": (35, False), "India": (25, False), "Singapore": (20, False),
                 "Bangladesh": (18, False), "Cambodia": (18, False), "Indonesia": (18, False),
                 "Malaysia": (18, False), "Thailand": (18, False), "EU": (15, True), "Taiwan": (15, True),
                 "Japan": (15, True), "Korea": (15, True), "Switzerland": (15, True), "China": (20, "cn")},
    "deal": {"Vietnam": (20, False), "India": (17, False), "Singapore": (10, False)},
    "unsatisfactory": {"Bangladesh": (20, False), "Cambodia": (25, False), "Indonesia": (25, False),
                       "Malaysia": (25, False), "Thailand": (25, False), "EU": (20, True),
                       "Japan": (20, True), "Korea": (25, True), "Switzerland": (20, True),
                       "Taiwan": (25, False), "China": (40, "cn_all")},
}

# Section 232 coverage by HTS prefix (approximation; derivative steel/alu outside ch72/73/76 not flagged)
S232 = (
    [f"72{h:02d}" for h in range(6, 30)] + ["73"] + ["76"] +                      # steel, aluminum
    ["7403", "7405", "7406", "7407", "7408", "7409", "7410", "7411", "7412", "7413",
     "7415", "7418", "7419"] +                                                  # copper semis/derivatives
    ["8703", "870421", "870431", "8706", "8707", "8708"] +                     # light vehicles & parts
    ["840731", "840732", "840733", "840734", "840820", "840991", "840999",
     "8511", "851220", "851230", "851240", "854430", "401110", "401120",
     "700711", "700721", "940120"] +                                            # listed auto parts (subset)
    ["870120", "870422", "870423", "870432", "870442", "870443", "870452", "8702"] +  # MHDV, buses
    ["4403", "4406", "4407", "440911", "440919", "94016", "94017",
     "94034090", "94036080", "94039170"]                                        # wood/lumber/furniture/cabinets
)

def is232(h):
    return any(h.startswith(p) for p in S232)

# ---------------------------------------------------------------- data
def load(f, s):
    d = pd.read_csv(f, dtype={"I_COMMODITY": str, "CTY_CODE": str})
    d = d.rename(columns={f"CON_VAL_{s}": "val", f"DUT_VAL_{s}": "dval", f"CAL_DUT_{s}": "duty"})
    d["hts10"] = d.I_COMMODITY.str.zfill(10)
    return d[["economy", "hts10", "val", "dval", "duty"]].astype({"val": float, "duty": float, "dval": float})

cur = pd.concat([load(C / f"hs10_2026-{m:02d}.csv", "MO") for m in (8, 9)])
cur = cur.groupby(["economy", "hts10"], as_index=False).sum()
y24 = load(C / "hs10_2024_annual.csv", "YR")
y25 = load(C / "hs10_2025_annual.csv", "YR")
d = cur.merge(y24[["economy", "hts10", "val", "duty"]].rename(columns={"val": "v24", "duty": "d24"}),
              on=["economy", "hts10"], how="left")
d = d[d.val > 0].copy()
d["r0"] = 100 * d.duty / d.val
d["m"] = np.where(d.v24 > 0, 100 * d.d24 / d.v24, np.nan)
d["hts8"] = d.hts10.str[:4] + "." + d.hts10.str[4:6] + "." + d.hts10.str[6:8]
d["s232"] = d.hts10.map(is232)

# ---------------------------------------------------------------- annex classification
ax = pd.read_csv(B / "annex_codes.csv", dtype=str).fillna("")
def annex_map(econ):
    a = ax[ax.economy == econ]
    full = set(a[(a.scope == "") & (a.annex != "B")].hts8)
    part = set(a[a.scope.isin(["Aircraft", "Pharma", "Ex"])].hts8)
    annexB = set(a[a.annex == "B"].hts8)
    return full, part, annexB

def fl_paid(row, econ):
    """Estimated FL 301 add-on actually paid on the line (pp), from observed vs base."""
    rate, capped = FL[econ]
    if np.isnan(row.m):
        return np.nan
    return row.r0 - row.m

out = []
for econ, g in d.groupby("economy"):
    full, part, annexB = annex_map(econ)
    g = g.copy()
    g["annex_full"] = g.hts8.isin(full)
    g["annex_part"] = g.hts8.isin(part) & ~g.annex_full
    g["annexB"] = g.hts8.isin(annexB)
    rate, capped = FL[econ]
    mm = g.m.fillna(0.0)
    # FL expected if line covered by FL
    fl_exp = np.where(capped, np.maximum(rate - mm, 0), rate)
    excess = g.r0 - g.m
    # empirical FL-paying share for partial-scope lines (aircraft/pharma/ex); default 0.5 if undetectable
    emp = np.clip(excess / np.where(fl_exp > 1, fl_exp, np.nan), 0, 1)
    g["c_part"] = np.where(np.isfinite(emp), emp, 0.5)
    g["fl_exp"] = fl_exp
    g["excess"] = excess
    # ---- coverage share actually used (non-China): empirical where FL payment is detectable
    detect = g.m.notna().values & (fl_exp > 1)
    ch98 = g.hts10.str[:2].isin(["98", "99"]).values
    list_c = np.where(g.annex_full | g.s232, 0.0, np.where(g.annex_part, 0.5, 1.0))
    emp_c = np.where(excess > fl_exp + 5, 0.5,            # 232 derivative: metal share exempt
                     np.clip(excess / np.where(fl_exp > 1, fl_exp, 1), 0, 1))
    c_emp = np.where(ch98 | g.annex_full.values | g.s232.values, 0.0,
                     np.where(detect, emp_c, list_c))
    if capped:
        # paying above the FL all-in cap cannot be FL: it is a Section 232 line.
        # ~15% all-in = 232 deal rate (fully exempt); anything else = mixed derivative (half)
        over = g.r0.values - np.maximum(mm.values, rate)
        is232obs = g.m.notna().values & (over > 1.5)
        c_emp = np.where(is232obs, np.where((g.r0.values >= 14) & (g.r0.values <= 16), 0.0,
                                            np.minimum(c_emp, 0.5)), c_emp)
    g["c_emp"] = c_emp
    g["ch98"] = ch98
    # China: list-based, plus Ch.98/99 and lines visibly exempt from FL (e.g. Nairobi Protocol) excluded
    g["cn_exempt"] = ch98 | (detect & (excess < 1.5) & ~g.annex_full.values & ~g.s232.values
                             & ~g.annex_part.values)
    out.append(g)
d = pd.concat(out)

def increment(g, econ, spec):
    """pp added by the EC action on each line, and coverage share c."""
    level, mode = spec
    rate, capped = FL[econ]
    m = g.m.fillna(0.0).clip(lower=0)
    if mode == "cn":                          # China headline
        d_cov = level - rate                 # 20 net of FL 12.5 -> +7.5 on FL-paying lines
        inc = np.select(
            [g.cn_exempt, g.annexB, g.annex_full, g.s232, g.annex_part],
            [0.0, 0.0, 10.0, float(level), g.c_part * d_cov + (1 - g.c_part) * 10.0],
            default=d_cov)
        return inc, np.where(inc > 0, 1.0, 0.0)
    if mode == "cn_all":                      # China alternative: 40 net of FL on all goods
        fl_on = np.where(g.annex_full | g.s232 | g.annexB, 0.0,
                         np.where(g.annex_part, g.c_part * rate, rate))
        inc = np.where(g.cn_exempt, 0.0, level - fl_on)
        return inc, np.ones(len(g))
    c = g.c_emp.values
    if mode is True:                          # all-in level incl. MFN
        cur_lvl = np.maximum(m, rate) if capped else m + rate
        inc = np.maximum(np.maximum(m, level) - cur_lvl, 0)
    else:                                     # level net of existing 301 (above MFN)
        fl_now = np.maximum(rate - m, 0) if capped else rate
        inc = np.maximum(level - fl_now, 0)
    return inc * (c > 0) , c

rows = []
lines = []
for econ, g in d.groupby("economy"):
    V = g.val.sum()
    rec = {"economy": econ, "imports_AugSep26_$bn": V / 1e9, "current_eff_%": (g.duty.sum() / V) * 100}
    # coverage shares
    rec["share_232_%"] = 100 * g.val[g.s232].sum() / V
    rec["share_annex_full_%"] = 100 * g.val[g.annex_full & ~g.s232].sum() / V
    rec["share_annex_partial_%"] = 100 * g.val[g.annex_part & ~g.s232].sum() / V
    for sc, specs in SCEN.items():
        if econ not in specs:
            continue
        inc, c = increment(g, econ, specs[econ])
        add = (g.val * c * inc).sum() / V
        rec[f"{sc}_eff_%"] = rec["current_eff_%"] + add
        rec[f"{sc}_add_pp"] = add
        if sc == "headline":
            rec["share_covered_%"] = 100 * (g.val * c).sum() / V
            gg = g.assign(inc=inc, c=c)
            lines.append(gg)
    rows.append(rec)

res = pd.DataFrame(rows).set_index("economy")
order = ["China", "EU", "Japan", "Korea", "Taiwan", "Switzerland", "Singapore", "India", "Vietnam",
         "Thailand", "Malaysia", "Indonesia", "Cambodia", "Bangladesh"]
res = res.loc[[o for o in order if o in res.index]]
res.to_csv(B / "results_effective_rates.csv")
pd.concat(lines).to_csv(B / "results_lines_headline.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
print(res.round(1).to_string())
