# Economic Interpretation of the Results So Far

Status: training period only (decisions and months up to 31 October 2021). The blind window has not been opened. Every number here comes from files in `reports/tables`.

This note reads the models as macroeconomics: what the estimates say about how the Reserve Bank of India and Nepal Rastra Bank set policy, and why the forecasts succeed or fail where they do.

## 1. The RBI reaction function

Ordered probit on 115 RBI decisions from November 2002 to October 2021 (`india_reaction_function_economic.csv`). Average marginal effects give the change in the probability of a hike for a one unit rise in each variable.

| Variable | Coefficient | p value | Effect on P(hike), pp | Effect on P(cut), pp |
|---|---|---|---|---|
| Previous decision (smoothing) | 0.94 | below 0.001 | +24.5 | minus 16.4 |
| Revision to the RBI inflation projection | 1.05 | 0.003 | +27.6 | minus 17.6 |
| Realized inflation gap from the nominal anchor | 0.11 | 0.09 | +2.5 | minus 2.6 |
| Projected inflation gap from the nominal anchor | minus 0.23 | 0.13 | minus 4.7 | +5.7 |
| Growth gap (IIP) | 0.01 | 0.46 | +0.2 | minus 0.2 |
| Rupee depreciation, three months | minus 0.02 | 0.59 | minus 0.3 | +0.4 |

### 1.1 Interest rate smoothing is the strongest regularity

A hike makes another hike about 25 points more likely. This is the policy inertia documented by Clarida, Galí and Gertler for the Federal Reserve and modelled by Woodford as optimal under commitment: a central bank that moves in small, predictable steps gets more traction on long rates and expectations than one that moves abruptly. For forecasting it explains why "repeat the last decision" is so hard to beat: the RBI moves in cycles (six hikes in 2010 to 2011, five cuts in 2019), and inside a cycle the next step is usually the same as the last.

### 1.2 The RBI reacts to news in its own forecast

A one point upward revision to the RBI's projection raises the probability of a hike by about 28 points, while the level of the projection does not. Policy responds to new information about the inflation outlook, consistent with a forward looking, inflation forecast targeting central bank (Svensson) and with Garga and Sengupta (2026), who find the RBI responds to its published projections after inflation targeting. The revision is the cleanest summary of that news.

### 1.3 Why the gap matters and the level does not

Inflation levels carried no signal in the pooled sample, while the realized gap from the anchor has the expected positive sign (p = 0.09). The nominal anchor moved: about 5 percent WPI before 2014, then the glide path of 8 percent for January 2015 and 6 percent for January 2016, 5 percent for March 2017, and 4 percent CPI from 2017. Six percent inflation was a reason to hike in 2018 but on target in 2015. A Taylor type rule is written in deviations from target for exactly this reason. The small marginal effect (2.5 points per point of gap) is the short run response; with smoothing, the long run response is larger, because each step raises the chance of the next.

### 1.4 The projected gap has the "wrong" sign, and that is informative

A higher projected gap goes with a lower chance of a hike. RBI projections are conditional on the policy path the RBI itself intends, so when the RBI has already tightened it projects inflation returning towards target; when it projects inflation above target at the end of the horizon, it is usually already easing or holding through a supply shock. This is the endogeneity of conditional central bank forecasts: the projection partly reflects the decision rather than causing it. It is why the revision, not the level, is the policy signal.

### 1.5 Output and the exchange rate look weak, for different reasons

* **Output.** IIP covers industry only, about a quarter of GDP, and is noisy; the RBI weighs a broader activity picture. A weak output response is also consistent with an inflation targeting central bank that treats growth as a secondary objective.
* **Exchange rate.** The RBI defends the rupee mainly through foreign exchange intervention and liquidity tools rather than the repo rate. In July 2013 it raised the marginal standing facility rate and tightened liquidity while leaving the repo rate unchanged. Our target is the repo rate, so the exchange rate channel shows up in a different instrument. This supports adding a broader stance measure for India later.

## 2. Forecast performance in economic terms

| Model (75 decisions, 2010 to 2021) | Balanced accuracy | Macro F1 | Kappa | Brier |
|---|---|---|---|---|
| Persistence | 0.56 | 0.53 | 0.29 | 0.509 |
| Hybrid ordered probit (projections) | 0.59 | 0.60 | 0.31 | 0.527 |
| Economic ordered probit (anchor gaps, rupee, growth gap) | 0.64 | 0.63 | 0.39 | 0.510 |

Writing the model in terms of gaps from the regime's nominal anchor is what an economist would do, and it raised balanced accuracy from 0.59 to 0.64 without any search over features (decision D029). The remaining gap to persistence on log loss reflects the turning points: smoothing makes the RBI predictable inside a cycle, and the hard part is calling when a cycle ends. Those turning points are where the economic variables should earn their keep, and the blind window chart will show them decision by decision.

## 3. Nepal: why the interbank rate is hard to predict

The Nepal models do not beat chance at a three month horizon (balanced accuracy 0.34 to 0.38 against 0.33 for random guessing; no Diebold Mariano test significant). This is an economic finding, not only a modelling failure.

1. **The peg imports monetary policy.** With the rupee fixed at 1.6 to the Indian rupee and an open border, Nepal faces the impossible trinity: a fixed exchange rate and a largely open financial link with India leave little room for an independent interest rate. The NRB's own 2025/26 policy names the peg as the nominal anchor and the interbank rate only as an operating target.
2. **Liquidity, not policy, drives the interbank rate.** The seasonal pattern (falls of about 1 point in mid August and mid September, rises in February and May) is consistent with the government's spending and revenue calendar and with remittance flows, a hypothesis the next Nepal features test directly. Large year end spending floods banks with liquidity; revenue collection drains it. The rate sat near the corridor floor for long spells of excess liquidity (2011 to 2016, 2020, 2024 to 2025).
3. **The corridor moves rarely.** The NRB bank rate changed 17 times before November 2021, over 45 years.

### 3.1 Nepal model 2: liquidity under the peg (D030)

The second Nepal model replaces policy reaction variables with liquidity drivers built from the IMF monetary surveys (NRB reported, monthly from December 2001, lagged two months). 157 test months, July 2008 to July 2021 (`nepal_walk_forward_train_liquidity_*.csv`).

| Model | Balanced accuracy | Kappa | Log loss | Brier |
|---|---|---|---|---|
| Majority | 0.30 | minus 0.08 | 1.05 | 0.639 |
| Persistence | 0.38 | 0.09 | 1.06 | 0.644 |
| Liquidity ordered probit | 0.42 | 0.19 | 1.13 | 0.645 |
| Same without the India repo | 0.41 | 0.16 | 1.08 | 0.648 |
| Liquidity random forest | 0.40 | 0.14 | 1.03 | 0.623 |

Liquidity variables lift classification above every benchmark (balanced accuracy 0.42 against 0.38), but the probabilities are not better calibrated and no Diebold Mariano test is significant (p 0.29 to 0.52). The honest reading: liquidity explains the direction better than history does, but three months ahead the interbank rate is still mostly unforecastable.

What the model learned, with signs that hold in every or almost every walk forward window:

* **Peg inflows lower the rate.** Faster growth of NRB net foreign assets (remittances and balance of payments surpluses bought by the NRB at the fixed rate) predicts a fall. Under a peg the central bank must buy the foreign exchange, and that creates reserves: the textbook monetary consequence of a fixed exchange rate.
* **Fiscal drains raise the rate.** A rise in government deposits at the NRB (revenue collected faster than spent) predicts a rise. Money moved from banks to the government account at the NRB leaves the banking system: the fiscal liquidity channel behind the seasonal pattern.
* **Excess reserves lower the rate**, as expected when banks hold more than they need. The sign holds in 82 percent of windows.
* **Mean reversion in the level.** A high adjusted rate tends to fall, consistent with the rate moving inside the NRB corridor.
* **Credit growth above deposit growth goes with a fall, the opposite of a simple loan demand story.** A plausible reading is that credit booms came after liquidity surpluses (2011 to 2016) and were followed by NRB tightening of credit ratios rather than by a higher interbank price. We record it as an unexplained sign, not a finding.

### 3.2 The transmission test

Declared in advance: does the RBI repo change add predictive power once Nepali liquidity is controlled for? It does not. Adding it raises balanced accuracy slightly (0.42 against 0.41) but worsens log loss (1.13 against 1.08); the Diebold Mariano p value is 0.40. Its coefficient is negative in every window, which contradicts direct pass through and probably reflects timing: RBI tightening episodes coincided with Nepali liquidity surpluses. Within a three month horizon, India's policy rate does not transmit to Nepal's interbank rate beyond what liquidity already explains. This is consistent with the peg working through the balance of payments and reserves, a slow channel, rather than through short rates. The slower channel is the subject of the local projection step.

## 4. Are the learned relationships concrete and the accuracy replicable?

Declared standard (D031): a learned relationship counts only if its sign holds in at least 80 percent of walk forward windows, and accuracy is judged block by block, not only pooled (`stability_coefficients.csv`, `stability_accuracy_by_block.csv`).

**Coefficients.** All six India coefficients and all eight Nepal coefficients pass. In India, smoothing, the projection revision, the inflation gap and the projected gap keep their sign in 100 percent of 75 windows; rupee depreciation is the weakest at 81 percent and is small, so we do not interpret it. The economics the RBI model learned in 2010 is the economics it still held in 2021.

**Accuracy by three year block, against persistence.**

| Country | Block | Months or decisions | Model balanced accuracy | Persistence |
|---|---|---|---|---|
| India | 2010 to 2012 | 19 | 0.56 | 0.52 |
| India | 2013 to 2015 | 21 | 0.40 | 0.46 |
| India | 2016 to 2018 | 18 | 0.59 | 0.47 |
| India | 2019 to 2021 | 17 | 0.71 | 0.50 |
| Nepal | 2008 to 2010 | 30 | 0.31 | 0.43 |
| Nepal | 2011 to 2013 | 36 | 0.43 | 0.35 |
| Nepal | 2014 to 2016 | 36 | 0.49 | 0.35 |
| Nepal | 2017 to 2019 | 36 | 0.39 | 0.41 |
| Nepal | 2020 to 2021 | 19 | 0.54 | 0.35 |

The India model beats persistence in three of four blocks. The exception, 2013 to 2015, is economically identifiable: the July 2013 rupee defence went through the MSF rather than the repo, the anchor changed from WPI to the CPI glide path, and the RBI cut in January 2015 between scheduled meetings. Regime change is exactly where a reaction function estimated on the past should struggle, and it is where it does. Nepal beats persistence in three of five blocks; the losses are in the earliest block (smallest training window) and in 2017 to 2019. Small blocks give wide uncertainty, so the claim is "better in most periods", not "better in every period".

**Replication.** Rebuilding both feature tables and rerunning both walk forwards from the raw files gives byte identical outputs (SHA256 in `reproducibility_hashes.csv`; run `python -m src.validation.stability --check`). Random forests use a fixed seed; nothing depends on the date of the run except the downloads, which are kept with their hashes.

## 5. What this means for the paper

* India: the RBI behaves like a forecast targeting, inertial central bank whose anchor changed in steps; the policy signal is news about its own forecast and the gap from the prevailing anchor.
* Nepal: policy is constrained by the peg; short run interest rates are a liquidity phenomenon. Reserve inflows lower the rate and fiscal drains raise it, consistently across 13 years, while India's repo adds nothing at three months once liquidity is known.
* Both conclusions are on the training period. The blind window (from November 2021) is the confirmatory test.
