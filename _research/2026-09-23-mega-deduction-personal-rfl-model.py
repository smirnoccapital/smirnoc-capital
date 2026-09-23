import math

# 2026 combined federal + Ontario marginal rate ladder (taxtips.ca), regular income
BRACKETS = [
    (0,        53_891,  0.1905),
    (53_891,   58_523,  0.2315),
    (58_523,   94_907,  0.2965),
    (94_907,   107_785, 0.3148),
    (107_785,  111_814, 0.3389),
    (111_814,  117_045, 0.3791),
    (117_045,  150_000, 0.4341),
    (150_000,  181_440, 0.4497),
    (181_440,  220_000, 0.4826),
    (220_000,  258_482, 0.4982),
    (258_482,  math.inf,0.5353),
]

def personal_tax(income):
    if income <= 0:
        return 0.0
    tax = 0.0
    for lo, hi, rate in BRACKETS:
        if income > lo:
            tax += (min(income, hi) - lo) * rate
        else:
            break
    return tax

def marginal_rate(income):
    for lo, hi, rate in BRACKETS:
        if lo < income <= hi or (income > lo and hi == math.inf):
            return rate
    return BRACKETS[0][2]

CCA_RATE = 0.20
def cca_year1(cost, regime):
    if regime == "old":
        return cost * CCA_RATE * 0.5
    if regime == "aii":
        return min(cost, cost * CCA_RATE * 0.5 * 3)
    if regime == "mega":
        return cost

def scenario(label, pretax_income, equipment_cost):
    print(f"\n{label}  (pretax income {pretax_income:,})")
    for regime in ["old", "aii", "mega"]:
        cca = cca_year1(equipment_cost, regime)
        taxable = pretax_income - cca
        loss = max(0, -taxable)
        taxable_after = max(0, taxable)
        tax = personal_tax(taxable_after)
        rate = tax / pretax_income
        print(f"  {regime:5s}  CCA={cca:>10,.0f}  taxable={taxable_after:>10,.0f}  "
              f"loss={loss:>9,.0f}  tax={tax:>10,.0f}  avg rate={rate:6.1%}  "
              f"marginal rate before CCA={marginal_rate(pretax_income):5.1%}")

scenario("Farm A (unincorporated) - steady $60k/yr", 180_000, 60_000)
scenario("Farm B (unincorporated) - lumpy $480k combine", 180_000, 480_000)
scenario("Farm C (unincorporated) - large operator, lumpy $480k combine", 650_000, 480_000)

# sanity check: top marginal rate
print("\nCheck top marginal rate at 300k:", marginal_rate(300_000))
print("Check marginal rate at 180k:", marginal_rate(180_000))
print("Check marginal rate at 650k:", marginal_rate(650_000))

# Farm B loss carryback under personal tax (assume same 180k income & tax paid in prior 3 yrs)
print("\n--- Farm B (unincorporated) carryback mechanics ---")
prior_tax = personal_tax(180_000)
loss = 480_000 - 180_000  # since mega claim=480k fully offsets the 180k then creates loss beyond
print(f"Prior-year tax on 180,000 taxable income: {prior_tax:,.0f}")
print(f"Loss created by Mega claim: {loss:,.0f}")
refund = min(loss, prior_tax*3)
print(f"Max 3-yr carryback refund: {refund:,.0f}")

# ---- Multi-year: Farm A steady investor (unincorporated), 8-year NPV ----
DISCOUNT = 0.06
years = 8

def declining_balance_schedule(cost, first_year_claim, yrs, rate=CCA_RATE):
    ucc = cost - first_year_claim
    claims = [first_year_claim]
    for _ in range(yrs - 1):
        c = ucc * rate
        claims.append(c)
        ucc -= c
    return claims

def npv(cashflows):
    return sum(cf/(1+DISCOUNT)**t for t, cf in enumerate(cashflows))

print("\n--- Farm A (unincorporated), 8-yr CCA stream + tax + NPV, AII vs Mega ---")
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

pretax = 180_000
tax_aii = [personal_tax(pretax - c) for c in aii_by_year]
tax_mega = [personal_tax(pretax - c) for c in mega_by_year]
print("AII  CCA by yr:", [round(v) for v in aii_by_year])
print("AII  tax by yr:", [round(v) for v in tax_aii], " nominal total:", round(sum(tax_aii)), " NPV:", round(npv(tax_aii)))
print("Mega CCA by yr:", [round(v) for v in mega_by_year])
print("Mega tax by yr:", [round(v) for v in tax_mega], " nominal total:", round(sum(tax_mega)), " NPV:", round(npv(tax_mega)))
print("NPV diff (AII - Mega, i.e. Mega's saving):", round(npv(tax_aii) - npv(tax_mega)))

# ---- Farm B (unincorporated), 3-way NPV over 8-yr cycle ----
print("\n--- Farm B (unincorporated), 3-way NPV over 8-yr cycle ---")
cost = 480_000

def run_farm_b_personal(regime):
    first = cca_year1(cost, regime)
    sched = declining_balance_schedule(cost, first, years)
    loss_cf = 0.0
    taxes = []
    for cca in sched:
        taxable = pretax - cca - loss_cf
        if taxable < 0:
            loss_cf = -taxable
            taxable = 0
        else:
            loss_cf = 0
        taxes.append(personal_tax(taxable))
    return sched, taxes, loss_cf

sched_aii, taxes_aii, _ = run_farm_b_personal("aii")
sched_mega, taxes_mega_cf, _ = run_farm_b_personal("mega")
print("AII        yearly tax:", [round(x) for x in taxes_aii], " NPV:", round(npv(taxes_aii)))
print("Mega (c/f) yearly tax:", [round(x) for x in taxes_mega_cf], " NPV:", round(npv(taxes_mega_cf)))

# Mega with carryback of the $300k loss against personal tax paid in prior 3 yrs (assume 180k/yr)
prior_tax = personal_tax(180_000)
loss = 300_000
refund = min(loss, prior_tax * 3)
loss_after_cb = loss - refund
print(f"\nPrior-year personal tax at 180,000 taxable: {prior_tax:,.0f}; 3-yr carryback cap: {refund:,.0f}")
taxes_mega_cb = [0 - refund]
loss_running = loss_after_cb
for yr in range(1, years):
    taxable = pretax - 0 - loss_running
    if taxable < 0:
        loss_running = -taxable
        taxable = 0
    else:
        loss_running = 0
    taxes_mega_cb.append(personal_tax(taxable))
print("Mega (c/b) yearly tax:", [round(x) for x in taxes_mega_cb], " NPV:", round(npv(taxes_mega_cb)))
def rfl_deductible(loss):
    if loss <= 2_500:
        return loss
    return min(loss, 2_500 + 0.5 * min(loss - 2_500, 30_000))

CCA_RATE = 0.20
def cca_year1(cost, regime):
    if regime == "old":
        return cost * CCA_RATE * 0.5
    if regime == "aii":
        return min(cost, cost * CCA_RATE * 0.5 * 3)
    if regime == "mega":
        return cost

farm_income = 40_000   # net farm income before CCA -- secondary/part-time operation
off_farm_income = 140_000
cost = 480_000

print("Farm D: part-time/multi-income farmer, off-farm income $140,000 + farm income $40,000 pretax")
print(f"{'regime':6s} {'CCA':>10s} {'raw farm loss':>14s} {'deductible now':>15s} {'restricted c/f':>15s} {'taxable this yr':>16s} {'tax':>10s}")
import math
BRACKETS = [
    (0,        53_891,  0.1905),(53_891,   58_523,  0.2315),(58_523,   94_907,  0.2965),
    (94_907,   107_785, 0.3148),(107_785,  111_814, 0.3389),(111_814,  117_045, 0.3791),
    (117_045,  150_000, 0.4341),(150_000,  181_440, 0.4497),(181_440,  220_000, 0.4826),
    (220_000,  258_482, 0.4982),(258_482,  math.inf,0.5353),
]
def personal_tax(income):
    if income <= 0: return 0.0
    tax = 0.0
    for lo, hi, rate in BRACKETS:
        if income > lo:
            tax += (min(income, hi) - lo) * rate
        else:
            break
    return tax

results = {}
for regime in ["old", "aii", "mega"]:
    cca = cca_year1(cost, regime)
    raw_loss = max(0, cca - farm_income)
    deductible = rfl_deductible(raw_loss) if raw_loss > 0 else 0
    restricted_cf = raw_loss - deductible
    taxable_this_year = off_farm_income - deductible + max(0, farm_income - cca)
    tax = personal_tax(taxable_this_year)
    results[regime] = (cca, raw_loss, deductible, restricted_cf, taxable_this_year, tax)
    print(f"{regime:6s} {cca:>10,.0f} {raw_loss:>14,.0f} {deductible:>15,.0f} {restricted_cf:>15,.0f} {taxable_this_year:>16,.0f} {tax:>10,.0f}")

# years to exhaust the restricted carryforward assuming steady future farm income of $40k/yr, no further CCA
for regime in ["aii", "mega"]:
    cf = results[regime][3]
    years_to_exhaust = cf / farm_income
    print(f"{regime}: restricted c/f {cf:,.0f} / {farm_income:,.0f} per yr farm income => ~{years_to_exhaust:.1f} years to exhaust (cap 20 yrs)")

# compare deductible-this-year across regimes explicitly
print("\nDeductible-this-year is IDENTICAL for AII and Mega:", results["aii"][2] == results["mega"][2])
