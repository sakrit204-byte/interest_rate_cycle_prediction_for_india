# RateCycle India Nepal: Implementation Plan

Version 0.1, prepared 25 October 2026. Status: plan only. No data has been downloaded, no model has been trained, and no result in this document is an empirical finding.

Writing convention for all project documentation: no hyphen or dash is used to join words or sentences. Compound terms are written as separate words (for example "out of sample", "walk forward", "time series"). Hyphens appear only where a technical format demands them, such as Markdown table syntax, ISO dates inside data files, or code.

## 1. What the project is actually asking

The core question is whether the historical behaviour of the Reserve Bank of India (RBI) and Nepal Rastra Bank (NRB) can be learned from information that was public at the time of each decision, and whether a model trained on that history, with the most recent five years hidden from it, would have suggested the policy direction the central banks then chose.

That breaks into four separable claims, each with its own standard of evidence:

| Claim type | Question | Evidence standard |
|---|---|---|
| Prediction | Given what was public before a meeting, can we predict hike, hold or cut? | Out of sample accuracy against naive baselines, on a sealed test window |
| Prescription | What direction does an explicit, documented policy rule recommend? | Internal consistency of the rule; agreement with actual decisions is descriptive, not proof of optimality |
| Causal inference | What does a monetary policy shock do to inflation, output and credit? | Identified shocks (for example high frequency surprises), local projections, stated assumptions |
| Simulation | What paths follow under a hike, hold or cut, conditional on assumptions? | Only as good as the estimated responses; always labelled conditional |

A model that matches RBI decisions well tells us it has learned the RBI reaction function. It does not tell us the RBI was right, and it does not tell us what a rate hike does to inflation. The plan keeps these apart at every layer, including the UI.

## 2. Practicality assessment

### 2.1 Verdict

The India arm is practical at zero cost. The Nepal arm is practical for descriptive, rule based and econometric work but is too sparse for a standalone machine learning classifier of policy decisions. The political event arm is practical only as a small, hand coded, carefully dated dataset. The five year blind test is practical for India and partially practical for Nepal.

### 2.2 India

* The RBI has used the repo rate under the Liquidity Adjustment Facility as its signal rate since the early 2000s. The Monetary Policy Committee (MPC) began in October 2016 and normally meets six times a year.
* Expected decision count: roughly 60 MPC decisions from October 2016 to October 2026, plus pre MPC policy reviews and several inter meeting moves from 2001 to 2016. A rough total of 120 to 150 dated decisions is plausible but must be counted from RBI press releases in Step 2.
* Class imbalance is the central risk. Holds dominate; hikes and cuts arrive in clusters. Clusters mean consecutive decisions are not independent, so the effective sample size is much smaller than the raw count.
* Structural break: flexible inflation targeting was adopted through the Monetary Policy Framework Agreement of 20 February 2015 and given a statutory basis by the 2016 amendment of the RBI Act, which also created the MPC (source: Garga and Sengupta 2026, Section 2). Decisions before that were made under a multiple indicator approach dating from April 1998. Training on both periods without a regime indicator risks learning a reaction function the RBI no longer uses.
* Forward looking behaviour: Garga and Sengupta (2026) find that backward looking Taylor rules show no robust response to realized inflation after inflation targeting, while the RBI's own published inflation projections do show a significant response, and a hybrid rule fits best. The RBI's projections, published in each policy statement, are therefore a core feature. They are public at the decision date by construction, which also avoids revised data problems.
* Statistical break inside the test window: MoSPI released a new CPI series with base 2024 = 100 in February 2026, replacing base 2012 = 100, with a linking factor. Any inflation feature spanning 2026 must use the linked series and document the splice.
* Free data looks adequate: RBI DBIE, MoSPI eSankhyiki (which advertises API access), FRED (which redistributes the India Economic Policy Uncertainty index and several Indian series), IMF and World Bank portals.
* A public RBI monetary policy shock series exists: Lakdawala and Sengupta (2021), "Measuring monetary policy shocks in emerging economies: Evidence from India", IGIDR Working Paper 2021 021. Shocks come from daily changes in OIS rates from one month to one year around 115 RBI announcement dates, September 2003 to December 2020, cross checked against a narrative reading of statements and press coverage. The authors state the shocks and dates are public; licence terms are still to be checked. The series ends before the test window, which matters for the causal arm but not for the prediction arm. Its list of announcement dates also gives an independent check on our decision list.

### 2.3 Nepal

* NRB issues one annual Monetary Policy statement (around the start of the Nepali fiscal year in mid July) and reviews it quarterly. That gives at most four decision points a year.
* An interest rate corridor has operated since about 2016, initially without a named policy rate; a full corridor with a policy rate appears to date from about 2020. Before that, the bank rate and reserve requirements were the main signals. Exact dates must be confirmed from NRB documents in Step 2.
* Consequence: a policy rate decision target exists for only about six years, which is roughly 24 decision points, nearly all of which fall inside the five year blind window. There is essentially nothing left to train on.
* Smallest defensible alternatives for Nepal, in priority order:
  1. A monthly continuous target: the interbank rate or the weighted average lending rate, which NRB publishes in its Current Macroeconomic and Financial Situation reports.
  2. A longer, coarser stance target built from the bank rate, CRR and corridor changes, coded with an explicit rule and audited by hand.
  3. A rule based and transmission based assessment (does RBI stance help predict the Nepali interbank rate?) rather than a classifier.
* The NPR has been pegged to the INR at 1.6 since 1993. An NRB working paper (Budha, 2015) reports long run price level convergence with India alongside substantial monetary policy independence. This is the right starting point for RQ3 and RQ4: the peg constrains, but it does not mechanically dictate, NRB decisions.

### 2.4 Political events

* No free, curated, monetary relevant political event dataset for both countries was found during scoping. It must be built by hand from primary sources: the Election Commission of India, the Election Commission Nepal, parliamentary records, Union and Nepal budget documents, and reputable news archives.
* Feasible scale: tens of high consequence events per country, not thousands. Recent Nepali events that are candidates for coding (government changes, the September 2025 protests and the subsequent interim government, the 2026 election) must each be verified from primary sources before they enter the dataset.
* A complementary, already constructed measure exists for India: the Baker, Bloom and Davis Economic Policy Uncertainty index (monthly, on FRED as INDEPUINDXM). No equivalent exists for Nepal, which is itself a documented limitation.
* With so few events, any claim that political features improve prediction will be fragile. The plan treats RQ2 as a hypothesis test with a high bar and a preregistered rule for what counts as improvement.

### 2.5 The five year blind test

* Blind window: 1 November 2021 to the latest available decision (as of 25 October 2026). Training and all model selection use only information published on or before 31 October 2021.
* For India the window appears to contain a tightening phase, a long hold and an easing phase, which makes it a demanding and informative test. The exact decision list will be built from RBI press releases, not assumed.
* The training window includes only five years of the MPC regime (October 2016 to October 2021), and that period includes the pandemic. This is a real weakness and is disclosed rather than hidden.
* For Nepal, the blind window covers nearly all of the policy rate era, so the Nepal blind test will compare rule based and transmission based suggestions against NRB actions, not a trained classifier.

## 3. Architecture

```
Source registry  →  Ingestion (India, Nepal, International, Events)  →  data/raw (immutable, checksummed)
      →  Validation  →  data/interim  →  Release aware feature builder  →  data/processed
      →  [Prediction arm]   baselines, ordered logit, regularized logit, random forest
      →  [Prescription arm] estimated reaction function, textbook Taylor rule, peg aware Nepal rule
      →  [Causal arm]       local projections, small VAR, identified shocks
      →  Policy suggestion engine  →  Blind backtest  →  Scenario engine
      →  Streamlit dashboard, reports, manuscript
```

Ten layers as specified in the brief, with one addition: `src/policy/`, which holds the suggestion engine described in Section 6. Each layer reads only from the layer before it and writes only to its own folder.

## 4. Target definitions

### 4.1 India primary target

* Unit of observation: one scheduled or unscheduled RBI monetary policy decision.
* Rate: repo rate under the LAF. Reverse repo, SDF, MSF and CRR changes are recorded as separate fields and never relabelled as repo decisions.
* Classes: hike (change greater than 0), hold (change of 0), cut (change less than 0). Magnitude in basis points is stored as a secondary target.
* Forecast cutoff: the close of business seven calendar days before the decision announcement. Every feature must have been published before that cutoff. The seven day gap is a design choice to be stress tested at 1, 7 and 30 days.
* Inter meeting moves are kept and flagged; a robustness run excludes them.

### 4.2 India secondary targets

* Stance language (accommodative, neutral, withdrawal of accommodation, and so on), coded from the published statement, as a leading indicator of direction.
* Next 3 month change in the weighted average call rate as a continuous measure of the operating target.

### 4.3 Nepal targets

* Primary (policy era only): direction of the policy rate at each annual statement or quarterly review.
* Feasible training target: monthly change in the interbank rate, and a hand coded stance index from bank rate, corridor and CRR changes.
* Every NRB decision where several instruments move together is coded with a documented rule in `docs/target_coding_rules.md` (Step 2 deliverable).

### 4.4 Sample size rules

* Events per parameter: no model may have more free parameters than one tenth of the count of its smallest class in training. With, for example, 20 hikes in training, the model gets at most two free slopes unless regularized and justified.
* If the smallest class has fewer than 15 training examples, three class classification is replaced by an ordered model or a binary "change versus hold" plus "direction given change" structure, and this is reported.

## 5. Methodology for overfitting and underfitting

Small samples, clustered decisions and regime changes make overfitting the dominant risk. Underfitting matters too, because a model that only ever predicts "hold" can score high accuracy while being useless.

### 5.1 Controls against overfitting

| Control | What it does here |
|---|---|
| Sealed test window | The five year blind window is never touched during development. A configuration file and its SHA256 hash are committed before the blind window is unlocked, acting as a preregistration. |
| Walk forward validation | Inside the training period, models are fitted on an expanding window and evaluated on the next block of decisions. No random shuffling ever. |
| Embargo gap | A gap of one decision between training and validation folds so autocorrelated features do not leak across the boundary. |
| Nested selection | Hyperparameters are chosen in an inner walk forward loop; the outer loop only reports. |
| Small feature budget | A core set of about six to eight economically motivated features, fixed before modelling (RBI projected inflation gap, realized inflation gap, output or IIP gap, lagged rate change, call rate spread, USD/INR change, oil price change, global rate). Extra features must earn their place in an ablation. |
| Established benchmark model | An ordered probit with an inaction band (the policy rate moves only when the desired change crosses a threshold) is the primary interpretable model, following the ordered choice literature on central bank decisions (Kim for Korea; Chevapatrakul, Kim and Mizen for the UK; Sirchenko for the Federal Reserve, all to be read in full). Machine learning models must beat it, not only the naive baselines. |
| Regularization | L2 and elastic net logistic regression; ordered logit with shrinkage; random forest limited in depth and leaf size. |
| One standard error rule | Among models within one standard error of the best validation score, the simplest is chosen. |
| Learning curves | Training versus validation score as training size grows. A large persistent gap is overfitting. |
| Permutation test of the target | Shuffle labels within blocks; a model that still "performs" on shuffled labels is learning artefacts. |
| Forecast comparison tests | Diebold Mariano or Giacomini White tests on loss differences, and block bootstrap intervals on metric differences, so improvements are judged against noise. |
| Feature stability | Coefficient signs and permutation importances are tracked across folds; unstable rankings are reported, not hidden. |
| Probability calibration | Reliability curves and Brier score where class counts allow. |

### 5.2 Controls against underfitting

| Control | What it does here |
|---|---|
| Strong naive baselines | Persistence (last decision repeats), majority class, and a simple inflation threshold rule. A model must beat all three. |
| Balanced metrics | Balanced accuracy, macro F1 and Cohen's kappa instead of raw accuracy, so "always hold" is exposed. |
| Learning curves | Low training and low validation scores together signal underfitting. |
| Residual and error analysis | Inspect which decisions are missed (turning points versus continuations). |
| Controlled complexity ladder | Baseline, then logistic, then ordered logit, then random forest, each added only if the previous rung clearly underfits. |
| Class weighting | Balanced class weights so minority classes are not ignored. |

### 5.3 Leakage controls

* Every observation carries a publication date as well as a reference period. Features are joined on publication date, not reference month. CPI for September, for example, is unusable for a decision before its release in October.
* Where real time vintages exist (some FRED ALFRED series, RBI and MoSPI archived releases), they are used; otherwise the use of revised data is disclosed as a limitation.
* Political events are joined on announcement timestamp, never occurrence date.
* Automated tests assert that no feature timestamp exceeds its decision cutoff.

## 6. How policy direction suggestions are generated

The suggestion engine produces, for every historical decision date, a suggested direction (hike, hold, cut), a confidence level, and a short list of reason codes. It combines three independent sources so that disagreement is visible.

1. **Learned reaction function (positive).** The best validated classifier gives probabilities for hike, hold and cut. This answers "what would the RBI or NRB of the training period have done?"
2. **Estimated policy rule (positive, interpretable).** An inertial hybrid Taylor type rule estimated on training data: target rate equals a smoothing term times the lagged rate, plus responses to the RBI projected inflation gap, the realized inflation gap and the output gap, plus, for Nepal, the Indian policy rate and reserve adequacy as peg relevant terms. The gap between the prescribed rate and the current rate, passed through a deadband of 12.5 basis points either side, gives the direction.
3. **Textbook benchmark rule (normative).** A standard Taylor rule with conventional weights and India's 4 percent CPI target. It is reported as a reference point, never as the "correct" policy.

Combination rule (fixed before unblinding): the suggestion is the classifier's most probable class when its top probability exceeds 0.5 and the estimated rule agrees; otherwise the engine reports "uncertain" with both signals shown. Reason codes come from the sign and size of each rule term and from held out permutation importance.

Evaluation of agreement with actual decisions in the blind window:

* Hit rate, balanced accuracy, macro F1, Cohen's kappa and a confusion matrix.
* Turning point analysis: did the suggestion turn before, with, or after the central bank at the start of each tightening and easing cycle, measured in meetings.
* Direction of error: whether the engine was systematically more hawkish or dovish than the MPC.
* Interpretation rule: agreement means the model learned the reaction function; disagreement is analysed as either model failure or a change in the reaction function, with evidence for each.

### 6.1 Required chart: blind backtest

One main figure, generated by script, shown in the dashboard and the report:

* Top panel: actual policy rate as a step line, with the blind window shaded and labelled "sealed test period".
* Markers at each decision: actual decision symbol, suggested decision colour, and a ring on every mismatch.
* Middle panel: stacked area of predicted probabilities for hike, hold and cut.
* Bottom panel: prescribed rate from the estimated rule and the textbook rule with bootstrap bands, against the actual rate.
* Companion figures: confusion matrix, rolling balanced accuracy, and turning point lead or lag bars.

## 7. Variables considered from every direction

The full ledger lives in `data/source_registry/variable_registry.csv` and is explained in `docs/variable_log.md`. Every variable is recorded with its status (core, candidate, robustness only, excluded, or pending feasibility) and the reason. Families considered:

| Family | India examples | Nepal examples | Why it matters |
|---|---|---|---|
| Policy instruments | Repo, reverse repo, SDF, MSF, CRR, stance | Policy rate, bank rate, deposit collection rate, CRR | Target and lagged policy |
| Money markets | Weighted call rate, TREPS, 91 day T bill | Interbank rate, T bill rates | Operating target and market expectations |
| Prices | CPI headline, food, fuel, core, WPI | CPI headline, food, non food, India CPI | Inflation targeting and imported inflation |
| Expectations | RBI published inflation and growth projections in each policy statement, household inflation expectations survey, professional forecasters survey | None regular; documented gap | Forward looking policy |
| Activity | GDP, IIP, PMI (access to check), GST collections, auto sales | GDP (annual, some quarterly), production proxies | Output gap |
| Credit and banking | Bank credit growth, deposit growth, NPAs | Private sector credit, deposits, credit to deposit ratio | Transmission and financial stability |
| External | USD/INR, reserves, current account, FPI flows | INR peg rate, reserves in months of imports, remittances, imports from India, BOP | Exchange rate pressure and peg sustainability |
| Global | Fed funds, US 10 year yield, dollar index, VIX, Brent | Same, through India | Spillovers |
| Fiscal | Fiscal deficit, borrowing calendar, budget dates | Budget execution, capital spending, domestic borrowing | Fiscal dominance and liquidity |
| Supply and weather | Monsoon rainfall departure (IMD), food supply shocks | Monsoon, agricultural output | Food inflation drives headline in both |
| Political and policy events | Elections, budgets, major reforms, EPU index | Government changes, protests, elections, budgets | RQ2 |
| Cross border | RBI stance as a Nepal feature, interest differential, India Nepal trade | Same | RQ3 and RQ4 |

The ledger also records what was left out and why, for example: high frequency equity data (no clear policy channel at decision frequency), news sentiment from paid APIs (budget constraint), and Nepal monthly GDP proxies (no consistent official series confirmed yet).

## 8. Possible research expansions

These are candidate directions, each needing its own feasibility check. None is claimed novel until the literature review is complete.

* Text measures of RBI and NRB statements (dictionary based hawkish and dovish scores, fully local, no paid LLM) as features and as a stance target.
* Monsoon and food supply shocks as a regime variable linking climate to monetary policy in both countries.
* Peg stress indicators for Nepal: reserves cover, interest differential with India, and remittance flows, and whether NRB responds to these more than to domestic inflation.
* Reaction function stability: rolling or regime switching estimates showing whether the RBI reaction function changed after 2016 and again after 2022.
* Global spillover channel: does the Federal Reserve cycle add predictive information for RBI beyond domestic inflation?
* Inflation forecasting as a separate task, which also feeds the scenario engine.

## 9. Dashboard (Streamlit, local)

Pages:

1. Overview: research questions, status of each gate, clear labelling legend (observed, predicted, simulated, synthetic).
2. Data explorer: India and Nepal series with source links and publication lags.
3. Variable ledger: searchable table of every variable with status and reason.
4. Event timeline: political and policy events with sources and verification status.
5. Models: evaluation tables, confusion matrices, learning curves, calibration.
6. Blind backtest: the Section 6.1 chart and turning point analysis.
7. Transmission: India and Nepal comovement, rate differentials, peg indicators, impulse responses.
8. Scenarios: user chosen rate paths and shocks; outputs clearly labelled conditional, with extrapolation flags.
9. Methods and limitations: model cards, decision log, failed experiments.

Plotly will be added for interactive charts (free, open source); matplotlib generates static publication figures.

## 10. Step sequence and gates

| Step | Deliverable | Gate before moving on |
|---|---|---|
| 1 Scoping and literature | Protocol, literature review, matrix, novelty assessment | No novelty claim before review is complete |
| 2 Data feasibility | Source registry, variable ledger populated with verified coverage, decision counts, sample size report | Targets defined and decision counts verified |
| 3 Environment | Pinned requirements, configs, logging, synthetic test data, first tests | Tests pass |
| 4 Economic ingestion | Ingestion modules, raw manifests, checksums | Sample observations checked against source |
| 5 Political events | Event CSV, coding guide, quality report | Every event traceable |
| 6 Features | Release aware features, data quality report, EDA | Leakage tests pass |
| 7 Baselines | Baselines and logistic models, walk forward results | Beat naive baselines or report failure |
| 8 Ablations | Political and cross country ablations | Improvement survives tests |
| 9 Transmission | Peg documentation, comovement and predictive tests | No causal language from correlation |
| 10 Econometrics | Local projections, VAR, identification document | Identification defensible or claims restricted |
| 11 Suggestion engine and blind test | Engine, preregistered config hash, unblinded backtest | Config committed before unblinding |
| 12 Scenarios | Scenario engine and tests | Assumptions labelled |
| 13 Dashboard | Streamlit app | No synthetic data shown as real |
| 14 Robustness and paper | Robustness report, manuscript | Every number traceable |

The suggestion engine and blind test are placed after the econometrics so that the estimated rule is available, but the blind window stays sealed throughout Steps 6 to 10.

## 11. Step 1 in detail: tasks and acceptance criteria

Tasks:

1. Run the literature search strategy in `docs/literature_review.md` across RBI, NRB, IMF, BIS, NBER, RePEc and Google Scholar.
2. Read, not only list, each candidate paper and record it in `docs/literature_matrix.csv` with question, data, method, findings, limitations and relevance.
3. Verify the access terms and coverage of the Lakdawala and Sengupta RBI shock dataset.
4. Search specifically for prior work on India to Nepal policy rate spillover and on machine learning for monetary policy decision classification in emerging markets.
5. Write `docs/novelty_assessment.md` separating established knowledge from the proposed contribution.
6. Finalize `docs/research_protocol.md` with hypotheses and the blind test protocol.

Acceptance criteria:

* At least the core strands in the search strategy have been searched, with search strings and dates logged.
* Every matrix row marked "read" has been read in full; rows found only through search are marked "screened".
* The novelty assessment names the closest existing studies and states what, if anything, this project adds.
* No citation in any document lacks a source link or full reference.

## 12. Blockers and working defaults

The open questions below were not yet answered when work continued, so working defaults were adopted (decision log entry D008). Each can be overridden.

| Question | Working default |
|---|---|
| Class report or journal submission? | Class report built to publication standard; Steps 10 and 14 kept but scaled to the evidence |
| Nepal training target | Monthly interbank rate change plus hand coded stance index. NRB describes the weighted average interbank rate as its operating target in the 2025/26 Monetary Policy (per search excerpt; to verify in the document), which supports this choice |
| Prediction cutoff | Seven days before announcement, stress tested at 1 and 30 days |
| Manual downloads | Automated downloads where sites allow them; files you download yourself otherwise |
| Second coder for political events | To be named; until then, a documented self audit of a random sample after a delay |

New blocker found on 25 October 2026: `www.nrb.org.np` and `nrb.org.np` could not be reached from this machine (connection timed out), while FRED and RBI responded normally. Nepal data may need to be downloaded by you from a browser that can reach NRB and placed in `data/raw/nepal/`, or fetched later if the outage is temporary.
