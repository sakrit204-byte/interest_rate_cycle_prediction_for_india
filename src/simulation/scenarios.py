"""Conditional scenarios (Step 12). Every output is conditional on the user's assumptions and
on relationships estimated from history; none is a forecast and none is causal.

India: the user sets the RBI's situation at a meeting (previous decision, revision to its
inflation projection, realized and projected inflation, growth gap, rupee move, current repo,
anchor). The economic ordered probit and the estimated inertial rule, both fitted on every
decision whose outcome is known, return decision probabilities and a prescribed change; the
textbook Taylor rule is shown as a normative reference. Inputs outside the historical range
are flagged as extrapolation.

Nepal: an RBI repo move of a chosen size is passed through the local projection estimates
(D032) to give the conditional path of Nepali variables with 95 percent bands.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import statsmodels.api as sm

from src.models import walk_forward as wf
from src.policy import suggestion_engine as se

ROOT = Path(__file__).resolve().parents[2]
LP = ROOT / "reports" / "tables" / "local_projections.csv"
INPUTS = ["prev_decision", "proj_revision", "infl", "proj_infl", "growth_gap", "inr_depr_3m", "repo_level", "anchor"]


def history() -> pd.DataFrame:
    """All decisions with complete features and a known outcome (training and blind window)."""
    return se.load(unblind=True)


def derived(x: dict) -> pd.Series:
    s = pd.Series(x, dtype=float)
    s["infl_gap"] = s["infl"] - s["anchor"]
    s["proj_gap"] = s["proj_infl"] - s["anchor"]
    s["anchor_minus_repo"] = s["anchor"] - s["repo_level"]
    return s


def extrapolation(x: pd.Series, hist: pd.DataFrame) -> list[str]:
    cols = ["proj_revision", "infl_gap", "proj_gap", "growth_gap", "inr_depr_3m", "anchor_minus_repo"]
    return [c for c in cols if not hist[c].min() <= x[c] <= hist[c].max()]


def india(x: dict, hist: pd.DataFrame | None = None) -> dict:
    hist = history() if hist is None else hist
    s = derived(x)
    proba = wf.ordered_probit(hist, s, wf.ECON_MODEL_FEATURES)
    rule = sm.OLS(hist["change"], sm.add_constant(hist[se.RULE_TERMS])).fit()
    change = float(rule.params["const"] + (rule.params[se.RULE_TERMS] * s[se.RULE_TERMS]).sum())
    taylor = se.R_STAR + s["infl"] + 0.5 * s["infl_gap"] + 0.5 * s["growth_gap"]
    deadband = se.config()["deadband"]
    return {"p_cut": proba[0], "p_hold": proba[1], "p_hike": proba[2],
            "rule_change_pp": change, "rule": se.NAMES[se.direction(change, deadband)],
            "taylor_rate": taylor, "taylor": se.NAMES[se.direction(taylor - s["repo_level"], deadband)],
            "extrapolated": extrapolation(s, hist), "n_decisions": len(hist)}


def nepal(shock_pp: float) -> pd.DataFrame:
    """Conditional response of Nepali variables to an RBI repo change of shock_pp points."""
    lp = pd.read_csv(LP)
    out = lp[["outcome", "horizon"]].copy()
    for c in ("coef", "ci_low", "ci_high"):
        out[c] = lp[c] * shock_pp
    if shock_pp < 0:  # a negative shock flips the band
        out["ci_low"], out["ci_high"] = out["ci_high"].copy(), out["ci_low"].copy()
    return out.rename(columns={"coef": "response"})
