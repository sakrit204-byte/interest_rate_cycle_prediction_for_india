# RBI rate cycle outlook to April 2027, written 28 October 2026

Decision D050. Source: src/simulation/outlook.py, reports/tables/india_outlook_20261028.csv and
india_outlook_paths_20261028.csv. The December 2026 probabilities are recorded here before the
meeting and will be scored after it; the February and April figures are conditional on the
scenarios and are not forecasts in the strict sense.

## Where things stand

On 7 October 2026 the MPC raised the repo rate by 25 basis points to 5.50 percent, the first
hike of a new cycle, and changed its stance to calibrated tightening, saying that the next move
could only be a hike or a pause. CPI inflation then rose to 5.54 percent in September (food 7.7
percent), up every month since January. The RBI projects 5.6 percent for the first quarter of
2027/28. Industrial production grew about 8 percent over the three months to August, well above
its five year average. The next meetings are 2 to 4 December 2026, early February and early
April 2027.

The world outside India over the last week:

* Oil: Brent about 115 dollars, up roughly 12 percent in October, with analysts putting about
  20 dollars of that down to the risk of renewed US strikes on Iran after the 3 November US
  election and to Houthi attacks on Saudi facilities.
* AI equities: a selloff in AI and chip stocks, with the Chinese STAR50 index down 40 percent in
  under four months and the Nasdaq's worst day since July on 14 October.
* United States: the Fed raised rates in September and is expected to hold today and hike again
  in December, which keeps the dollar firm.
* Rupee: close to its record low against the dollar, with the RBI selling reserves.

## How the news enters the model

The model is the economic ordered probit that was tested on the 2021 to 2026 blind window
(balanced accuracy 0.69), refitted on all 146 decisions with a known outcome. It is not changed.
D040 and D042 showed that adding news or geopolitical indices to it makes it worse, so the news
enters only through the inputs the RBI itself reacts to:

* oil through the RBI's own sensitivity (crude 10 percent above baseline: inflation about 0.3
  points higher, growth about 0.2 points lower), measured from about 105 dollars, the level at
  the October decision;
* the AI bust through weaker world demand (lower growth, softer goods prices) and a weaker rupee
  while portfolio money leaves;
* each meeting's decision feeds the next one through the previous decision, so every scenario
  gives a full probability tree of repo paths.

| Scenario | Story | Brent | CPI at the three cutoffs | Growth gap | Rupee move, 3 months |
|---|---|---|---|---|---|
| Premium persists | no new shock, oil stays high through the winter | 112 | 5.7, 5.6, 5.7 | 2.4, 1.8, 1.2 | 1 percent weaker |
| Escalation | US strikes on Iran after the election | 135 | 5.9, 6.1, 6.4 | 2.2, 1.2, 0.4 | 3, 2, 1 percent weaker |
| Easing tensions | no strikes, the war premium unwinds | 92 | 5.5, 5.2, 5.1 | 2.6, 2.3, 2.0 | 1 percent stronger, then flat |
| AI bust | AI selloff becomes a global risk off and slowdown | 90 | 5.5, 5.0, 4.7 | 1.7, minus 0.1, minus 0.9 | 3, 2, 0 percent weaker |
| Stagflation | AI bust and Gulf escalation together | 125 | 5.8, 5.8, 5.9 | 1.3, minus 0.5, minus 1.8 | 5, 3, 1 percent weaker |

## Results

Probability of each decision at each meeting (paths chained):

| Scenario | December 2026: hike, hold, cut | February 2027: hike, hold, cut | April 2027: hike, hold, cut | Expected repo after April |
|---|---|---|---|---|
| Premium persists | 0.57, 0.42, 0.01 | 0.35, 0.57, 0.08 | 0.21, 0.62, 0.17 | 5.71 |
| Escalation | 0.56, 0.43, 0.01 | 0.56, 0.41, 0.02 | 0.26, 0.62, 0.12 | 5.81 |
| Easing tensions | 0.57, 0.42, 0.01 | 0.19, 0.64, 0.17 | 0.16, 0.62, 0.22 | 5.63 |
| AI bust | 0.55, 0.44, 0.01 | 0.16, 0.64, 0.21 | 0.10, 0.59, 0.31 | 5.57 |
| Stagflation | 0.55, 0.44, 0.01 | 0.45, 0.51, 0.05 | 0.20, 0.63, 0.18 | 5.74 |

Repo rate after the April 2027 meeting, probability:

| Repo | Premium persists | Escalation | Easing tensions | AI bust | Stagflation |
|---|---|---|---|---|---|
| 5.00 or lower | 0.04 | 0.02 | 0.08 | 0.11 | 0.03 |
| 5.25 | 0.10 | 0.07 | 0.13 | 0.15 | 0.10 |
| 5.50 | 0.27 | 0.22 | 0.27 | 0.29 | 0.26 |
| 5.75 | 0.26 | 0.22 | 0.30 | 0.28 | 0.23 |
| 6.00 | 0.21 | 0.31 | 0.14 | 0.12 | 0.26 |
| 6.25 | 0.12 | 0.17 | 0.07 | 0.05 | 0.12 |

No input in any scenario lies outside the range seen in the 146 past decisions.

## Economic reading

**December is decided mostly by what is already known.** In every scenario the chance of a
second hike in December is 0.55 to 0.57. The RBI will see October inflation near 5.5 to 5.9
percent, its own projection of 5.6 percent, which it raised by 0.3 points in October, strong
industrial growth and a recent hike. Central banks smooth: in the 146 past decisions a hike was
followed by another hike 71 percent of the time. Oil and the AI selloff cannot move much in five
weeks because the inflation print the RBI will see in December was largely set before them.

**The scenarios split from February, and they split on the inflation versus growth trade off.**
If the oil premium persists or the Gulf escalates, inflation stays above the projection and the
cycle runs to 6.00 or 6.25 percent (probability 0.33 if the premium persists, 0.48 in escalation). If the war premium
unwinds or the AI selloff turns into a world slowdown, falling oil lowers inflation and the
growth gap closes, so the cycle ends at one or two hikes. The AI bust gives the lowest expected repo in April, 5.57
percent, and the highest chance (0.26) that the repo is below today's level by then.

**Stagflation is the hardest case for the RBI.** Dear oil and a weak rupee argue for hikes, a
negative growth gap argues against. The model resolves it as one or two more hikes and then a hold.

**What the model cannot see.** It reads numbers, not words. The RBI has said cuts are off the
table, but the model still gives cuts a 0.12 to 0.31 chance by April in some scenarios because,
historically, falling inflation and a closing growth gap were followed by cuts. Read those cut
probabilities as holds. In the 2022 to 2023 cycle the same model gave hikes 0.84 and 0.72 at the
first meetings after a hike and then about 0.45 while the RBI kept hiking, so it tends to call
the end of a cycle early. If it errs here it will most likely be by too few hikes.

**Answer to the question.** The new cycle most likely continues with one more hike, in December
or February, to 5.75 percent. A second further hike to 6.00 percent needs oil to stay above about
110 dollars or the Gulf to escalate. An AI driven world slowdown is the main force that would
end the cycle at 5.50 or 5.75 percent.

## What it means for Nepal

The rupee is pegged at 1.6 to the Indian rupee, so every weakening of the Indian rupee against
the dollar is a weakening of the Nepali rupee too, and imported oil and goods from India pass
straight into Nepali prices.

Through interest rates the effect is small. The estimated response of Nepali rates to a 25 basis
point RBI hike (local projections, D032) is close to zero and not significant at any horizon up
to six months (interbank rate minus 0.15 points at three months, band minus 0.50 to 0.20). The
corridor analysis (D049) explains why: the Nepali interbank rate has sat at the NRB floor of
2.75 percent for 34 months with surplus reserves and the NRB absorbing liquidity, so it moves only
when the NRB moves the floor or when liquidity dries up.

The scenario that could change that is Gulf escalation. Remittances, now 29 percent of broad
money a year, come largely from workers in the Gulf. While oil is high the Gulf economies pay
well and remittances rise, which keeps Nepal at the floor. A war that disrupts work in Saudi
Arabia or the other Gulf states would cut that inflow, and with credit demand weak the surplus
would shrink only slowly; a rise off the floor within six months would need a large and lasting
fall in remittances. The frozen Nepal model's most recent sealed forecast (origin July 2026,
three months ahead) gives a rise of more than half a point a 0.29 chance and a fall a 0.24
chance.

## Sources

RBI policy and outlook: SCC Online on the October 2026 decision; RBI press release on the next
MPC dates. Inflation: CNBC on the September 2026 CPI. Oil: The National and CNBC, 26 to 28
October 2026. AI selloff: CNN, 15 October 2026, and Reuters via US News, 26 October 2026. Fed:
CNBC, 26 October 2026. Rupee: BusinessToday, 8 October 2026. Oil sensitivity: RBI Monetary
Policy Report, October 2021, as reported by Business Standard. Links:

* https://www.scconline.com/blog/post/2026/10/09/rbi-hikes-repo-rate-to-5-50-percent-october-2026/
* https://www.rbi.org.in/scripts/BS_PressReleaseDisplay.aspx?prid=63742
* https://www.cnbc.com/2026/10/12/india-inflation-oil-energy-iran-war.html
* https://www.thenationalnews.com/business/energy/2026/10/28/oil-prices-up-due-to-houthi-strikes-and-us-threat-to-renew-iran-war/
* https://www.cnbc.com/2026/10/28/oil-price-today-wti-brent-hormuz.html
* https://www.cnn.com/2026/10/15/business/tech-selloff-nasdaq-ai-intl
* https://money.usnews.com/investing/news/articles/2026-10-26/analysis-in-china-the-ai-bubble-has-already-burst
* https://www.cnbc.com/2026/10/26/fed-decision-expectations-october-meeting.html
* https://www.businesstoday.in/latest/economy/story/rupee-near-record-low-why-rbis-multiple-defences-are-losing-effectiveness-560381-2026-10-08
* https://www.business-standard.com/amp/podcast/markets/rbi-monetary-policy-october-2021-report-10-key-takeaways-121101100405_1.html
