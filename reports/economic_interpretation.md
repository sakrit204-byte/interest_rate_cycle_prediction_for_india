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

The economic implication is that a Nepal model needs liquidity drivers rather than policy reaction variables: government balances at the NRB, remittance inflows, deposit growth relative to credit growth, and NRB open market operations. These are the next Nepal features. The test of transmission from India is then whether RBI moves still help once domestic liquidity is controlled for.

## 4. What this means for the paper

* India: the RBI behaves like a forecast targeting, inertial central bank whose anchor changed in steps; the policy signal is news about its own forecast and the gap from the prevailing anchor.
* Nepal: policy is constrained by the peg; short run interest rates are a liquidity phenomenon, so predictability must come from the liquidity calendar and balance of payments flows, with Indian policy as a slower background force.
* Both conclusions are on the training period. The blind window (from November 2021) is the confirmatory test.
