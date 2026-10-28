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

The Nepal models do not beat chance at a three month horizon (balanced accuracy 0.35 to 0.38 against 0.33 for random guessing; no Diebold Mariano test significant). This is an economic finding, not only a modelling failure.

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

## 5. Transmission from India to Nepal: local projections (D032)

Response of Nepali variables to a one point (100 basis point) change in the RBI repo rate, from monthly local projections, August 2000 to October 2021, holding oil prices, US policy and Indian inflation fixed (`local_projections.csv`). The RBI moved 60 times in the sample.

| Months after the RBI move | Interbank rate, pp | 91 day T bill, pp | CPI inflation, pp | Private credit growth, pp |
|---|---|---|---|---|
| 0 | minus 0.39 (p 0.28) | minus 0.21 (p 0.48) | 0.12 (p 0.59) | minus 1.0 (p 0.67) |
| 3 | minus 0.59 (p 0.41) | minus 0.38 (p 0.50) | 0.15 (p 0.81) | 1.3 (p 0.74) |
| 6 | minus 0.73 (p 0.33) | minus 0.70 (p 0.32) | 0.10 (p 0.88) | 8.1 (p 0.10) |
| 12 | minus 1.57 (p 0.05) | minus 0.43 (p 0.44) | 0.04 (p 0.95) | 6.0 (p 0.21) |
| 24 | minus 0.88 (p 0.22) | minus 0.25 (p 0.70) | 0.87 (p 0.23) | 7.9 (p 0.31) |

### 5.1 Reading

1. **No direct interest rate pass through.** Under a credible peg with an open capital link, uncovered interest parity would make Nepali short rates follow Indian rates one for one. They do not: the point estimates are negative at every horizon, and at twelve months full pass through (plus 1) lies outside the confidence interval for the interbank rate. Nepal's border with India is open for goods and cash, but its capital account is largely closed and its banks cannot freely arbitrage into Indian money markets. Capital controls are what let the peg and an independent short rate coexist, the escape route from the impossible trinity.
2. **Why the sign is negative.** The negative sign should not be read as Indian tightening easing Nepali money. RBI cycles are few (about six tightening and easing episodes) and they happened to coincide with Nepali liquidity cycles running the other way. The clearest case is 2010 to 2011, when the RBI hiked while Nepal had a liquidity crunch, which then turned into a remittance driven surplus. With so few independent episodes, timing coincidences dominate. The safe conclusion is negative, not that the effect is negative: the data show no positive transmission through short rates.
3. **No measurable response of inflation to the RBI's own moves.** The CPI response is near zero for a year and rises to 0.9 points after two years, but it is not significant (p 0.23). An earlier version reported 1.5 points (p 0.04); that came from an error in the IMF CPI file, in which the price index for mid August 2006 to mid July 2007 repeats the year before, so measured inflation was zero for twelve months. Those months are now left missing (D052). The peg does tie Nepal's prices to India's (inflation in the two countries moves together, section 5.4), but that link runs through Indian prices and the exchange rate, not through the RBI repo rate itself.
4. **Credit responds positively but imprecisely**, as it would if Indian tightening coincides with Indian demand booms that raise Nepali trade and remittance income. None of these estimates is significant.

### 5.2 Does liquidity change transmission? (H4)

Splitting the RBI shock by Nepali excess reserves (`local_projections_state.csv`) shows a larger negative interbank response when liquidity is abundant (minus 3.3 points at twelve months, p 0.001) than when it is scarce (minus 1.0, p 0.47). This pattern is the opposite of H4's mechanism, under which abundant liquidity should mute any transmission. It supports the coincidence reading above: abundant liquidity episodes are the remittance surpluses that overlapped with RBI tightening. H4 as stated (incomplete pass through that varies with liquidity) holds only in the trivial sense that pass through is absent; we do not claim a liquidity dependent transmission mechanism.

### 5.3 What it means for the transmission question

India's monetary policy does not reach Nepal through short term interest rates, and its effect on Nepali inflation cannot be measured with confidence. What the peg transmits is India's prices and, through the balance of payments, liquidity. This matches the forecasting result in section 3.2: the RBI repo adds nothing to a three month forecast of the interbank rate once liquidity is known. Both methods point the same way, which is more convincing than either alone.

### 5.4 What the peg carries and what it does not (D052)

Side by side, from `peg_channels.csv` and `reports/figures/peg_channels.png`:

| Period | Inflation correlation, India and Nepal, same month | 12 month change in RBI repo and Nepal interbank rate, correlation | Nepal interbank minus RBI repo, mean, points |
|---|---|---|---|
| 2001 to 2026 | 0.46 (0.66 with India's CPI only, from 2013) | minus 0.07 | minus 3.2 |
| Before the corridor, 2001 to 2016 | 0.32 | minus 0.20 | minus 3.9 |
| Corridor, 2016 to 2021 | 0.29 | 0.45 | minus 2.7 |
| Blind window, 2021 to 2026 | 0.88 | 0.18 | minus 1.4 |

Prices follow India: average inflation is close in the two countries (5.5 percent in India, 6.4 in Nepal since 2001) and, once India's CPI is used on both sides, the two rates move together closely, most of all since 2021 when both were driven by the same food and fuel shocks. Interest rates do not: over 25 years the change in Nepal's interbank rate is unrelated to the change in the RBI repo rate, and Nepal's rate sits on average three points below it. The positive correlation in 2016 to 2021 covers a single cycle (both fell in 2020 with the pandemic, a common shock rather than transmission). This is the impossible trinity resolved through capital controls: the peg fixes the exchange rate and so imports India's price level, while the closed capital account leaves the NRB its own short rate, which is set by the liquidity that the peg creates when remittances are converted at the fixed rate (D049).

## 6. What this means for the paper

* India: the RBI behaves like a forecast targeting, inertial central bank whose anchor changed in steps; the policy signal is news about its own forecast and the gap from the prevailing anchor.
* Nepal: policy is constrained by the peg; short run interest rates are a liquidity phenomenon. Reserve inflows lower the rate and fiscal drains raise it, consistently across 13 years, while India's repo adds nothing at three months once liquidity is known. The peg carries India's prices into Nepal (inflation correlation 0.66 since 2013), but not India's policy rate, from which Nepal's capital controls insulate it.
* Both conclusions are on the training period. The blind window (from November 2021) is the confirmatory test.

## 7. The suggestion engine on the training period

The engine (`src/policy/suggestion_engine.py`, D033) was run in real time over the 75 training decisions from 2010 to 2021 (`suggestions_train.csv`, figure `reports/figures/backtest_train.png`). This is a rehearsal; the confirmatory test is the blind window.

| Source | Decisions called | Hit rate where called |
|---|---|---|
| Learned reaction function (economic ordered probit) | 75 | 0.65 |
| Estimated inertial rule | 75 | 0.51 |
| Textbook Taylor rule | 75 | 0.31 |
| Combined suggestion (classifier and rule agree, top probability above 0.5) | 42 | 0.64 |

**What the estimated rule says about the RBI.** Across the walk forward windows, the RBI closes about 6 percent of the gap between the policy rate and its neutral level at each decision (smoothing 0.94, range 0.87 to 0.97), and the implied neutral real rate is about 1.2 percent (interquartile range 0.9 to 1.35). Both are economically sensible: heavy inertia is the norm for inflation targeting central banks, and a real neutral rate a little above 1 percent is in the range discussed for India. Because each step is small, the rule's prescribed change rarely clears the 12.5 basis point deadband, so it mostly says hold. That is why the combined suggestion covers only 42 of 75 decisions: it speaks only when the two positive sources agree.

**Turning points.** The learned reaction function called every change of cycle (2012, 2013, 2015, 2018, 2019) exactly one decision late. That is the signature of interest rate smoothing in the data: the best single predictor of the next move is the last move, so a model fitted to an inertial central bank follows it into a new cycle rather than anticipating it. The textbook Taylor rule signals each turn early, two to fourteen decisions ahead, because it has no inertia, but it is wrong most of the time in between (hit rate 0.31) and swings wildly when IIP growth jumps on base effects (minus 10 percent in August 2020, 38 percent in August 2021). The gap between the two is the practical meaning of gradualism: the RBI does what a Taylor rule says only slowly and only after the evidence accumulates.

## 8. Do political events help? (H2, D034)

Training period walk forward, each primary model with and without political indicators (`ablation_political_*.csv`).

| Model | Balanced accuracy | Log loss | Brier | Diebold Mariano p |
|---|---|---|---|---|
| India economic probit | 0.64 | 0.866 | 0.510 | |
| with election and budget indicators | 0.64 | 0.849 | 0.485 | 0.57 |
| Nepal liquidity probit | 0.42 | 1.132 | 0.645 | |
| with government change and disruption indicators | 0.40 | 1.151 | 0.660 | 0.32 |

H2 (political events add nothing) is not rejected in either country. For India the probabilities improve slightly but not significantly; only five training decisions fell inside an election period, far too few to estimate a political business cycle, and an independent central bank with a statutory inflation target from 2016 gives less room for one. Budgets carry fiscal news, but the RBI already sees it through its own inflation projection, which is in the model. For Nepal, government turnover is so frequent (a new prime minister about once every 14 months) that it is almost background; what matters for the interbank rate is whether turnover changes spending, which the government deposit feature already measures directly. The economic lesson is that political shocks act on monetary conditions through the fiscal and liquidity variables already in the models, not as separate predictors.

## 9. Blind window and the textbook rule's extreme values

The confirmatory results are in `reports/blind_test_results.md`. The textbook Taylor rule leaves the chart scale five times. The August 2020 (minus 10 percent), October 2020 (minus 1 percent) and August 2021 (38 percent) values come from IIP growth swinging on pandemic base effects, which the rule reads as an output gap. The December 2025 (minus 1 percent) and February 2026 (about 0 percent) values come from realized inflation falling to between 0.25 and 1.3 percent on food prices. Both cases show why central banks do not set rates mechanically from realized data: one noisy activity indicator or one supply shock can move a static rule by several points.
