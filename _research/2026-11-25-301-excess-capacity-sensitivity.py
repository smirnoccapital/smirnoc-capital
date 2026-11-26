import sys, pathlib, numpy as np, pandas as pd
B = pathlib.Path(sys.argv[1])
L = pd.read_csv(B/"results_lines_headline.csv", dtype={"hts10": str})
res = pd.read_csv(B/"results_effective_rates.csv", index_col=0)
lvl = {"Vietnam":35,"India":25,"Singapore":20,"Bangladesh":18,"Cambodia":18,"Indonesia":18,"Malaysia":18,"Thailand":18}
L["r1"] = L.r0 + L.c*L.inc
# (a) 2025 annual weights
y = pd.read_csv(B/"census/hs10_2025_annual.csv", dtype={"I_COMMODITY": str})
y["hts10"] = y.I_COMMODITY.str.zfill(10); y = y.rename(columns={"CON_VAL_YR": "w25"})[["economy","hts10","w25"]]
M = L.merge(y, on=["economy","hts10"], how="left").fillna({"w25": 0})
out = {}
for e, g in M.groupby("economy"):
    tot25 = y[y.economy==e].w25.sum()
    r = {"w25_matched_%": 100*g.w25.sum()/tot25,
         "cur_eff_w25_%": (g.w25*g.r0).sum()/g.w25.sum(),
         "head_eff_w25_%": (g.w25*g.r1).sum()/g.w25.sum()}
    if e in lvl:  # stacked reading: full level on top of FL on covered lines
        r["head_eff_stacked_%"] = res.loc[e,"current_eff_%"] + (g.val*g.c).sum()/g.val.sum()*lvl[e]
    out[e] = r
s = pd.DataFrame(out).T.loc[res.index]
s.to_csv(B/"results_sensitivity.csv")
print(s.round(1).to_string())
