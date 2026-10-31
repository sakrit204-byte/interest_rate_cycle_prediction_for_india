"""Two year RBI outlook, December 2026 to October 2028, with the implied NRB path (decision D057).

Extends the six month outlook of D050 (src/simulation/outlook.py) to twelve meetings with the same
frozen economic ordered probit, the same five scenarios and the same chained probability tree.
The first three meetings use the D050 inputs unchanged. From June 2027 the inputs follow the
assumptions declared in D057:

* neutral inflation converges to 4.7 percent (India's CPI average, November 2021 to October 2026)
  and the growth gap to zero, each closing half the remaining distance every two meetings;
* the oil effect on twelve month inflation and growth drops out from December 2027, twelve
  months after the shock (a base effect), because oil is held at a level, not rising further;
* demand effects of the AI bust and stagflation scenarios fade by half every two meetings;
* rupee depreciation returns to 1 percent per three months;
* the RBI projection equals the scenario inflation path two meetings ahead;
* policy feedback: in each branch inflation is 0.4 point lower per point of repo above 5.50.

Nepal: the NRB bank rate implied by the D056 response, 5.75 plus 0.49 times the change in the
expected repo from 5.25, with the 0.14 and 0.85 bounds as the range. An implication, not a forecast.

Outputs: reports/tables/india_outlook_2y_20261031.csv (scenario and meeting),
         reports/tables/india_outlook_2y_paths_20261031.csv (repo rate distribution in October 2028)
Usage: python -m src.simulation.outlook_two_year
"""

from __future__ import annotations

import sys

import numpy as np
import pandas as pd

from src.simulation import outlook as ol
from src.simulation import scenarios as sc

STAMP = "20261031"
MEETINGS = ol.MEETINGS + ["2027-06-04", "2027-08-06", "2027-10-06", "2027-12-08", "2028-02-04",
                          "2028-04-07", "2028-06-06", "2028-08-04", "2028-10-06"]
LONG_INFL, HALF_LIFE = 4.7, 2  # meetings
OIL_DROPS_OUT = "2027-12-08"
FEEDBACK, FEEDBACK_FROM, FEEDBACK_BASE = 0.4, 3, 5.50
NRB_NOW, REPO_BEFORE, NRB_RESPONSE = 5.75, 5.25, {"low": 0.14, "mid": 0.49, "high": 0.85}


def inputs(name: str) -> list[dict]:
    """Model inputs at each meeting, before the branch's previous decision, repo and feedback."""
    s = ol.SCENARIOS[name]
    gap = (s["oil"] / ol.OIL_BASE - 1) * 100
    first = ol.inputs(name)
    decay = 0.5 ** (1 / HALF_LIFE)
    path, growth, d_infl, d_growth = [], [], s["demand_infl"][-1], s["demand_growth"][-1]
    infl_neutral, growth_neutral = ol.NEUTRAL["infl"][-1], ol.NEUTRAL["growth_gap"][-1]
    for m in MEETINGS[3:]:
        infl_neutral = LONG_INFL + (infl_neutral - LONG_INFL) * decay
        growth_neutral *= decay
        d_infl, d_growth = d_infl * decay, d_growth * decay
        oil = 0.0 if m >= OIL_DROPS_OUT else 1.0
        path.append(infl_neutral + ol.OIL_INFL * gap * oil + d_infl)
        growth.append(growth_neutral + ol.OIL_IIP * gap * oil + d_growth)
    full = [r["infl"] for r in first] + path
    rows, proj = first, first[-1]["proj_infl"]
    for i, m in enumerate(MEETINGS[3:], start=3):
        new = full[min(i + 2, len(full) - 1)]
        rows.append({"meeting": m, "cpi_month": "", "infl": full[i], "proj_infl": new, "proj_revision": new - proj,
                     "growth_gap": growth[i - 3], "inr_depr_3m": 1.0, "anchor": 4.0})
        proj = new
    return rows


def tree(model: ol.Probit, name: str) -> tuple[list[dict], pd.Series]:
    branches = {(1, 5.50): 1.0}  # previous decision hike, repo 5.50 after 7 October 2026
    out = []
    for i, row in enumerate(inputs(name)):
        nxt, p_meeting, flags = {}, np.zeros(3), set()
        for (prev, repo), w in branches.items():
            x = {**{k: row[k] for k in sc.INPUTS if k in row}, "prev_decision": prev, "repo_level": repo}
            if i >= FEEDBACK_FROM:
                x["infl"] = row["infl"] - FEEDBACK * (repo - FEEDBACK_BASE)
            flags |= set(sc.extrapolation(sc.derived(x), model.hist))
            p = model.proba(x)
            p_meeting += w * p
            for k, cls in enumerate((-1, 0, 1)):
                key = (cls, round(repo + cls * ol.STEP, 2))
                nxt[key] = nxt.get(key, 0.0) + w * p[k]
        branches = nxt
        dist = pd.Series(dtype=float)
        for (_, repo), w in branches.items():
            dist[repo] = dist.get(repo, 0.0) + w
        dist = dist.sort_index()
        cum = dist.cumsum()
        expected = float((dist.index.to_numpy() * dist.to_numpy()).sum())
        rec = {"scenario": name, "meeting": row["meeting"], "infl_input": row["infl"], "proj_infl": row["proj_infl"],
               "growth_gap": row["growth_gap"], "p_cut": p_meeting[0], "p_hold": p_meeting[1], "p_hike": p_meeting[2],
               "expected_repo_after": expected, "repo_p10": float(cum[cum >= 0.1].index[0]),
               "repo_median": float(cum[cum >= 0.5].index[0]), "repo_p90": float(cum[cum >= 0.9].index[0]),
               "extrapolated_inputs": ";".join(sorted(flags))}
        for k, b in NRB_RESPONSE.items():
            rec[f"nrb_bank_rate_{k}"] = NRB_NOW + b * (expected - REPO_BEFORE)
        out.append(rec)
    return out, dist


def main() -> int:
    hist = sc.history()
    model = ol.Probit(hist)
    rows, paths = [], []
    for name in ol.SCENARIOS:
        r, dist = tree(model, name)
        rows += r
        paths.append(dist.rename(name))
    table = pd.DataFrame(rows).round(3)
    dist = pd.concat(paths, axis=1).fillna(0).round(3)
    dist.index.name = "repo_after_october_2028"
    table.to_csv(ol.TABLES / f"india_outlook_2y_{STAMP}.csv", index=False)
    dist.to_csv(ol.TABLES / f"india_outlook_2y_paths_{STAMP}.csv")
    pd.set_option("display.width", 250)
    print(table[["scenario", "meeting", "infl_input", "proj_infl", "p_cut", "p_hike", "expected_repo_after",
                 "repo_p10", "repo_median", "repo_p90", "nrb_bank_rate_mid", "extrapolated_inputs"]].to_string(index=False))
    print(dist.to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
