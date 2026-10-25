# Research Protocol (preliminary)

Version 0.1, 25 October 2026. This protocol is written before any data is analysed. Changes after this date are recorded in `docs/decision_log.md` with a reason.

## Research questions

* RQ1: Can macroeconomic information public before a decision predict RBI and NRB policy decisions better than naive baselines?
* RQ2: Do political and policy events add out of sample predictive value beyond macroeconomic variables?
* RQ3: Does the RBI stance add predictive information about NRB decisions and Nepali monetary conditions?
* RQ4: How does the INR peg shape transmission of Indian monetary policy into Nepali interest rates, inflation, liquidity, credit and output?
* RQ5: Do these relationships differ across regimes (high inflation, weak growth, external supply shocks, political uncertainty)?
* RQ6: What trade offs are associated with alternative policy scenarios, conditional on estimated responses?

## Hypotheses (stated before analysis)

* H1: For India, an ordered or regularized logistic model using the inflation gap, an activity gap and lagged policy beats persistence and majority class baselines on balanced accuracy in the blind window.
* H2: Adding political event indicators does not significantly improve out of sample log loss for India. This is stated as the null to be rejected, not as a belief.
* H3: The lagged RBI repo change improves out of sample prediction of the Nepali interbank rate change beyond Nepali domestic variables.
* H4: Pass through from Indian to Nepali short rates is incomplete and varies with Nepali liquidity conditions.

## Blind test protocol

1. Blind window: decisions announced on or after 1 November 2021. Training and selection data: information published on or before 31 October 2021.
2. Before unblinding, the following are committed to git: feature list, model classes, hyperparameter grids, selection metric, combination rule of the suggestion engine, and evaluation metrics. The SHA256 hash of `configs/blind_test.yaml` is recorded in the commit message.
3. The unblinding script refuses to run if the config hash differs from the recorded hash.
4. After unblinding, no model may be retuned on blind window results. Any later change is a new, separately labelled experiment.

## Primary metrics

Balanced accuracy, macro F1, Cohen's kappa, multiclass log loss and Brier score, with block bootstrap intervals. Turning point lead or lag in meetings.

## Claims policy

Predictive importance is never reported as causal effect. Simulation output is always labelled conditional. Negative and failed results are reported.
