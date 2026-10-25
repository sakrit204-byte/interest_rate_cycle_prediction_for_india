# Step 7: India Baselines, Walk Forward on the Training Period

Status: first run, 25 October 2026. Realized inflation only (no RBI projections yet). The blind window (from 1 November 2021) was not read; the evaluation code refuses its rows.

## Design

* Data: 120 RBI decisions from April 2001 to October 2021 with all features (2 early decisions lack a previous decision).
* Information cutoff: decision date minus 7 days. Every feature uses only values public by then (see `docs/decision_log.md`, D004 and D021).
* Walk forward: models are refitted before each of the last 80 training decisions (March 2010 to October 2021), using only decisions whose outcome was known by the cutoff. Features are standardized on each training window.
* Feature set v1 (ten features): targeted inflation (WPI before 21 January 2014, CPI after), its three month change, IIP growth (three month average), repo level, real rate, six month repo change, six month US policy rate change, previous decision, FIT and MPC regime indicators.
* Uncertainty: 95 percent moving block bootstrap intervals (blocks of six decisions) for balanced accuracy.

## Results (80 test decisions)

| Model | Accuracy | Balanced accuracy (95% interval) | Macro F1 | Kappa | Log loss | Brier |
|---|---|---|---|---|---|---|
| Majority class | 0.54 | 0.36 (0.29 to 0.47) | 0.31 | 0.04 | 1.02 | 0.61 |
| Persistence (Markov) | 0.63 | 0.53 (0.41 to 0.61) | 0.51 | 0.31 | 0.84 | 0.51 |
| Inflation change threshold rule | 0.46 | 0.36 (0.23 to 0.51) | 0.32 | 0.02 | 1.02 | 0.62 |
| Ordered probit, ten features | 0.51 | 0.44 (0.26 to 0.56) | 0.46 | 0.13 | 1.18 | 0.59 |
| Ordered probit, Taylor type (four features) | 0.59 | 0.52 (0.36 to 0.67) | 0.54 | 0.26 | 0.89 | 0.54 |
| Logistic with L2 penalty | 0.63 | 0.52 (0.36 to 0.62) | 0.49 | 0.29 | 0.90 | 0.55 |
| Random forest (depth 3) | 0.68 | 0.55 (0.38 to 0.64) | 0.52 | 0.37 | 0.81 | 0.49 |

Full tables: `reports/tables/walk_forward_train_metrics.csv`, by period in `walk_forward_train_metrics_by_period.csv`, and every prediction in `walk_forward_train_predictions.csv`.

## Reading the results

1. **No model clearly beats persistence.** Every balanced accuracy interval overlaps the persistence interval. The RBI moves in runs, and "do what you did last time" is a strong benchmark. This is the bar every later model must clear.
2. **The ten feature ordered probit overfits.** Its log loss (1.18) is worse than always predicting the training class shares (1.02). In 2014 to 2021 its log loss rises to 1.41. With about 40 to 120 training decisions per window, ten unpenalized slopes plus two cut points are too many.
3. **The Taylor type ordered probit is the best interpretable model.** Inflation, its change, output growth and the previous decision give the highest macro F1 (0.54) and a log loss close to persistence. It was declared after the first run (D023), so this comparison is reported as exploratory, not as a confirmed test.
4. **2014 to 2021 is hard for every model.** Under inflation targeting the RBI held often and hiked only twice before the blind window, and no model beats always hold on plain accuracy there (0.65). Balanced accuracy in that period ranges from 0.28 to 0.43.
5. **Hypothesis H1 is not supported on the training period with realized inflation only.** H1 expects the ordered probit with projected and realized inflation gaps to beat the baselines; projections are not yet in the model, so the test of H1 as written comes with the second model.

## What this changes next

* The second model adds RBI published inflation projections (IN029), as agreed, using the Taylor type specification as the base.
* A learning curve and a label permutation test are run before the blind window, to show whether more data or a different feature set could help, and that the learned signal is not chance.
* No further specifications are tried on this validation set without a decision log entry, to limit the number of comparisons.
