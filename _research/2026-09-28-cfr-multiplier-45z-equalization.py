"""
CFR credit multiplier needed to equalize US 45Z value (per litre, CAD).

Equalization logic
  A US plant earns 45Z (US$ per gallon) PLUS the same CFR credits a Canadian plant
  earns per litre (multiplier 1.0) when it sells into Canada.
  A Canadian plant earns CFR credits x M and no 45Z.
  Parity:  (M - 1) * CFR_value_per_litre = 45Z_value_per_litre (CAD)
           M = 1 + 45Z_CAD_per_L / CFR_value_per_L

CFR credits per litre = (CI_ref - CI_fuel) [g/MJ] * energy density [MJ/L] * 1e-6 [t/g]
  (Clean Fuel Regulations, credit formula CIdiff x (Q x D) x 10^-6; Schedule 2 energy densities)

45Z per gallon = $1.00 * (50 - CI45Z) / 50   (PWA-compliant rate, CI in kg CO2e/mmBtu)
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---- Inputs -------------------------------------------------------------
L_PER_GAL = 3.785411784
FX = 1.414                 # CAD per USD, 2026-09-24 (Fed H.10 / MTFX series)
CI_REF = 80.1              # g/MJ, ECCC discussion paper assumption (both fuels)
ED = {"ethanol": 23.419e-6, "rd": 34.921e-6, "bd": 35.183e-6}  # MJ/L * 1e-6 -> t per (g/MJ) per L
PRICE_ECCC = 300.0         # CAD/t, ECCC 2030 assumption

def cfr_value(ci, fuel, price):
    """CAD per litre of CFR credit value."""
    return (CI_REF - ci) * ED[fuel] * price

def val45z_cad_per_l(ci45z):
    usd_gal = max(0.0, 1.00 * (50 - ci45z) / 50)
    return usd_gal / L_PER_GAL * FX

def multiplier(ci45z, fuel, ci_can, price):
    return 1 + val45z_cad_per_l(ci45z) / cfr_value(ci_can, fuel, price)

# ---- 1. Back-test ECCC's published multipliers ---------------------------
print("== ECCC back-test (CAD 300/t, ref CI 80.1) ==")
for fuel, ci, us_c, eccc_m in [("ethanol", 38, 0.05, 1.14), ("rd", 30, 0.23, 1.40)]:
    cv = cfr_value(ci, fuel, PRICE_ECCC)
    print(f"{fuel}: CFR value {cv*100:.1f} c/L at CI {ci}; ECCC US incentive {us_c*100:.0f} c/L "
          f"-> implied M = {1+us_c/cv:.3f} (ECCC {eccc_m}); "
          f"incentive implied by ECCC M = {(eccc_m-1)*cv*100:.1f} c/L")
# 45Z CI that ECCC's 5c / 23c CAD per L would correspond to
for fuel, us_c in [("ethanol", 0.05), ("rd", 0.23)]:
    usd_gal = us_c / FX * L_PER_GAL
    print(f"{fuel}: {us_c*100:.0f} c CAD/L = US${usd_gal:.3f}/gal = 45Z CI of {50-usd_gal*50:.1f} kg/mmBtu")

# ---- 2. Ethanol: Iowa plant 45Z CI scenarios -----------------------------
eth_ci45 = [45, 40, 35, 30, 25, 20, 15]
prices = [300, 350, 430]
print("\n== ETHANOL: multiplier needed (Canadian plant CFR CI 38) ==")
print("45Z CI | US$/gal | CAD c/L | " + " | ".join(f"CAD{p}" for p in prices))
for c in eth_ci45:
    row = [multiplier(c, "ethanol", 38, p) for p in prices]
    print(f"{c:6} | {1.0*(50-c)/50:7.2f} | {val45z_cad_per_l(c)*100:7.1f} | " + " | ".join(f"{m:5.2f}" for m in row))

print("\n== ETHANOL: 45Z CI 30 ($0.40/gal), sensitivity to Canadian plant CFR CI, price CAD 300/350 ==")
for ci_can in [30, 34, 38, 42, 46, 50]:
    print(ci_can, [round(multiplier(30, "ethanol", ci_can, p), 2) for p in (300, 350)])

# ---- 3. Renewable diesel & biodiesel ------------------------------------
print("\n== RD (soy, 45Z CI 26.36 = $0.55) / BD (soy, 45Z CI 20.23 = $0.66); Canadian CFR CI 30 ==")
for label, fuel, c45 in [("RD", "rd", 26.36), ("BD", "bd", 20.23)]:
    print(label, f"45Z ${(50-c45)/50:.3f}/gal = {val45z_cad_per_l(c45)*100:.1f} c CAD/L;",
          {p: round(multiplier(c45, fuel, 30, p), 2) for p in prices})
print("\nRD sensitivity to Canadian CFR CI (45Z CI 26.36):")
for ci_can in [20, 25, 30, 35, 40]:
    print(ci_can, {p: round(multiplier(26.36, "rd", ci_can, p), 2) for p in prices})
print("\nBD sensitivity to Canadian CFR CI (45Z CI 20.23):")
for ci_can in [20, 25, 30, 35, 40]:
    print(ci_can, {p: round(multiplier(20.23, "bd", ci_can, p), 2) for p in prices})
print("\nAlt RD/BD 45Z per gallon (older-model soy values 0.11 / 0.33):")
for label, fuel, usd in [("RD old", "rd", 0.11), ("BD old", "bd", 0.33)]:
    c45 = 50 - usd * 50
    print(label, round(multiplier(c45, fuel, 30, 300), 2))

# ---- 4. Chart -------------------------------------------------------------
INK, MUTED, GRID = "#1f2933", "#6b7280", "#e5e7eb"
C_ETH, C_RD = "#1b6ca8", "#c2571a"
fig, ax = plt.subplots(figsize=(8.2, 4.8), dpi=200)
x = np.linspace(0.10, 0.75, 200)          # US$/gal 45Z value
def m_from_usd_gal(u, fuel, ci_can, price):
    return 1 + (u / L_PER_GAL * FX) / cfr_value(ci_can, fuel, price)
ax.plot(x, m_from_usd_gal(x, "ethanol", 38, 300), color=C_ETH, lw=2)
ax.plot(x, m_from_usd_gal(x, "rd", 30, 300), color=C_RD, lw=2)
ax.axhline(1.14, color=C_ETH, lw=1, ls=(0, (4, 3)))
ax.axhline(1.40, color=C_RD, lw=1, ls=(0, (4, 3)))
ax.text(0.752, 1.14, "ECCC ethanol 1.14", color=INK, fontsize=8, va="center")
ax.text(0.752, 1.40, "ECCC diesel 1.40", color=INK, fontsize=8, va="center")
# scenario markers
pts = [("Ethanol\n$0.40 (CI 30)", 0.40, m_from_usd_gal(0.40, "ethanol", 38, 300), C_ETH),
       ("Soy RD\n$0.55", 0.55, m_from_usd_gal(0.55, "rd", 30, 300), C_RD)]
for lab, u, m, col in pts:
    ax.plot([u], [m], "o", ms=8, color=col, mec="white", mew=2)
ax.annotate("Ethanol at $0.40/gal:\n~%.2f" % m_from_usd_gal(0.40, "ethanol", 38, 300), (0.40, m_from_usd_gal(0.40, "ethanol", 38, 300)),
            xytext=(0.14, 1.52), fontsize=8.5, color=INK, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
ax.annotate("Soy RD at $0.55/gal:\n~%.2f" % m_from_usd_gal(0.55, "rd", 30, 300), (0.55, m_from_usd_gal(0.55, "rd", 30, 300)),
            xytext=(0.58, 1.17), fontsize=8.5, color=INK, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
ax.text(0.11, 1.78, "Ethanol (CFR CI 38)", color=C_ETH, fontsize=9, fontweight="bold")
ax.text(0.43, 1.25, "Renewable diesel (CFR CI 30)", color=C_RD, fontsize=9, fontweight="bold")
ax.set_xlim(0.10, 0.75); ax.set_ylim(1.0, 2.0)
ax.set_xlabel("US 45Z credit value, US$ per gallon", color=MUTED, fontsize=9)
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
