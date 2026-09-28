"""
CFR credit multiplier needed to equalize US 45Z value per litre (CAD).
Rev. 2 (2026-09-28): adds 2026 inflation adjustment ($1.09), IRFA-based Iowa plant
CI conversion (g/MJ -> kg/mmBtu, ILUC removed), and a CAD 200/t credit-price case.

Parity logic
  A US plant selling into Canada earns 45Z PLUS ordinary CFR credits (multiplier 1.0).
  A Canadian plant earns CFR credits x M and no 45Z.
  (M - 1) * CFR_value_per_litre = 45Z_value_per_litre (CAD)
  M = 1 + 45Z_CAD_per_L / CFR_value_per_L

CFR credits per litre = (CI_ref - CI_fuel) [g/MJ] * energy density [MJ/L] * 1e-6 [t/g]
  (Clean Fuel Regulations credit formula CIdiff x (Q x D) x 10^-6; Schedule 2 densities)
45Z per gallon = applicable amount * (50 - rate)/50, rate in kg CO2e/mmBtu.
  2026 applicable amount with prevailing wage/apprenticeship = $1.00 x 1.0929 = $1.09
  (IRS Notice 2026-41).
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---- Inputs -------------------------------------------------------------
L_PER_GAL = 3.785411784
FX = 1.414                  # CAD per USD, 2026-09-24
CI_REF = 80.1               # g/MJ, ECCC discussion paper
ED = {"ethanol": 23.419e-6, "rd": 34.921e-6, "bd": 35.183e-6}
PRICE_ECCC = 300.0
AMOUNT_2026 = 1.09          # $/gal, 45Z alternative amount, 2026 (1.00 x 1.0929, rounded)
MJ_PER_MMBTU = 1055.056
G_MJ_TO_KG_MMBTU = MJ_PER_MMBTU / 1000.0     # 1.05506

def cfr_value(ci, fuel, price):
    return (CI_REF - ci) * ED[fuel] * price

def usd_gal_45z(rate, amount=AMOUNT_2026):
    return max(0.0, amount * (50 - rate) / 50)

def cad_l_45z(rate, amount=AMOUNT_2026):
    return usd_gal_45z(rate, amount) / L_PER_GAL * FX

def multiplier(rate, fuel, ci_can, price, amount=AMOUNT_2026):
    return 1 + cad_l_45z(rate, amount) / cfr_value(ci_can, fuel, price)

# ---- 0. Iowa plant CI from the IRFA (Feb 2023) study --------------------
print("== Iowa plant CI (IRFA Comparative Economics, Phase 1, Feb 2023) ==")
LUC_GREET3 = 7.382          # g/MJ, GREET 3.0 default LUC used in the study
LUC_CA = LUC_GREET3 + 12.62 # g/MJ, CA-GREET LUC (study: 12.62 higher)
print(f"LUC: GREET3 {LUC_GREET3} g/MJ = {LUC_GREET3*G_MJ_TO_KG_MMBTU:.1f} kg/mmBtu; CA-GREET {LUC_CA:.1f} g/MJ")
rows = [
    ("Iowa avg, CA-CI as published (lowest corn-starch score)", 68.25, LUC_CA),
    ("Iowa avg, CA-CI adjusted to GREET3 LUC", 55.83, LUC_GREET3),
    ("National avg, GREET 3.0 default (Argonne)", 55.333, LUC_GREET3),
    ("Iowa best published CA-CI (range low end 59)", 59.0, LUC_CA),
    ("Iowa worst published CA-CI (range high end 82)", 82.0, LUC_CA),
]
for name, ci, luc in rows:
    ex = ci - luc
    kg = ex * G_MJ_TO_KG_MMBTU
    print(f"{name}: {ci} g/MJ -> ex-LUC {ex:.2f} g/MJ = {kg:.1f} kg/mmBtu -> 45Z ${usd_gal_45z(kg):.3f}/gal")
print("Score with CCS (IRFA: ~30-point cut) from 51:", round(51 - 30, 1), "->", f"${usd_gal_45z(21):.2f}/gal")
print("Old-basis check: 55.83 g/MJ incl. LUC = %.1f kg/mmBtu" % (55.83 * G_MJ_TO_KG_MMBTU))

# ---- 1. Back-test ECCC ---------------------------------------------------
print("\n== ECCC back-test (CAD 300/t, ref CI 80.1) ==")
for fuel, ci, us_c, eccc_m in [("ethanol", 38, 0.05, 1.14), ("rd", 30, 0.23, 1.40)]:
    cv = cfr_value(ci, fuel, PRICE_ECCC)
    print(f"{fuel}: CFR value {cv*100:.1f} c/L; ECCC US incentive {us_c*100:.0f} c/L -> M = {1+us_c/cv:.3f} "
          f"(ECCC {eccc_m}); incentive implied by ECCC M = {(eccc_m-1)*cv*100:.1f} c/L")
for fuel, us_c in [("ethanol", 0.05), ("rd", 0.23)]:
    usd_gal = us_c / FX * L_PER_GAL
    print(f"{fuel}: {us_c*100:.0f} c CAD/L = US${usd_gal:.3f}/gal = 45Z rate of {50 - usd_gal*50/AMOUNT_2026:.1f} kg/mmBtu (at $1.09 amount)")

# CFR revenue per million litres (for the explainer)
print("\nCFR credits per litre, ethanol CI 38:", round((CI_REF-38)*ED['ethanol'], 6), "t/L; per million litres:",
      round((CI_REF-38)*ED['ethanol']*1e6), "credits; value at CAD 300: $%.0f" % ((CI_REF-38)*ED['ethanol']*1e6*300))

# ---- 2. Ethanol grid ------------------------------------------------------
prices = [200, 300, 350, 430]
eth_rates = [51, 48, 45, 43, 41, 40, 35, 30, 25, 21, 15]
print("\n== ETHANOL: M needed (Canadian plant CFR CI 38) ==")
print("45Z rate | US$/gal | CAD c/L | " + " | ".join(f"CAD{p}" for p in prices))
for c in eth_rates:
    print(f"{c:8} | {usd_gal_45z(c):7.3f} | {cad_l_45z(c)*100:7.1f} | " +
          " | ".join(f"{multiplier(c,'ethanol',38,p):5.2f}" for p in prices))

print("\n== ETHANOL sensitivity to Canadian CFR CI (45Z rate 45 and 30), prices 200/300/430 ==")
for r in (45, 30):
    for ci_can in [30, 34, 38, 42, 46, 50]:
        print(r, ci_can, [round(multiplier(r, "ethanol", ci_can, p), 2) for p in (200, 300, 430)])

# ---- 3. RD / BD ---------------------------------------------------------
print("\n== RD (soy, rate 26.36) / BD (soy, rate 20.23); Canadian CFR CI 30 ==")
for label, fuel, r, asa in [("RD", "rd", 26.36, 0.55), ("BD", "bd", 20.23, 0.66)]:
    print(label, f"formula ${usd_gal_45z(r):.3f}/gal ({cad_l_45z(r)*100:.1f} c CAD/L) vs ASA ${asa}:",
          {p: round(multiplier(r, fuel, 30, p), 2) for p in prices})
    amt_asa = asa * 50 / (50 - r)
    print("   ASA-implied applicable amount:", round(amt_asa, 3),
          {p: round(multiplier(r, fuel, 30, p, amt_asa), 2) for p in prices})
print("\nRD sensitivity to Canadian CFR CI:")
for ci_can in [20, 25, 30, 35, 40]:
    print(ci_can, {p: round(multiplier(26.36, "rd", ci_can, p), 2) for p in prices})
print("BD sensitivity to Canadian CFR CI:")
for ci_can in [20, 25, 30, 35, 40]:
    print(ci_can, {p: round(multiplier(20.23, "bd", ci_can, p), 2) for p in prices})

# ---- 4. Chart -------------------------------------------------------------
INK, MUTED, GRID = "#1f2933", "#6b7280", "#e5e7eb"
C_ETH, C_RD = "#1b6ca8", "#c2571a"
fig, ax = plt.subplots(figsize=(8.2, 4.8), dpi=200)
x = np.linspace(0.0, 0.75, 200)
def m_from_usd_gal(u, fuel, ci_can, price):
    return 1 + (u / L_PER_GAL * FX) / cfr_value(ci_can, fuel, price)
ax.plot(x, m_from_usd_gal(x, "ethanol", 38, 300), color=C_ETH, lw=2)
ax.plot(x, m_from_usd_gal(x, "rd", 30, 300), color=C_RD, lw=2)
ax.axhline(1.14, color=C_ETH, lw=1, ls=(0, (4, 3)))
ax.axhline(1.40, color=C_RD, lw=1, ls=(0, (4, 3)))
ax.text(0.752, 1.14, "ECCC ethanol 1.14", color=INK, fontsize=8, va="center")
ax.text(0.752, 1.40, "ECCC diesel 1.40", color=INK, fontsize=8, va="center")
e1, e2, r1 = usd_gal_45z(45), usd_gal_45z(30), usd_gal_45z(26.36)
for u, fuel, ci, col in [(e1, "ethanol", 38, C_ETH), (e2, "ethanol", 38, C_ETH), (r1, "rd", 30, C_RD), (0, "ethanol", 38, C_ETH)]:
    ax.plot([u], [m_from_usd_gal(u, fuel, ci, 300)], "o", ms=8, color=col, mec="white", mew=2)
def note(txt, pt, xy_text):
    ax.annotate(txt, pt, xytext=xy_text, fontsize=8.5, color=INK,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
note("Iowa-average plant (~51):\n$0.00, M = 1.00", (0, 1.0), (0.16, 0.99))
note("Improved plant (45):\n$%.2f, M = %.2f" % (e1, m_from_usd_gal(e1, "ethanol", 38, 300)),
     (e1, m_from_usd_gal(e1, "ethanol", 38, 300)), (0.16, 1.42))
note("Deep-cut plant (30):\n$%.2f, M = %.2f" % (e2, m_from_usd_gal(e2, "ethanol", 38, 300)),
     (e2, m_from_usd_gal(e2, "ethanol", 38, 300)), (0.16, 1.72))
note("Soy RD (26.36):\n$%.2f, M = %.2f" % (r1, m_from_usd_gal(r1, "rd", 30, 300)),
     (r1, m_from_usd_gal(r1, "rd", 30, 300)), (0.56, 1.55))
ax.text(0.30, 1.82, "Ethanol (CFR CI 38)", color=C_ETH, fontsize=9, fontweight="bold")
ax.text(0.45, 1.22, "Renewable diesel (CFR CI 30)", color=C_RD, fontsize=9, fontweight="bold")
ax.set_xlim(0.0, 0.75); ax.set_ylim(0.95, 2.0)
ax.set_xlabel("US 45Z credit value, US\$ per gallon (2026 amount \$1.09)", color=MUTED, fontsize=9)
ax.set_ylabel("Canadian credit multiplier needed for parity", color=MUTED, fontsize=9)
ax.set_title("What multiplier equalizes 45Z? (CFR credit at CAD 300/t, USD/CAD 1.414)",
             loc="left", fontsize=10.5, color=INK, fontweight="bold")
ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True)
for s in ("top", "right"): ax.spines[s].set_visible(False)
for s in ("left", "bottom"): ax.spines[s].set_color(GRID)
ax.tick_params(colors=MUTED, labelsize=8.5)
fig.subplots_adjust(right=0.80)
fig.savefig("cfr-multiplier-45z-parity.png", facecolor="white")
print("chart saved")
