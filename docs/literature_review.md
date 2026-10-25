# Literature Review: Search Strategy and Screening Log

Status: screening started 25 October 2026. Nothing below is yet a reviewed finding. Entries marked "screened" were found through search results and have not been read in full.

## Strands and search strings

| Strand | Search strings | Databases |
|---|---|---|
| A. Predicting central bank decisions | "ordered probit" "monetary policy reaction function"; "machine learning" "interest rate decision" classification; "RBI" "repo rate" forecast | Google Scholar, RePEc, SSRN, RBI working papers |
| B. RBI reaction function and Taylor rules | "Taylor rule" India; "Monetary Policy Committee" India reaction function; "flexible inflation targeting" India | RBI, EPW, Journal of Asian Economics, IMF |
| C. Indian monetary policy shocks | "high frequency" "monetary policy shocks" India; Lakdawala Sengupta RBI shocks | NBER, CAFRAL, RBI, journals |
| D. Nepal monetary policy and the peg | Nepal "monetary policy transmission"; "Indian rupee" peg Nepal; NRB working paper | NRB, IMF Article IV, NepJOL, World Bank |
| E. India to Nepal spillovers | Nepal India "interest rate" pass through; "monetary policy independence" peg small open economy | IMF, NRB, Scholar |
| F. Political uncertainty and monetary policy | "political uncertainty" "monetary policy" emerging; "election" "central bank" "policy rate"; "economic policy uncertainty" India | Scholar, RePEc |
| G. Explainable ML in macroeconomics | SHAP macroeconomic forecasting; "machine learning" central banks | BIS, Bank of England, ECB, Scholar |
| H. Real time data and leakage | "real time data" monetary policy rules; Orphanides real time Taylor rule | Scholar |

## Initial screening log

| Source | Strand | Status | Note |
|---|---|---|---|
| Lakdawala and Sengupta, RBI monetary policy shocks (working paper 2021; journal version cited as 2024) | C | screened | Combines high frequency market data with narrative analysis; public database of RBI policy dates and shocks; sample reported as Sept 2003 to Dec 2020. Access terms to verify. |
| IMF working paper "Still Packing a Punch" (high frequency identification, 16 economies incl. India) | C | screened | Separates target and path surprises. Exact reference to be confirmed. |
| Budha, NRB Working Paper 29 (2015), Monetary Policy Transmission in Nepal | D | screened | Reports long run price convergence to India under the peg with substantial policy independence; SVAR evidence. |
| NRB Working Paper 17 | D | screened | Bank lending channel; tightening reduces lending, heterogeneity by bank size and liquidity. |
| Byanjankar, NRB Working Paper 61 (2025) | D | screened | Local projections and SVAR; pass through from policy rate to base rate immediate but incomplete. |
| Pratap and Sengupta, RBI Working Paper 04/2019 | G | screened | ML inflation forecasting for India; ML generally beats standard models; forecast combination helps. |
| Chakraborty and Joseph (2017), Bank of England Staff Working Paper, Machine learning at central banks | G | screened | Review; ML strong in prediction, causal properties open. |
| SHAP based evaluation of ML models for CBRT policy decisions (Journal of Economic Policy Researches, 2026) | A | screened | Gradient boosting failed to beat majority class baseline in walk forward evaluation. A direct warning for this project. |
| Baker, Bloom and Davis, Economic Policy Uncertainty index for India (FRED INDEPUINDXM) | F | screened | Monthly, newspaper based, normalized to mean 100 before 2011. |
| RBI study, Monetary Policy Transmission in India: Do Global Spillovers Matter? | B, E | screened | Time varying VAR; money and credit market transmission unaffected by global spillovers, debt market affected. |
| Kelly, Pastor and Veronesi (2016), Journal of Finance, political uncertainty and option prices | F | screened | Political uncertainty is priced; not about policy rates. |

## Gaps already visible after screening

* No study was found during screening that estimates how RBI rate changes pass through to NRB policy or Nepali market rates. This is a candidate contribution, not a claimed one, until strands D and E are searched systematically.
* No study was found during screening that applies ML classification to RBI MPC decisions with a sealed out of sample test. A master's thesis forecasting central bank rates with sentiment features exists and must be read.

## Screening round 2 (25 October 2026)

Additional searches were run for strands A, B, D, E, F, H and evaluation methods. New sources are rows L011 to L024 in `docs/literature_matrix.csv`.

Reading status: Garga and Sengupta (2026) was partially read from the PDF (abstract, introduction, background, forward looking specification and data construction). Lakdawala and Sengupta (2021) was read through the authors' Ideas for India summary; the working paper itself was not yet read.

Findings that change the design:

* The RBI's own published inflation projections explain post 2015 decisions better than realized inflation (Garga and Sengupta 2026). These projections become a core feature, and the estimated rule becomes a hybrid rule.
* Ordered choice models with inaction bands are the established benchmark for decision prediction. The primary interpretable model is now an ordered probit, and ML models must beat it.
* The Lakdawala and Sengupta shock series and announcement dates are public (https://sites.google.com/view/rasesite/public-goods/data-on-monetary-policy-shocks-in-india). Licence terms are still unchecked.
* For forecast comparisons, the Diebold Mariano test can be badly sized in small samples. The Harvey, Leybourne and Newbold correction or fixed b methods are needed, and the Giacomini White test suits rolling windows.
* For RBI decisions around elections, only press commentary was found. That is a gap, or a sign that strand F needs a better search.

Access problem: the NRB website could not be reached from this machine on 25 October 2026, so NRB documents in the matrix remain unread.
