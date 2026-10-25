# Research Decision Log

Each entry records a methodological decision, the alternatives considered, and the reason. Entries are never deleted; a reversed decision gets a new entry.

| ID | Date | Decision | Alternatives | Reason |
|---|---|---|---|---|
| D001 | 25 Oct 2026 | Blind window starts 1 November 2021; training information cutoff 31 October 2021 | Last 3 years; last 7 years | User requirement of five years; window appears to contain tightening, hold and easing phases |
| D002 | 25 Oct 2026 | India target is the LAF repo rate decision in three classes, with magnitude as secondary | Call rate only; binary change | Official signal rate; three classes kept unless minority class counts fall below 15 in training |
| D003 | 25 Oct 2026 | Nepal training target is the monthly interbank rate change plus a hand coded stance index; policy rate decisions used for evaluation | Policy rate classifier only | Policy rate era is about six years and almost entirely inside the blind window |
| D004 | 25 Oct 2026 | Main forecast cutoff is seven days before announcement, stress tested at 1 and 30 days | Day before only | Realistic forecaster information set; tests sensitivity |
| D005 | 25 Oct 2026 | Suggestions combine a learned classifier, an estimated inertial Taylor type rule, and a textbook rule as benchmark | Classifier only | Disagreement between learned and rule based signals is informative and guards against overfitting |
| D006 | 25 Oct 2026 | Political events are hand coded from primary sources; no LLM in the core pipeline | Automated news classification | Zero cost, reproducibility, and the expected small number of consequential events |
| D007 | 25 Oct 2026 | Documentation avoids hyphens and dashes to join words or sentences | None | Project writing convention set by the team |
| D008 | 25 Oct 2026 | Working defaults adopted for open questions: class report built to publication standard; Nepal interbank target; seven day cutoff; automated downloads where allowed; self audit of event coding until a second coder is named | Waiting for answers | User asked to continue without answering; each default can be overridden |
| D009 | 25 Oct 2026 | RBI published inflation projections become a core India feature; the estimated rule becomes a hybrid of projected and realized inflation | Backward looking rule only | Garga and Sengupta 2026 find the RBI responds to its projections after inflation targeting, and the projections are real time by construction |
| D010 | 25 Oct 2026 | Ordered probit with an inaction band is the primary interpretable model and the benchmark that ML must beat | Multinomial logit as primary | Established in the central bank decision literature; uses the ordering of hike, hold and cut; fewer parameters |
| D011 | 25 Oct 2026 | FIT regime dated from the Monetary Policy Framework Agreement of 20 February 2015, with the MPC era from 2016 as a second regime marker | 2016 only | Garga and Sengupta 2026, Section 2 |
