"""Policy direction suggestions for RBI decisions from three independent sources (plan section 6).

1. Learned reaction function: the economic ordered probit (model 3, D029) gives P(cut, hold, hike).
2. Estimated inertial rule, fitted by OLS on past decisions only:
       change = c + lam * (anchor - repo) + b1 infl_gap + b2 proj_gap + b3 growth_gap
   so the rate closes a share lam of the gap to a neutral rate that moves with the regime's
   nominal anchor (lam = 1 - smoothing; implied neutral real rate c / lam).
3. Textbook Taylor rule (normative reference, never "correct"):
       rate = R_STAR + infl + 0.5 * (infl - anchor) + 0.5 * growth_gap
   with the IIP growth gap as a stand in for the output gap.

Rule directions use a deadband of DEADBAND_BP either side of zero. Combination (fixed before
unblinding): the suggestion is the classifier's top class when its probability exceeds
MIN_TOP_PROB and the estimated rule agrees, otherwise "uncertain". Reason codes are the two
largest contributions to the estimated rule.

Every model is refit at each decision on outcomes public by its cutoff (real time). Blind
window decisions are refused unless the blind config is frozen and its hash matches (D033).

Output: reports/tables/suggestions_train.csv (or suggestions_blind.csv when unblinded)
Usage: python -m src.policy.suggestion_engine [--unblind]
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import yaml

from src.models import walk_forward as wf

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "configs" / "blind_test.yaml"
FROZEN_HASH = ROOT / "configs" / "blind_test.sha256"
TABLES = ROOT / "reports" / "tables"
CLASSIFIER_FEATURES = wf.ECON_MODEL_FEATURES
RULE_TERMS = ["anchor_minus_repo", "infl_gap", "proj_gap", "growth_gap"]
R_STAR = 1.5  # neutral real rate, within the RBI's published estimates (to cite in the paper)
NAMES = {-1: "cut", 0: "hold", 1: "hike"}


def config() -> dict:
    cfg = yaml.safe_load(CONFIG.read_text())
    return {"deadband": cfg["suggestion_engine"]["deadband_bp"] / 100,
            "min_top": cfg["suggestion_engine"]["classifier_min_top_probability"],
            "blind_start": pd.Timestamp(cfg["blind_window_start"]), "status": cfg["status"]}


def load(unblind: bool) -> pd.DataFrame:
    f = pd.read_csv(wf.FEATURE_FILE, parse_dates=["date", "cutoff"])
    f = f[f["complete_econ"]].reset_index(drop=True)
    f["anchor"] = f["infl"] - f["infl_gap"]
    f["anchor_minus_repo"] = f["anchor"] - f["repo_level"]
    f["change"] = f["change_bp"] / 100
    if not unblind:
        f = f[f["date"] < config()["blind_start"]].reset_index(drop=True)
    return f


def config_hash() -> str:
    """SHA256 of the config with line endings normalised, so a checkout on any system matches."""
    return hashlib.sha256(CONFIG.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def check_frozen() -> None:
    cfg = config()
    digest = config_hash()
    if cfg["status"] != "frozen" or not FROZEN_HASH.exists() or FROZEN_HASH.read_text().split()[0] != digest:
        raise RuntimeError("blind config is not frozen or its hash differs; refusing to unblind")


def direction(x: float, deadband: float) -> int:
    return 1 if x > deadband else (-1 if x < -deadband else 0)


def suggest(tr: pd.DataFrame, te: pd.Series, cfg: dict) -> dict:
    proba = wf.ordered_probit(tr, te, CLASSIFIER_FEATURES)
    top = int(np.argmax(proba))
    rule = sm.OLS(tr["change"], sm.add_constant(tr[RULE_TERMS])).fit()
    contrib = rule.params[RULE_TERMS] * te[RULE_TERMS].astype(float)
    rule_change = float(rule.params["const"] + contrib.sum())
    taylor = R_STAR + te["infl"] + 0.5 * te["infl_gap"] + 0.5 * te["growth_gap"]
    rule_dir = direction(rule_change, cfg["deadband"])
    clf_dir = int(wf.CLASSES[top])
    agreed = proba[top] > cfg["min_top"] and clf_dir == rule_dir
    lam = rule.params["anchor_minus_repo"]
    reasons = contrib.reindex(contrib.abs().sort_values(ascending=False).index)[:2]
    return {"date": te["date"].date(), "actual": NAMES[int(te["y"])], "repo_before": te["repo_level"],
            "p_cut": proba[0], "p_hold": proba[1], "p_hike": proba[2], "classifier": NAMES[clf_dir],
            "rule_change_pp": rule_change, "rule_prescribed_rate": te["repo_level"] + rule_change,
            "rule": NAMES[rule_dir], "smoothing": 1 - lam, "neutral_real_rate": rule.params["const"] / lam if lam else np.nan,
            "taylor_rate": taylor, "taylor": NAMES[direction(taylor - te["repo_level"], cfg["deadband"])],
            "suggestion": NAMES[clf_dir] if agreed else "uncertain",
            "reasons": "; ".join(f"{k} {v:+.2f}" for k, v in reasons.items()), "n_train": len(tr),
            "blind_window": bool(te["date"] >= cfg["blind_start"])}


def run(data: pd.DataFrame, cfg: dict, start: int = wf.MIN_TRAIN) -> pd.DataFrame:
    rows = []
    for i in range(start, len(data)):
        te = data.iloc[i]
        tr = data.iloc[:i]
        rows.append(suggest(tr[tr["date"] <= te["cutoff"]], te, cfg))  # outcomes known by the cutoff
    return pd.DataFrame(rows)


def agreement(s: pd.DataFrame) -> pd.DataFrame:
    out = []
    for col in ["classifier", "rule", "taylor", "suggestion"]:
        sure = s[s[col] != "uncertain"]
        out.append({"source": col, "n": len(s), "covered": len(sure), "hit_rate_covered": (sure[col] == sure["actual"]).mean(),
                    "hit_rate_all": (s[col] == s["actual"]).mean()})
    return pd.DataFrame(out)


def main() -> int:
    unblind = "--unblind" in sys.argv
    if unblind:
        check_frozen()
    cfg = config()
    s = run(load(unblind), cfg)
    if unblind:
        s = s[s["blind_window"]]
    tag = "blind" if unblind else "train"
    TABLES.mkdir(parents=True, exist_ok=True)
    s.round(4).to_csv(TABLES / f"suggestions_{tag}.csv", index=False)
    a = agreement(s)
    a.round(4).to_csv(TABLES / f"suggestions_{tag}_agreement.csv", index=False)
    print(a.round(3).to_string(index=False))
    print(s[["smoothing", "neutral_real_rate"]].describe().round(2).to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
