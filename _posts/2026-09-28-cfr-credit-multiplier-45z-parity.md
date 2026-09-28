---
layout: post
title: "Ottawa's Proposed Biofuel Credit Multiplier Would Match the US 45Z Credit at 1.14 for Ethanol. Our Math Says Matching an Iowa Plant Takes About 1.5"
date: 2026-09-28
categories: [biofuels, trade-policy, energy-policy]
excerpt: "Environment and Climate Change Canada says a credit multiplier of about 1.14 for ethanol and 1.4 for biomass-based diesel would replicate what US producers get from the 45Z tax credit. The diesel number holds up when you run the math. The ethanol number looks too low once you account for how the US dropped indirect land-use emissions from 45Z scoring in 2026."
source: manual
sources_cited:
  - "https://www.canada.ca/en/environment-climate-change/corporate/transparency/consultations/share-view-ideas-targeted-amendments-clean-fuel-regulations/discussion-paper.html"
  - "https://www.clearbluemarkets.com/knowledge-base/canadas-clean-fuel-regulations-and-us-45z-incentives-what-to-expect-from-the-cfr-targeted-amendments"
  - "https://ethanolrfa.org/media-and-news/category/news-releases/article/2026/01/rfa-comments-on-proposed-amendments-to-canada-s-clean-fuel-regulations"
  - "https://laws-lois.justice.gc.ca/eng/regulations/SOR-2022-140/page-12.html"
  - "https://www.irs.gov/pub/irs-drop/n-26-53.pdf"
  - "https://www.hklaw.com/en/insights/publications/2026/09/section-45z-2026-emissions-rate-table"
  - "https://www.agbull.com/beyond-rins-45z-carbon-scores-and-trade-redraw-the-biofuels-market/"
  - "https://www.grainjournal.com/article/1153414/updated-45z-model-could-boost-soybean-demand-and-farm-level-value"
  - "https://farmdocdaily.illinois.edu/2026/05/the-clean-fuel-production-tax-credit-45z-introductory-discussion.html"
  - "https://www.foundationeconomics.com/insights/260506_CFRPriceDynamics"
  - "https://www.mtfxgroup.com/tools/historical-currency-exchange-rates/usd-to-cad-rate/"
  - "https://www.mickco.com/news-insights/greet-model-revised"
---

**By Kal Sharven**

**TL;DR:** Ottawa is considering a credit multiplier under the Clean Fuel Regulations (CFR): domestic low-carbon fuel would earn more compliance credits per litre than the same imported fuel. ECCC's December 2025 discussion paper says a multiplier of about **1.4 for biomass-based diesel** and about **1.14 for ethanol** would replicate the per-litre value US producers get from the 45Z tax credit. We reverse-engineered both numbers and then re-ran them against 45Z as it works after the 2026 rule changes. For renewable diesel and biodiesel, ECCC's 1.4 checks out: parity lands at roughly **1.34 to 1.47** depending on the fuel and inputs. For ethanol, it doesn't. ECCC's 1.14 implies a US benefit of about 5 cents CAD per litre, which corresponds to a 45Z score near 43 kg CO2e/mmBtu, or roughly US$0.13 a gallon. But the US removed indirect land-use change (ILUC) emissions from 45Z scoring for fuel made after 2025, and industry analysts put a typical corn ethanol plant near a score of 30, worth about **US$0.40 a gallon**. At that value the multiplier needed for parity is about **1.5**, not 1.14. The gap is not a math error on ECCC's part so much as a timing one: the discussion paper (December 3, 2025) predates the US model update (June 12, 2026) that changed the answer.

## What Ottawa actually proposed

On September 5, 2025, the federal government announced targeted amendments to the CFR alongside a CAD 370 million Biofuel Production Incentive covering 2026 and 2027. ECCC's [discussion paper](https://www.canada.ca/en/environment-climate-change/corporate/transparency/consultations/share-view-ideas-targeted-amendments-clean-fuel-regulations/discussion-paper.html) laid out two ways to favour domestic low-carbon fuel: a minimum domestic content requirement, or a credit multiplier. The context is import share: in 2024, more than 70% of CFR compliance credits came from imported fuel, mostly from the US, and imported US grain ethanol supplied 61% of the ethanol used to comply, according to the [Renewable Fuels Association](https://ethanolrfa.org/media-and-news/category/news-releases/article/2026/01/rfa-comments-on-proposed-amendments-to-canada-s-clean-fuel-regulations) (RFA). US trade groups have come out in favour of the multiplier over the domestic-content option.

The multiplier works on credit creation. A domestic low-carbon fuel would generate more credits per litre than the identical imported litre. ECCC left open that different fuels could get different multipliers, and it sized the two headline examples to "the per-litre value Canadian producers are giving up by not having an equivalent to 45Z." Its stated inputs:

| | Renewable diesel | Ethanol |
|---|---|---|
| Multiplier | ~1.4 | ~1.14 |
| Credit price assumed (2030) | CAD 300/tonne | CAD 300/tonne |
| Reference carbon intensity | 80.1 g CO2e/MJ | 80.1 g CO2e/MJ |
| Average fuel carbon intensity | 30 g CO2e/MJ | 38 g CO2e/MJ |
| US production incentive | ~23 cents CAD/L | ~5 cents CAD/L |

As of the most recent reporting we could find (late August 2026), draft regulatory text had not yet appeared in the Canada Gazette, Part I, so none of this is final.

## The parity math

Setting the multiplier so a Canadian plant matches a US plant is a one-line calculation. A US plant selling into Canada earns 45Z **plus** the ordinary CFR credits (multiplier of 1.0). A Canadian plant earns CFR credits times M and no 45Z. Parity requires:

**M = 1 + (45Z value per litre, in CAD) / (CFR credit value per litre, in CAD)**

Both pieces are computable from public rules:

- **CFR credits per litre** = (reference CI − fuel CI) × energy density × 10⁻⁶, multiplied by the credit price. The [regulations](https://laws-lois.justice.gc.ca/eng/regulations/SOR-2022-140/page-12.html) (Schedule 2) set energy density at 23.419 MJ/L for ethanol, 34.921 MJ/L for renewable diesel, and 35.183 MJ/L for biodiesel.
- **45Z value per gallon** = US$1.00 × (50 − emissions rate) / 50, where the rate is in kg CO2e/mmBtu and the $1.00 assumes the prevailing-wage and apprenticeship requirements are met. Without them the credit is one-fifth of that.
- **Conversion**: 3.785 litres per gallon and USD/CAD of 1.414 (the September 24 rate).

**Back-testing ECCC.** Plugging ECCC's own inputs into this formula gives 1.17 for ethanol and 1.44 for renewable diesel, against its published 1.14 and 1.4. The diesel figure is close. The ethanol figure implies ECCC used a US benefit nearer 4 cents CAD/L than 5. That is well within the "approximately" in the paper, and it tells us the formula is a fair reconstruction of ECCC's method, which the paper does not spell out. (ECCC does not disclose the exchange rate or the exact 45Z score it used.)

## Ethanol: what an Iowa plant's 45Z score means for the multiplier

The right starting question is what an Iowa dry-mill plant's credit actually is, and that is where ECCC's number gets shaky. Notice 2026-53, issued September 8, confirms that fuel made after 2025 must [exclude ILUC emissions](https://www.hklaw.com/en/insights/publications/2026/09/section-45z-2026-emissions-rate-table) from 45Z scoring, and that feedstock must come from the US, Canada, or Mexico. The updated 45ZCF-GREET model published June 12 implements this. The notice points plants to the model and does not publish a "typical plant" score, so each plant computes its own. Industry analysts have described the ILUC removal as dropping an average corn ethanol plant's score by 20 to 25 points, and one recent market [analysis](https://www.agbull.com/beyond-rins-45z-carbon-scores-and-trade-redraw-the-biofuels-market/) uses a score of 30 kg CO2e/mmBtu as an illustration, worth $0.40 a gallon. We treat a range of scores as scenarios, since we could not locate an official plant-average figure.

The table shows the multiplier that equalizes each score, for a Canadian plant at ECCC's assumed CFR carbon intensity of 38 g/MJ, at three credit prices:

| 45Z score (kg CO2e/mmBtu) | 45Z value (US$/gal) | 45Z value (CAD c/L) | M at CAD 300/t | M at CAD 350/t | M at CAD 430/t |
|---|---|---|---|---|---|
| 45 | $0.10 | 3.7 | 1.13 | 1.11 | 1.09 |
| 40 | $0.20 | 7.5 | 1.25 | 1.22 | 1.18 |
| 35 | $0.30 | 11.2 | 1.38 | 1.32 | 1.26 |
| **30** | **$0.40** | **14.9** | **1.51** | **1.43** | **1.35** |
| 25 | $0.50 | 18.7 | 1.63 | 1.54 | 1.44 |
| 20 | $0.60 | 22.4 | 1.76 | 1.65 | 1.53 |
| 15 | $0.70 | 26.1 | 1.88 | 1.76 | 1.62 |

ECCC's 1.14 corresponds to the top row, a plant scoring in the mid-40s and collecting about ten cents a gallon. That is roughly what a typical plant would have looked like with ILUC still in the score. It is not what the same plant collects in 2026. A plant with carbon capture, which the same analysts put in the low teens on the 45Z scale, sits at the bottom of the table and would need a multiplier of about 1.9 at CAD 300.

Two other inputs move the answer:

- **The Canadian plant's own score.** A Canadian plant with a higher CFR carbon intensity earns fewer credits per litre, so the multiplier has a smaller base to work on and must be larger to deliver the same cents. At a 45Z score of 30 and CAD 300, parity ranges from 1.42 (Canadian CI of 30) to 1.71 (CI of 50).
- **The credit price.** The multiplier scales the credit, so its dollar value rises and falls with the CFR price. CFR credits reportedly [reached CAD 430 per tonne](https://www.foundationeconomics.com/insights/260506_CFRPriceDynamics) in early April 2026, well above ECCC's CAD 300 assumption for 2030. At CAD 430, parity for the $0.40 plant falls to 1.35. If credit prices stay high, a smaller multiplier does the same job.

## Renewable diesel and biodiesel

The diesel side is where ECCC's number holds. The soybean pathway is scored with the same ILUC exclusion. The American Soybean Association, as [reported](https://www.grainjournal.com/article/1153414/updated-45z-model-could-boost-soybean-demand-and-farm-level-value) by Grain Journal on August 28, puts soybean-oil renewable diesel at a score of 26.36 (down from 42.60), worth $0.55 a gallon, and soybean biodiesel at 20.23 (down from 33.70), worth $0.66 a gallon.

One inconsistency to flag: applying the statutory formula to those scores gives $0.47 and $0.60, not $0.55 and $0.66. We do not know whether the gap reflects inflation indexing, rounding, or a different basis in the ASA's calculation, so we show both. Parity for a Canadian plant at a CFR score of 30 g/MJ, using each version:

| Fuel | 45Z basis | M at CAD 300/t | M at CAD 350/t | M at CAD 430/t |
|---|---|---|---|---|
| Renewable diesel (soy, CI 26.36) | Formula, $0.47/gal | 1.34 | 1.29 | 1.23 |
| Renewable diesel (soy, CI 26.36) | ASA figure, $0.55/gal | 1.39 | 1.33 | 1.27 |
| Biodiesel (soy, CI 20.23) | Formula, $0.60/gal | 1.42 | 1.36 | 1.29 |
| Biodiesel (soy, CI 20.23) | ASA figure, $0.66/gal | 1.47 | 1.40 | 1.33 |

At ECCC's own credit price, its 1.4 sits just above the renewable diesel range (1.34 to 1.39) and just below the biodiesel range (1.42 to 1.47), so it is a fair round number for both. If the reference is waste-based feedstock with a much lower score, the 45Z credit would be larger and the multiplier needed would be higher.

The chart shows the relationship directly. The ethanol line is steeper because ethanol earns fewer CFR credits per litre than diesel-range fuels at the same credit price, so each extra cent of 45Z requires more multiplier to offset.

![Multiplier needed for parity versus US 45Z credit value]({{ '/assets/images/cfr-multiplier-45z-parity.png' | relative_url }})

## Caveats that cut both ways

- **45Z has an end date; the CFR does not.** The US credit runs for fuel sold through 2029. A multiplier written into a permanent regulation would outlast the benefit it is meant to match.
- **A higher multiplier puts more credits into the market.** More supply pushes the credit price down, which shrinks the dollar value of every credit, including the multiplied ones. ECCC lists credit-market impact among its factors for choosing multipliers. This is a self-limiting effect, and the CAD 300 versus CAD 430 columns show how much the price matters.
- **The 45Z is monetized at a discount.** Most plants sell the credit rather than use it, and a sale price below face value shaves the US benefit and therefore the multiplier needed. We show face value throughout.
- **This is per-litre parity, not a full competitiveness comparison.** It ignores feedstock costs, freight, RIN and LCFS revenue, and the separate Biofuel Production Incentive, which would offset part of the gap for Canadian producers for two years.
- **The ethanol score is a scenario.** We found no official plant-average 45Z score for corn ethanol. The $0.40 example comes from a secondary analysis; a plant's real figure depends on its own inputs and, increasingly, on farm-level practices through the USDA feedstock calculator.

## What to watch

The number that matters is the one in the Canada Gazette. If ECCC finalizes an ethanol multiplier near 1.14 while 45Z pays a typical plant near $0.40 a gallon, the multiplier closes roughly a quarter of the gap on our numbers, and a US plant would still hold most of its per-litre advantage on Canadian sales. If ECCC re-runs its ethanol estimate with the post-ILUC 45Z scores, the multiplier it publishes could move toward the 1.4 to 1.5 range. The credit price is the other variable: at the CAD 400-plus prices seen this spring, a given multiplier does more work than ECCC's CAD 300 planning assumption suggests.

*The model behind these tables, including the ECCC back-test and sensitivity runs, is saved in the site's `_research` folder as `2026-09-28-cfr-multiplier-45z-equalization.py`.*
