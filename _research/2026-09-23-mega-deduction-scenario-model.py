import pandas as pd

# ---- Assumptions ----
SB_RATE = 0.122      # Ontario CCPC small business rate (9% fed + 3.2% ON), income <= $500k
GEN_RATE = 0.265     # Ontario CCPC general rate (15% fed + 11.5% ON), income > $500k
SB_LIMIT = 500_000
CCA_RATE = 0.20      # Class 8 declining balance rate
DISCOUNT = 0.06      # illustrative farm cost of capital / borrowing rate

def tax_on_income(ti):
    """Ontario CCPC active business income tax, blending SB + general rate."""
    if ti <= 0:
        return 0.0
    if ti <= SB_LIMIT:
        return ti * SB_RATE
    return SB_LIMIT * SB_RATE + (ti - SB_LIMIT) * GEN_RATE

def cca_year1(cost, regime):
    if regime == "old":       # half-year rule, no AII
        return cost * CCA_RATE * 0.5
    if regime == "aii":       # Budget 2025 re-up: 3x normal first-year (=1.5x full rate)
        return min(cost, cost * CCA_RATE * 0.5 * 3)
    if regime == "mega":      # Productivity Mega Deduction: 100% immediate
        return cost

def scenario_year1(label, pretax_income, equipment_cost):
    rows = []
    for regime in ["old", "aii", "mega"]:
        cca = cca_year1(equipment_cost, regime)
        taxable = pretax_income - cca
        loss = max(0, -taxable)
        taxable_after_loss = max(0, taxable)
        tax = tax_on_income(taxable_after_loss)
        avg_rate = tax / pretax_income if pretax_income else None
        rows.append({
            "farm": label, "regime": regime, "pretax_income": pretax_income,
            "equipment_cost": equipment_cost, "yr1_cca_claimed": cca,
            "taxable_income": taxable_after_loss, "non_capital_loss_created": loss,
            "tax_payable": tax, "avg_cash_tax_rate": avg_rate
        })
    return rows

results = []
# Farm A: steady investor, $180k pretax income, $60k equipment every year
results += scenario_year1("A: steady ($180k income, $60k/yr equip)", 180_000, 60_000)
# Farm B: lumpy mid-size investor, $180k pretax income, one $480k combine
results += scenario_year1("B: lumpy mid-size ($180k income, $480k combine)", 180_000, 480_000)
# Farm C: lumpy large investor, $650k pretax income, one $480k combine
results += scenario_year1("C: lumpy large ($650k income, $480k combine)", 650_000, 480_000)

df = pd.DataFrame(results)
pd.set_option("display.float_format", lambda x: f"{x:,.0f}")
print(df.to_string(index=False))
df.to_csv(r"C:\Users\ssharma\AppData\Local\Temp\claude\C--WINDOWS-system32\cbe00cad-6324-4941-9cfa-b788dc878deb\scratchpad\year1_scenarios.csv", index=False)

# ---- Multi-year NPV comparison: Farm A steady investor, AII vs Mega, 8-year horizon ----
def declining_balance_schedule(cost, first_year_claim, years, rate=CCA_RATE):
    ucc = cost - first_year_claim
    claims = [first_year_claim]
    for _ in range(years - 1):
        c = ucc * rate
        claims.append(c)
        ucc -= c
    return claims

years = 8
print("\n--- Farm A steady investor: $60k/yr equipment, cumulative CCA claimed, AII vs Mega ---")
# Each year's $60k purchase pool depreciates independently; sum across vintages per year
aii_pools = []
mega_pools = []
aii_by_year = [0.0]*years
mega_by_year = [0.0]*years
for purchase_year in range(years):
    aii_first = 60_000 * CCA_RATE * 0.5 * 3
    mega_first = 60_000
    aii_sched = declining_balance_schedule(60_000, aii_first, years - purchase_year)
    mega_sched = declining_balance_schedule(60_000, mega_first, years - purchase_year)
    for i, v in enumerate(aii_sched):
        aii_by_year[purchase_year + i] += v
    for i, v in enumerate(mega_sched):
        mega_by_year[purchase_year + i] += v

npv_aii = sum(v / (1+DISCOUNT)**t for t, v in enumerate(aii_by_year))
npv_mega = sum(v / (1+DISCOUNT)**t for t, v in enumerate(mega_by_year))
print("AII yearly CCA claims:", [round(v) for v in aii_by_year], "NPV of claims:", round(npv_aii))
print("Mega yearly CCA claims:", [round(v) for v in mega_by_year], "NPV of claims:", round(npv_mega))
print("Total nominal claimed over 8y (both regimes should sum to <= 480,000 total spend):",
      round(sum(aii_by_year)), round(sum(mega_by_year)))
tax_shield_npv_aii = npv_aii * SB_RATE
tax_shield_npv_mega = npv_mega * SB_RATE
print(f"PV of tax shield @ {SB_RATE:.1%}: AII = {tax_shield_npv_aii:,.0f}  Mega = {tax_shield_npv_mega:,.0f}  Diff = {tax_shield_npv_mega - tax_shield_npv_aii:,.0f}")

# ---- Farm B lumpy: loss carryback mechanics ----
print("\n--- Farm B lumpy mid-size: loss created under Mega, carryback value ---")
pretax = 180_000
cost = 480_000
mega_claim = cost
taxable = pretax - mega_claim
loss = -taxable
print(f"Pretax income {pretax:,}, Mega claim {mega_claim:,}, non-capital loss created: {loss:,}")
# carryback value: refund of tax paid in prior 3 years at SB rate, capped by loss and by prior taxes paid
prior_year_tax = tax_on_income(pretax)
carryback_years = 3
max_refund = min(loss, prior_year_tax * carryback_years)
print(f"Tax paid in a typical prior year (same income level): {prior_year_tax:,.0f}")
print(f"Max refund available via 3-yr carryback (loss-limited or tax-limited): {max_refund:,.0f}")

# AII in same year for Farm B (for comparison) - does it ever exceed income?
aii_claim_B = min(cost, cost*CCA_RATE*0.5*3)
print(f"AII year-1 claim on $480k combine: {aii_claim_B:,.0f} vs pretax income {pretax:,} -> creates loss? {aii_claim_B > pretax}")

# ---- Farm B: full 8-year cycle, AII vs Mega, including loss carryforward mechanics ----
print("\n--- Farm B lumpy mid-size: 8-year cycle total tax + NPV, AII vs Mega (with loss c/f) ---")
years = 8
pretax = 180_000
cost = 480_000

def run_farm_b(regime):
    first = cca_year1(cost, regime)
    sched = declining_balance_schedule(cost, first, years)
    loss_cf = 0.0
    taxes = []
    for yr, cca in enumerate(sched):
        taxable = pretax - cca - loss_cf
        if taxable < 0:
            loss_cf = -taxable
            taxable = 0
        else:
            loss_cf = 0
        tax = tax_on_income(taxable)
        taxes.append(tax)
    return sched, taxes, loss_cf

for regime in ["aii", "mega"]:
    sched, taxes, remaining_loss_cf = run_farm_b(regime)
    npv_tax = sum(t/(1+DISCOUNT)**yr for yr, t in enumerate(taxes))
    print(f"{regime.upper()}: CCA by year {[round(x) for x in sched]}")
    print(f"       tax by year   {[round(x) for x in taxes]}")
    print(f"       total nominal tax over 8y: {sum(taxes):,.0f}  NPV @ {DISCOUNT:.0%}: {npv_tax:,.0f}  remaining loss c/f at yr8 end: {remaining_loss_cf:,.0f}")

# Mega with immediate carryback election instead of carryforward (compare NPV)
print("\nMega w/ 3-yr carryback of the $300k loss (vs plain carryforward):")
loss = 300_000
refund = min(loss, tax_on_income(pretax) * 3)
print(f"Immediate refund (yr1, undiscounted): {refund:,.0f} -> PV (received yr1, no discount needed): {refund:,.0f}")
remaining_loss_after_cb = loss - refund
print(f"Remaining loss still carried forward after using carryback: {remaining_loss_after_cb:,.0f}")

# ---- Farm B: three strategies compared on NPV, apples-to-apples ----
print("\n--- Farm B: 3-way NPV comparison (AII / Mega+carryforward-only / Mega+carryback) ---")
def npv(cashflows):
    return sum(cf/(1+DISCOUNT)**t for t, cf in enumerate(cashflows))

# AII (from run_farm_b above)
sched_aii, taxes_aii, _ = run_farm_b("aii")
# Mega, carryforward only
sched_mega, taxes_mega_cf, _ = run_farm_b("mega")
# Mega, with yr-1 carryback of $65,880 against the $300k loss, remainder carried forward
sched_mega2 = sched_mega
loss_cf = 300_000 - 65_880  # after carryback used
taxes_mega_cb = [0 - 65_880]  # yr1: net cash tax effect = -refund
loss_running = loss_cf
for yr in range(1, years):
    taxable = pretax - 0 - loss_running
    if taxable < 0:
        loss_running = -taxable
        taxable = 0
    else:
        loss_running = 0
    taxes_mega_cb.append(tax_on_income(taxable))

print("AII        yearly net tax:", [round(x) for x in taxes_aii], " NPV:", round(npv(taxes_aii)))
print("Mega (c/f) yearly net tax:", [round(x) for x in taxes_mega_cf], " NPV:", round(npv(taxes_mega_cf)))
print("Mega (c/b) yearly net tax:", [round(x) for x in taxes_mega_cb], " NPV:", round(npv(taxes_mega_cb)))
