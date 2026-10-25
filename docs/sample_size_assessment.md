# Sample Size Assessment

Status: India section verified on 25 October 2026 from data. Nepal section pending (decision table not yet built).

## India: RBI repo rate decisions

Built by `python -m src.features.targets_india` from two independent sources:

* The RBI archive of monetary policy statements (one saved page per fiscal year, 2001/02 to 2026/27), which gives the dates of policy announcements.
* The BIS daily central bank policy rate series for India (official repo rate from 3 April 2001, compiled by the BIS from the RBI), which gives the rate before and after each announcement.

Every BIS rate change from August 2010 onward lines up with an RBI announcement. The 19 changes that match no announcement all fall between April 2001 and July 2010 and are coded as inter meeting moves, for example the crisis cuts of October 2008 to March 2009.

### Decision counts

| Period | Regime | Cuts | Holds | Hikes | Total |
|---|---|---|---|---|---|
| Training (to 31 Oct 2021) | Multiple indicator approach (to 19 Feb 2015) | 18 | 36 | 27 | 81 |
| Training | Inflation targeting before the MPC (20 Feb 2015 to 3 Oct 2016) | 4 | 6 | 0 | 10 |
| Training | MPC (from 4 Oct 2016) | 9 | 20 | 2 | 31 |
| Blind window (from 1 Nov 2021) | MPC | 4 | 20 | 7 | 31 |
| **All** | | **35** | **82** | **36** | **153** |

Included in these counts: 19 inter meeting moves, all before the blind window.

### What this means for the models

1. **Hikes under inflation targeting are almost absent from training.** From February 2015 to October 2021 there are 2 hikes (June and August 2018) against 13 cuts. A model trained only on the inflation targeting era cannot learn what precedes a hike, yet the blind window opens with a six meeting tightening cycle (May 2022 to February 2023). Training must therefore pool regimes, with a regime indicator, and the pooled hike examples come mostly from 2001 to 2014.
2. **The ordered model is required, not just preferred.** An ordered probit uses one set of slopes for the whole hike, hold, cut scale, so the many cuts help identify the response that also drives hikes. A multinomial model would need separate hike parameters estimated from 29 hikes, most of them from a different regime.
3. **The minority class rule is met only by pooling.** The plan requires at least 15 training examples of the smallest class for a three class model. Pooled training has 29 hikes and 31 cuts, so the rule is met. Inflation targeting alone fails it (2 hikes).
4. **Decisions are clustered.** Hikes and cuts come in runs: for example the six hikes of 2022 to 2023 and the five cuts of 2019. Consecutive decisions are not independent, so effective sample size is far below 122 training decisions. Evaluation uses block bootstrap intervals and reports results by cycle, not only per decision.
5. **The blind window is a hard test.** Of its 31 decisions, 20 are holds, so "always hold" scores 65 percent accuracy. This is why balanced accuracy, macro F1 and Cohen's kappa are the primary metrics.
6. **Data quality note for 2001 to 2004.** In the early LAF years the repo rate changed often and by irregular amounts (for example 10 and 40 basis points in March 2003). A robustness run starts the sample in November 2004.

## Nepal

Pending. The archived NRB documents cover annual monetary policies from 2003/04 onward, but since about 2020 the quarterly and mid term reviews exist only in Nepali, in a legacy font. 54 archived files were found to be truncated and need to be fetched again from older captures (see `docs/data_access.md`). The decision table will be built from the English annual policies, whose annex tables report the policy rates set at each review, cross checked against the monthly tables.
