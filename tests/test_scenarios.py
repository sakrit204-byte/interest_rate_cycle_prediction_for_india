from src.simulation import scenarios as sc

BASE = {"prev_decision": 0, "proj_revision": 0.0, "infl": 4.0, "proj_infl": 4.0, "growth_gap": 0.0,
        "inr_depr_3m": 0.0, "repo_level": 5.5, "anchor": 4.0}


def test_probabilities_sum_to_one_and_respond_to_revision():
    hist = sc.history()
    calm = sc.india(BASE, hist)
    hawk = sc.india({**BASE, "proj_revision": 1.0, "prev_decision": 1}, hist)
    assert abs(calm["p_cut"] + calm["p_hold"] + calm["p_hike"] - 1) < 1e-9
    assert hawk["p_hike"] > calm["p_hike"]


def test_extreme_inputs_flagged():
    out = sc.india({**BASE, "infl": 40.0})
    assert "infl_gap" in out["extrapolated"]


def test_nepal_response_scales_with_shock():
    one, half = sc.nepal(1.0), sc.nepal(0.5)
    assert (half["response"] - one["response"] / 2).abs().max() < 1e-12
    neg = sc.nepal(-1.0)
    assert (neg["ci_low"] <= neg["ci_high"]).all()


def test_nepal_binary_config_frozen():
    from src.models.nepal_binary import check_frozen
    cfg = check_frozen()
    assert cfg["horizon_months"] == 3 and cfg["deadband_pp"] == 0.5
