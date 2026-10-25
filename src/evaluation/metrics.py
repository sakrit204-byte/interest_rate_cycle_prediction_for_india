"""Classification metrics for three class policy decisions (cut = -1, hold = 0, hike = 1)."""

from __future__ import annotations

import numpy as np
from sklearn.metrics import balanced_accuracy_score, cohen_kappa_score, f1_score

CLASSES = np.array([-1, 0, 1])


def log_loss(y: np.ndarray, proba: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    """Per decision log loss; proba columns ordered as CLASSES."""
    p = np.clip(proba[np.arange(len(y)), np.searchsorted(CLASSES, y)], eps, 1)
    return -np.log(p)


def brier(y: np.ndarray, proba: np.ndarray) -> np.ndarray:
    """Per decision multi class Brier score (sum over classes, range 0 to 2)."""
    onehot = (y[:, None] == CLASSES[None, :]).astype(float)
    return ((proba - onehot) ** 2).sum(axis=1)


def summary(y: np.ndarray, pred: np.ndarray, proba: np.ndarray) -> dict:
    return {
        "n": len(y),
        "accuracy": float((y == pred).mean()),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "macro_f1": float(f1_score(y, pred, labels=CLASSES, average="macro", zero_division=0)),
        "cohen_kappa": float(cohen_kappa_score(y, pred, labels=CLASSES)),
        "log_loss": float(log_loss(y, proba).mean()),
        "brier": float(brier(y, proba).mean()),
    }


def block_bootstrap_ci(y: np.ndarray, pred: np.ndarray, block: int = 6, reps: int = 2000,
                       seed: int = 0) -> tuple[float, float]:
    """95 percent moving block bootstrap interval for balanced accuracy.

    Decisions come in runs (rate cycles), so blocks of consecutive decisions are resampled.
    """
    rng = np.random.default_rng(seed)
    n = len(y)
    starts = np.arange(n - block + 1)
    stats = []
    for _ in range(reps):
        idx = np.concatenate([np.arange(s, s + block) for s in rng.choice(starts, n // block + 1)])[:n]
        if len(np.unique(y[idx])) < 2:
            continue
        stats.append(balanced_accuracy_score(y[idx], pred[idx]))
    return float(np.percentile(stats, 2.5)), float(np.percentile(stats, 97.5))
