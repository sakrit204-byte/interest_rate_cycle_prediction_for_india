# Blind Test Results

Status: confirmatory. The configuration was frozen on 26 October 2026 (SHA256 b81227509f09f1949102f4227f8e2a5f54dabac9d0c92f5c6abfec613afdd778, decision D035) and the blind window was opened once, afterwards. Every model is the frozen specification, refit in real time at each origin on outcomes public by then. Nothing was retuned. Tables are in `reports/tables/blind_*.csv` and `suggestions_blind*.csv`; the chart is `reports/figures/backtest_blind.png`.

Blind window: 31 RBI decisions from December 2021 to October 2026; 57 Nepali interbank months whose three month outcome falls after October 2021.

## 1. India: the RBI reaction function out of sample

| Model | Accuracy | Balanced accuracy (95% CI) | Macro F1 | Kappa | Log loss | Brier |
|---|---|---|---|---|---|---|
| Majority class | 0.65 | 0.33 | 0.26 | 0.00 | 0.929 | 0.544 |
| Persistence | 0.77 | 0.56 (0.33 to 0.88) | 0.54 | 0.48 | 0.685 | 0.389 |
| Taylor ordered probit | 0.74 | 0.64 | 0.66 | 0.47 | 0.663 | 0.401 |
| Hybrid ordered probit (projections) | 0.74 | 0.64 | 0.66 | 0.47 | 0.622 | 0.365 |
| **Economic ordered probit (primary)** | **0.77** | **0.69 (0.50 to 0.86)** | **0.70** | **0.53** | 0.640 | 0.378 |
| Random forest | 0.71 | 0.49 | 0.49 | 0.34 | 0.666 | 0.400 |

Diebold Mariano tests on log loss: primary against majority p = 0.002; against persistence p = 0.51; random forest against primary p = 0.63; primary against hybrid p = 0.29.

**Hypotheses.**

* **H1 (primary beats persistence and majority on balanced accuracy):** supported against majority, with a significant loss difference. Against persistence the point estimate is clearly better (0.69 against 0.56; kappa 0.53 against 0.48) but, with 31 decisions, the difference is not statistically significant.
* **H1b (machine learning does not beat the ordered probit):** supported. The random forest is the weakest model after majority.
* **Replication.** The training period ranking held out of sample. The economic probit was best on balanced accuracy in training (0.64) and in the blind window (0.69). All theory based probits beat persistence on balanced accuracy and log loss.

## 2. The suggestion engine against what the RBI did

| Source | Decisions called | Hit rate where called |
|---|---|---|
| Learned reaction function | 31 | 0.77 |
| Estimated inertial rule | 31 | 0.68 |
| Textbook Taylor rule | 31 | 0.35 |
| Combined suggestion | 22 | 0.77 |

The combined suggestion speaks on 22 of 31 decisions and is right on 17 of them. When it is uncertain, the two positive sources disagree, and that was usually at the start of a cycle.

**Turning points.** The window has three changes of cycle.

| Change of cycle | Learned reaction function | Estimated rule | Textbook Taylor |
|---|---|---|---|
| Hike, 4 May 2022 (unscheduled meeting) | one decision late | never called | three decisions early |
| Cut, 7 February 2025 | one decision late | five decisions late | one decision late |
| Hike, 7 October 2026 | missed (last decision in the sample) | never called | ten decisions early |

The pattern from the training period repeats exactly. A model of an inertial central bank follows it into a new cycle one meeting late. A rule without inertia sees the turn early, but it is wrong most of the time in between.

## 3. Economic reading of the blind period

**2022: a forecast targeting central bank behind the curve.** Realized inflation was 5.7 to 6.1 percent at the February and April 2022 meetings, while the RBI's own projections were 4.2 to 5.0 percent and the real repo rate was about minus 2 percent. The model said hold, as the RBI did, because it had learned that the RBI moves on revisions to its own forecast, not on realized inflation. The hikes began when the projection was revised up by about 0.9 points, and the model switched to hike with probabilities of 0.84 and 0.72 at the June and August 2022 meetings. The out of sample evidence matches the training finding (section 1.2 of `economic_interpretation.md`). Forecast revisions are the RBI's policy signal, and an optimistic forecast delays tightening.

**2023 to 2024: the long hold at 6.5 percent.** The RBI held for eleven meetings while inflation moved between 3.7 and 6.8 percent. The model called every hold. The Taylor rule kept prescribing 7 to 10 percent, because it treats each inflation print as a reason to act. The RBI looked through food price spikes with a real rate of about 1 to 3 percent, above the neutral rate of about 1.2 percent our estimated rule implies, so policy was moderately restrictive and patient. The difference between the RBI and the Taylor rule here is gradualism and supply shock accommodation.

**2025 to 2026: easing slower than inflation fell.** Realized inflation fell from 5.2 percent to 0.25 percent (October 2025 data), but the RBI's projections stayed between 4.0 and 4.9 percent. The RBI cut 125 basis points in total, and the real repo rate rose from about 1.3 to 5.3 percent. Read through the reaction function, the RBI treated the collapse as transitory food deflation and anchored on its projection, which barely moved. The model's two misses in this phase are pauses (August 2025 and February 2026), where it expected a further cut because the realized gap was so negative. The textbook Taylor rule fell below zero (minus 1 percent in December 2025), which shows why a mechanical rule on realized inflation is a poor guide when inflation swings on food prices.

**The October 2026 hike.** The RBI's projection was revised up by 0.7 points at the August 2026 meeting, and inflation had risen back to about 4.4 percent. The model put only 9 percent on a hike in October, because it reacts to the revision at the meeting where it happens and to the previous decision. The RBI waited one meeting after the revision before acting. This is the one turning point the model missed outright. It is also the last observation, so the next decision will show whether a new cycle has begun.

## 4. Nepal out of sample

| Model | Balanced accuracy | Kappa | Log loss | Brier |
|---|---|---|---|---|
| Majority | 0.33 | 0.00 | 1.112 | 0.673 |
| Persistence | 0.43 | 0.19 | 1.089 | 0.652 |
| Mean reversion rule | 0.33 | 0.00 | 1.118 | 0.677 |
| **Liquidity ordered probit (primary)** | **0.47** | **0.23** | **1.047** | **0.617** |
| Same without the India repo | 0.46 | 0.21 | 1.063 | 0.627 |
| Liquidity random forest | 0.43 | 0.17 | 1.033 | 0.618 |

* **The liquidity model replicates.** The liquidity model was the best classifier in training (balanced accuracy 0.42) and again in the blind window (0.47), with the best Brier score. No Diebold Mariano test is significant (primary against persistence p = 0.53), so it confirms the training conclusion: liquidity explains direction better than history does, but three months ahead the interbank rate is still mostly unforecastable.
* **H3 (the India repo improves the Nepal forecast):** not supported. Adding the RBI repo change lowers log loss slightly in the blind window (1.047 against 1.063), but the test does not reject (p = 0.23). This matches the local projections, which find no short rate transmission.
* **NRB corridor decisions** in the window are described, not scored (D033). The NRB moved too rarely for a classifier.

## 5. What the blind test establishes

1. The RBI's behaviour from 2022 to 2026 is the behaviour learned from 2002 to 2021. It is inertial and forecast targeting: it moves on revisions to its own projection and on the gap from its anchor. That model called 77 percent of decisions, without retuning, across a tightening cycle, a long hold and an easing cycle.
2. Persistence remains a strong benchmark. The gain over it is in balanced accuracy and in calling holds and cycle phases, not in significantly better probabilities on 31 decisions.
3. The models anticipate no turning point. Interest rate smoothing makes the start of a cycle the hardest decision to predict, both in sample and out of sample.
4. For Nepal, the peg makes short rates a liquidity phenomenon. India's policy rate adds no reliable short horizon information, out of sample as in training.
