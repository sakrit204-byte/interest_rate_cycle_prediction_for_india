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

* **India**: the RBI published inflation projection and CPI headline inflation (the RBI responds to its projections more clearly than to realized inflation since 2015), IIP (only timely monthly activity proxy), the call rate (operating target), USD/INR (external pressure), Brent (imported inflation), and the lagged repo change (policy inertia). GDP is a candidate rather than core because it arrives with a long lag and is revised.
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
| 25 Oct 2026 | IN029, IN030 | Added: RBI published inflation (core) and growth (candidate) projections | Literature shows RBI responds to its own projections |
| 25 Oct 2026 | IN031 | Added as pending: monetary policy uncertainty index | Found in screening; data not located |
| 25 Oct 2026 | IN028 | Source URL and coverage filled in | Lakdawala and Sengupta dataset located |
| 25 Oct 2026 | IN007, IN008, IN009, IN011, IN015 | Coverage verified from the MoSPI open API; WPI and IIP sources moved to that API | No account needed after all; see docs/data_access.md |
| 25 Oct 2026 | Feature set v1 | First India feature set fixed at ten features: targeted inflation, its three month change, IIP growth (three month average), repo level, real rate, six month repo change, six month US policy rate change, previous decision, FIT and MPC regime indicators | Realized inflation only, as agreed for the first run; small budget for 120 training decisions (about one feature per twelve decisions) |
| 25 Oct 2026 | IN008, IN009, IN010 | Left out of feature set v1 | Collinear with headline; held for a later robustness model to keep the budget |
| 25 Oct 2026 | IN029 | Built: hand coded RBI headline inflation projection for 134 decisions (113 with a value; 94 forecasts, 12 stated objectives before 2009, 7 restatements); revision feature added | Second model (D024, D025) |
| 25 Oct 2026 | IN029 | Known limitation: the November 2010 value moves from 6.0 to 5.5 because of the WPI base change, which the revision feature reads as a 0.5 cut | Recorded rather than adjusted, to keep the coding literal |
| 25 Oct 2026 | NP009, NP010, NP012, NP016, NP021 | Built from IMF monetary surveys for Nepal model 2: excess reserves (banks' claims on the NRB over deposits), three month growth of NRB net foreign assets, three month change in government deposits at the NRB over broad money, private credit growth minus deposit growth | Liquidity channel under the peg (D030); NRB site down, IMF carries the same NRB reported data monthly from December 2001 |
| 25 Oct 2026 | NP013 remittances, NP015 balance of payments | Not built separately | NRB net foreign assets already captures remittance and balance of payments inflows monetised under the peg; keeps the feature budget |
| 25 Oct 2026 | nepal_cpi_yoy, india_repo_level | Left out of Nepal model 2 | Liquidity model is about the price of reserves; the India repo enters as its change only, for the transmission test |
