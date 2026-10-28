"""Six month RBI outlook under news based scenarios, with the Nepal implications (decision D050).

The model is the economic ordered probit that was tested on the blind window, fitted once on
all decisions with a known outcome. Nothing is added to it. Each scenario sets only the inputs
the model already uses (CPI inflation known at the cutoff, the RBI projection and its revision,
the growth gap and the three month rupee move) at the next three meetings. The decisions are
chained: at every meeting each branch carries its own previous decision and repo level, so the
output is a probability tree over the paths of the repo rate, not three separate guesses.

How the news becomes inputs (all stated in SCENARIOS and in D050):
* oil: the RBI sensitivity from its October 2021 Monetary Policy Report, crude 10 percent above
  baseline raising inflation by about 0.3 points and lowering growth by about 0.2 points of GDP;
  the baseline is about 105 dollars a barrel, the level around the 7 October decision; IIP growth
  is taken to move twice as much as GDP growth;
* the pass through of oil into the CPI known at a cutoff builds up: 30 percent by the October
  print, 70 percent by December, all of it by February;
* the RBI projection published at a meeting is known at the next one, and is assumed to move by
  the full oil effect plus any demand effect;
* the AI equity bust works through global demand: weaker growth, softer goods prices, a weaker
  rupee while portfolio money leaves.

Outputs: reports/tables/india_outlook_20261028.csv (one row per scenario and meeting),
         reports/tables/india_outlook_paths_20261028.csv (repo rate distribution in April 2027)
Usage: python -m src.simulation.outlook
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.miscmodels.ordinal_model import OrderedModel

from src.models import walk_forward as wf
from src.simulation import scenarios as sc

ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "reports" / "tables"
STAMP = "20261028"
MEETINGS = ["2026-12-04", "2027-02-05", "2027-04-07"]
CPI_MONTH = {"2026-12-04": "Oct 2026", "2027-02-05": "Dec 2026", "2027-04-07": "Feb 2027"}
OIL_BASE = 105.0
OIL_INFL, OIL_IIP = 0.03, -0.04  # points per percent of oil above baseline (RBI MPR, IIP twice GDP)
PASS_THROUGH = [0.3, 0.7, 1.0]
# Path with oil at the baseline: CPI near the RBI projection of 5.6, growth gap easing from +2.9
NEUTRAL = {"infl": [5.6, 5.5, 5.5], "growth_gap": [2.5, 2.0, 1.5]}
KNOWN_DECEMBER = {"proj_infl": 5.6, "proj_revision": 0.3}
SCENARIOS = {
    # oil in dollars a barrel; demand shifts CPI (points) and growth gap (points) per meeting;
    # inr is the three month rupee depreciation in percent at each cutoff
    "premium_persists": {"oil": 112, "demand_infl": [0, 0, 0], "demand_growth": [0, 0, 0], "inr": [1.0, 1.0, 1.0],
                         "story": "Brent stays near 110 to 115 dollars through the winter (UBS view); no new shock"},
    "escalation": {"oil": 135, "demand_infl": [0, 0, 0], "demand_growth": [0, 0, 0], "inr": [3.0, 2.0, 1.0],
                   "story": "US strikes on Iran resume after the 3 November election, Gulf supply disrupted"},
    "de_escalation": {"oil": 92, "demand_infl": [0, 0, 0], "demand_growth": [0, 0, 0], "inr": [-1.0, 0.0, 0.0],
                      "story": "no strikes after the election, the war premium of about 20 dollars unwinds"},
    "ai_bust": {"oil": 90, "demand_infl": [0.0, -0.2, -0.4], "demand_growth": [-1.0, -2.5, -3.0], "inr": [3.0, 2.0, 0.0],
                "story": "the AI equity selloff spreads from China and the Nasdaq into a global risk off and slowdown"},
    "stagflation": {"oil": 125, "demand_infl": [0.0, -0.1, -0.2], "demand_growth": [-1.0, -2.0, -2.5], "inr": [5.0, 3.0, 1.0],
                    "story": "AI bust and Gulf escalation together: dearer oil, weaker world demand, a falling rupee"},
}
STEP = 0.25


def inputs(name: str) -> list[dict]:
    """Model inputs at each meeting, before the previous decision and repo level are set."""
    s = SCENARIOS[name]
    gap = (s["oil"] / OIL_BASE - 1) * 100
    rows, proj = [], KNOWN_DECEMBER["proj_infl"]
    for i, meeting in enumerate(MEETINGS):
        if i == 0:
            proj_infl, revision = KNOWN_DECEMBER["proj_infl"], KNOWN_DECEMBER["proj_revision"]
        else:
            # projection published at the previous meeting: full oil effect plus the demand effect then
            new = KNOWN_DECEMBER["proj_infl"] + OIL_INFL * gap + s["demand_infl"][i - 1]
            proj_infl, revision, proj = new, new - proj, new
        rows.append({"meeting": meeting, "cpi_month": CPI_MONTH[meeting],
                     "infl": NEUTRAL["infl"][i] + OIL_INFL * gap * PASS_THROUGH[i] + s["demand_infl"][i],
                     "proj_infl": proj_infl, "proj_revision": revision,
                     "growth_gap": NEUTRAL["growth_gap"][i] + OIL_IIP * gap * PASS_THROUGH[i] + s["demand_growth"][i],
                     "inr_depr_3m": s["inr"][i], "anchor": 4.0})
    return rows


class Probit:
    """The economic ordered probit fitted once on every decision with a known outcome."""

    def __init__(self, hist: pd.DataFrame):
        self.hist, self.features = hist, wf.ECON_MODEL_FEATURES
        self.mean, self.sd = hist[self.features].mean(), hist[self.features].std(ddof=0)
        x = ((hist[self.features] - self.mean) / self.sd).to_numpy(float)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.res = OrderedModel(hist["y"].to_numpy(), x, distr="probit").fit(method="bfgs", disp=False, maxiter=2000)

    def proba(self, row: dict) -> np.ndarray:
        s = sc.derived(row)
        x = ((s[self.features] - self.mean) / self.sd).to_numpy(float)[None, :]
        return np.asarray(self.res.model.predict(self.res.params, exog=x))[0]


def tree(model: Probit, name: str) -> tuple[list[dict], pd.Series]:
    """Probability of each decision at each meeting, and of each repo level after the last one."""
    branches = {(1, 5.50): 1.0}  # previous decision hike, repo 5.50 after 7 October
    out = []
    hist = model.hist
    for row in inputs(name):
        nxt, p_meeting = {}, np.zeros(3)
        flags = set()
        for (prev, repo), w in branches.items():
            x = {**{k: row[k] for k in sc.INPUTS if k in row}, "prev_decision": prev, "repo_level": repo}
            flags |= set(sc.extrapolation(sc.derived(x), hist))
            p = model.proba(x)
            p_meeting += w * p
            for k, cls in enumerate((-1, 0, 1)):
                key = (cls, round(repo + cls * STEP, 2))
                nxt[key] = nxt.get(key, 0.0) + w * p[k]
        branches = nxt
        repo_dist = pd.Series({}, dtype=float)
        for (_, repo), w in branches.items():
            repo_dist[repo] = repo_dist.get(repo, 0.0) + w
        out.append({"scenario": name, **{k: v for k, v in row.items() if k != "anchor"},
                    "p_cut": p_meeting[0], "p_hold": p_meeting[1], "p_hike": p_meeting[2],
                    "expected_repo_after": float((repo_dist.index.to_numpy() * repo_dist.to_numpy()).sum()),
                    "extrapolated_inputs": ";".join(sorted(flags))})
    return out, repo_dist.sort_index()


def main() -> int:
    hist = sc.history()
    model = Probit(hist)
    rows, paths = [], []
    for name in SCENARIOS:
        r, dist = tree(model, name)
        rows += r
        paths.append(dist.rename(name))
    table = pd.DataFrame(rows).round(3)
    dist = pd.concat(paths, axis=1).fillna(0).round(3)
    dist.index.name = "repo_after_april_2027"
    table.to_csv(TABLES / f"india_outlook_{STAMP}.csv", index=False)
    dist.to_csv(TABLES / f"india_outlook_paths_{STAMP}.csv")
    pd.set_option("display.width", 220)
    print(f"fitted on {len(hist)} decisions, last {hist['date'].iloc[-1]}")
    print(table.drop(columns=["cpi_month"]).to_string(index=False))
    print(dist.to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
