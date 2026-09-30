"""
Implied 45Z scores and per-gallon values from public company disclosures (ethanol).
Universe: SEC EDGAR full-text search for "45Z" (10-K/10-Q/8-K, 2025-01 to 2026-09) restricted to ethanol
producers: Green Plains, REX American, Highwater Ethanol, Alto Ingredients, Gevo, Andersons, Aemetis,
Valero, ADM. Other hits (Marathon, HF Sinclair, CVR, Calumet, FutureFuel, Clean Energy, OPAL, Darling,
XCF, Blue Biofuels) are renewable diesel / biodiesel / RNG / refiners and are excluded.

implied rate (kg CO2e/mmBtu) = 50 * (1 - per_gal / amount);  g/MJ = rate / 1.055056
amount = $1.06 for fuel sold in 2025 (1.00 x 1.0611), $1.09 for 2026 (1.00 x 1.0929).
Caveats encoded in the `basis` column: net vs gross of discounts, produced vs sold gallons, estimated gallons.
Run from SC Project root: python _research/2026-09-30-45z-public-disclosures.py
"""
import csv

K = 1.055056
A25, A26 = 1.06, 1.09

# company, period, $M credit (or None), gallons M (or None), stated $/gal (or None), amount, basis/notes, ccs (capture plant in figure)
rows = [
    ("Valero", "Q1 2026 (10 plants)", None, None, 0.10, A26, "Stated on Q1 call: $0.10/gal booked on 10 plants 'using the original definition of qualified sales'", False),
    ("Valero", "H1 2026 (10 plants)", None, None, 0.14, A26, "Stated on Q2-26 call ('production tax credit we are capturing is $0.14 YTD'); net/gross not stated; H1 total reported ~$119M", False),
    ("Valero", "FY2026 projection", None, None, 0.17, A26, "Stated on Q2-26 call ('probably $0.17 for the full year')", False),
    ("Valero", "2027-2029 projection", None, None, 0.19, A26, "Stated on Q2-26 call; later-year amounts are inflation-indexed above $1.09, so implied score is slightly overstated", False),
    ("Andersons", "Q2 2026 (4 plants)", 24.229, 181.066, None, A26, "10-Q other income: clean fuel production credits $24,229K; gallons = ethanol sold (10-Q), may include third-party gallons", False),
    ("Andersons", "H1 2026 (4 plants)", 50.390, 354.037, None, A26, "10-Q: $50,390K; 354,037K gal sold", False),
    ("REX American", "Q2 FY2026 (May-Jul 2026)", 18.4, 70.6, None, A26, "Release: $18.4M to gross profit; consolidated gallons sold; credit claimed mainly at One Earth, so per-gallon is a lower bound", False),
    ("REX American", "H1 FY2026 (Feb-Jul 2026)", 26.0, 141.7, None, A26, "$26.0M YTD (Q2 call); 141.7M gal sold (release)", False),
    ("Highwater Ethanol", "9 mo. to Jul 31 2026, gross", 13.1, 70.0 * 9 / 12, None, A26, "Gross $13.1M before broker fees/discounts; gallons ESTIMATED from ~70M/yr rate (10-Q gives no gallons)", False),
    ("Highwater Ethanol", "9 mo. to Jul 31 2026, net", 11.7, 70.0 * 9 / 12, None, A26, "Net $11.7M after $1.4M of fees, discounts, energy credits, compliance payments; gallons estimated", False),
    ("Highwater Ethanol", "Calendar 2025, credits sold", 14.307388, 70.2, None, A25, "10-Q: sold $14,307,388 'worth' of 2025 credits May 29 2026; gallons ESTIMATED at permit rate 70.2M", False),
    ("Highwater Ethanol", "FY to Oct 31 2025 (10 mo. of credit)", 10.4, 70.2 * 10 / 12, None, A25, "Recognized $10.4M; credit only from Jan 1 2025, so 10 of 12 months of the 70.2M/yr rate; 2025 score includes ILUC", False),
    ("Highwater Ethanol", "FY to Oct 31 2025 (12 mo. of gallons)", 10.4, 70.2, None, A25, "Same credit over full-year gallons (lower bound on $/gal)", False),
    ("Alto Ingredients", "2026 stated", None, 90.0, 0.20, A26, "Stated: ~90M qualifying gal (Columbia + Pekin dry mills) 'at $0.20 per gallon'", False),
    ("Alto Ingredients", "2026 guidance, net", 15.0, 90.0, None, A26, "Q1 call: ~$15M net proceeds after all monetization costs on ~90M gal", False),
    ("Aemetis (Keyes, CA)", "Q1 2026", 2.6, 13.7, None, A26, "California Ethanol segment only", False),
    ("Aemetis (Keyes, CA)", "Q2 2026", 6.5, 15.5, None, A26, "California Ethanol segment; MVR efficiency project (~15-pt CI cut) targeted for Q2, possible catch-up", False),
    ("Green Plains", "H1 2026 (8 plants, 3 with CCS), 10-Q", 134.0, 334.896, None, A26, "10-Q: credits net of discounts recorded as cost-of-goods reduction; gallons = produced", True),
    ("Green Plains", "H1 2026 (8 plants, 3 with CCS), release", 113.9, 334.896, None, A26, "Earnings release: net of discounts, other costs and SG&A; gallons = produced", True),
    ("Gevo (Richardton ND, CCS)", "FY2025", 52.0, 69.0, None, A25, "$52M of 2025 credits sold; ~69M gal produced (Q4-25 call); CI described as 'low double digits'", True),
    ("Gevo (Richardton ND, CCS)", "FY2026 guidance", None, 67.0, 0.90, A26, "Mgmt: ~$0.90/gal in 2026, ~$0.10 above 2025 (per Q4-25 call)", True),
]

out = []
for co, per, usd_m, gal_m, pg, amt, basis, ccs in rows:
    per_gal = pg if pg is not None else usd_m / gal_m
    rate = 50 * (1 - per_gal / amt)
    out.append(dict(company=co, period=per, credit_usd_m=usd_m, gallons_m=round(gal_m, 1) if gal_m else None,
                    per_gal=round(per_gal, 3), amount=amt, implied_rate=round(rate, 1),
                    implied_g_per_mj=round(rate / K, 1), ccs=ccs, basis=basis))

print(f"{'company':28} {'period':42} {'$/gal':>6} {'rate':>6} {'g/MJ':>6}")
for r in out:
    print(f"{r['company']:28} {r['period']:42} {r['per_gal']:6.3f} {r['implied_rate']:6.1f} {r['implied_g_per_mj']:6.1f}")

with open("_research/2026-09-30-45z-public-disclosures.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
    w.writeheader(); w.writerows(out)

# Non-CCS cross-check against the CFR-list proxy (mean 41.8 kg/mmBtu, see 2026-09-30-cfr-ci-list-45z-proxy.py)
pick = [("Valero", "H1 2026 (10 plants)"), ("Andersons", "H1 2026 (4 plants)"), ("REX American", "H1 FY2026 (Feb-Jul 2026)"),
        ("Highwater Ethanol", "9 mo. to Jul 31 2026, net"), ("Alto Ingredients", "2026 stated"), ("Aemetis (Keyes, CA)", "Q1 2026")]
vals = [r["implied_rate"] for r in out if (r["company"], r["period"]) in pick]
print("\nNon-CCS disclosers (one row each):", vals, "mean", round(sum(vals) / len(vals), 1), "vs CFR-list proxy mean 41.8")
# Valero's own plants in the CFR list (VRF): approved CI 38-44 g/MJ
vrf = [38, 40, 42, 42, 42, 42, 43, 44]
print("VRF plants in CFR list: mean CI", sum(vrf) / len(vrf), "g/MJ ->", round(sum(vrf) / len(vrf) * K, 1), "kg/mmBtu -> $%.3f/gal" % (A26 * (50 - sum(vrf) / len(vrf) * K) / 50))
