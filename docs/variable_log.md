# Variable Log

This log explains every variable that was considered, why it is used, and why it is left out. The machine readable ledger is `data/source_registry/variable_registry.csv`. The two are updated together, and every status change is recorded below with a date.

## Status meanings

* **core**: planned for the main specification, subject to feasibility verification.
* **candidate**: considered on economic grounds; enters only if it passes the ablation rule in `docs/implementation_plan.md` Section 5.
* **robustness**: used only in sensitivity checks, usually because it is collinear with a core variable, slow to publish, or short in history.
* **pending_feasibility**: economically relevant, but free access or coverage is not yet confirmed.
* **excluded**: considered and rejected, with the reason recorded.

## Selection principles

1. Economic channel first: a variable must map to a documented channel in the RBI or NRB reaction function or in transmission.
2. Observable at the cutoff: it must have been published before the decision cutoff, using its real publication lag.
3. Free and legitimate access.
4. Small sample discipline: correlated variables compete for one slot rather than all entering together.
5. No silent substitution: if a series is unavailable, the substitute gets its own row and reason.

## Why the core set looks the way it does

* **India**: CPI headline inflation (target variable of the inflation targeting framework), IIP (only timely monthly activity proxy), the call rate (operating target), USD/INR (external pressure), Brent (imported inflation), and the lagged repo change (policy inertia). GDP is a candidate rather than core because it arrives with a long lag and is revised.
* **Nepal**: CPI, private credit growth, reserves, remittances, the interbank rate and the peg rate. The policy rate is the target but too short for training, so the interbank rate and a stance index carry the training load.
* **Cross border**: the RBI repo change and the India to Nepal interest differential are core because RQ3 and RQ4 cannot be answered without them.

## Notable exclusions so far

| Variable | Reason |
|---|---|
| Equity index returns | No clear channel at decision frequency; noise in a small sample |
| Paid news sentiment | Breaks the zero cost requirement |
| LLM event classification | Paid inference and reproducibility; manual coding with audit is used instead |
| Nepal EPU index | None published; building one is outside current scope |

## Change history

| Date | Variable | Change | Reason |
|---|---|---|---|
| 25 Oct 2026 | All | Ledger created | Initial planning; no coverage verified yet |
