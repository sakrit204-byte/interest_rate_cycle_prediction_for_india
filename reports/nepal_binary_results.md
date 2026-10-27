# Nepal binary model: results

Decisions D038 and D039. Specification frozen on 27 October 2026, SHA256
315638711b569799c6d5f03cc6a29356c4d7ede0620af2ea15f1a82740a39a77, committed (1b7286d) before
its first run on 2021 to 2026. Source: reports/tables/nepal_binary_metrics.csv and
nepal_binary_predictions.csv.

## Why the question changed

The pre registered Nepal model asked whether the seasonally adjusted interbank rate would be
down, flat or up three months ahead. On the blind window it reached a balanced accuracy of 0.47
against 0.43 for persistence. A search on the training period only (D038, about 30 designs, all
recorded) found no three class design above 0.48, and log loss was often worse than a uniform
guess. The exact three way direction of a liquidity price under the peg is close to
unforecastable from public monthly data.

The new model asks two narrower questions about the published rate: will it fall by more than
half a point over three months, and will it rise by more than half a point. It uses last
month's interbank rate, which banks know because they trade at it daily, and keeps the fiscal
year liquidity calendar as a signal instead of removing it.

Chance balanced accuracy for a yes or no question is 0.50, not 0.33, so these figures are not
comparable with the three class ones.

## Results

| Period | Question | Model | Calendar only | Persistence | Months | Share of yes |
|---|---|---|---|---|---|---|
| Training, 2008 to 2021 | Fall | **0.73** (0.66 to 0.81) | 0.63 | 0.51 | 158 | 0.35 |
| Training, 2008 to 2021 | Rise | **0.64** (0.54 to 0.73) | 0.60 | 0.49 | 158 | 0.30 |
| 2021 to 2026, post hoc | Fall | 0.53 (0.28 to 0.73) | 0.53 | **0.65** | 57 | 0.19 |
| 2021 to 2026, post hoc | Rise | **0.67** (0.36 to 0.83) | 0.50 | 0.60 | 57 | 0.18 |

Balanced accuracy, with 95 percent block bootstrap intervals in brackets. The 2021 to 2026 rows
are a second look at a window that had already been seen when the model was declared, so they
are not a blind test.

## Reading

**Rises survive, falls do not.** The model calls half point rises in the interbank rate in both
periods, at 0.64 and 0.67, ahead of the calendar and of persistence. Tightening of liquidity is
forecastable: it follows the fiscal calendar (revenue collection and slow capital spending early
in the fiscal year), falls in the NRB's net foreign assets and credit growing faster than
deposits.

The fall question breaks down after 2021. Falls became rarer (19 percent of months against 35
percent in training) because the rate spent long stretches pinned near the corridor floor, most
of all from mid 2024 to mid 2025 (D013). At the floor a rate cannot fall further, and the
training period contains few months like that, so the model kept predicting falls that the floor
prevented. Persistence did better because falls arrived in clusters.

**What this means for the 60 percent target.** On the training period both questions clear it.
On 2021 to 2026, rises clear it and falls do not. The intervals on 57 months with about ten yes
cases each are wide, so neither post hoc figure is precise. The honest summary is one robust
result (liquidity tightening) and one regime dependent one (easing, limited by the floor).

## Sealed forecasts

These outcomes were not public when the model was frozen, and will be scored as the bulletin
tables for August to October 2026 are released.

| Origin | Outcome month | P(fall) | P(rise) |
|---|---|---|---|
| May 2026 | August 2026 | 0.58 | 0.12 |
| June 2026 | September 2026 | 0.44 | 0.20 |
| July 2026 | October 2026 | 0.24 | 0.29 |

No outcome later than October 2026 can be forecast yet, because the bulletin data end in July
2026.
