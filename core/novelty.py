from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import math


def cosine_distance(x: Sequence[float], y: Sequence[float]) -> float:
    """Cosine distance for L2-normalized vectors.

    Returns a value in [0, 2]. Assumes inputs are normalized.
    """
    dot = sum(a * b for a, b in zip(x, y))
    # Clamp for numerical safety.
    dot = max(min(dot, 1.0), -1.0)
    return 1.0 - dot


@dataclass
class NoveltyParams:
    """Parameters for the v0 novelty function."""

    k: int
    r: float
    alpha: float
    beta: float


@dataclass
class NoveltyComponents:
    d_min: float | None
    rho_r: int
    n_d: float
    n_rho: float
    score: float


def compute_novelty(
    distances: list[float], params: NoveltyParams
) -> NoveltyComponents:
    """Compute v0 novelty score and components from neighbor distances."""
    if not distances:
        # No neighbors: treat as maximally novel.
        return NoveltyComponents(
            d_min=None,
            rho_r=0,
            n_d=1.0,
            n_rho=1.0,
            score=params.alpha + params.beta,
        )

    distances = sorted(distances)
    d_min = distances[0]
    rho_r = sum(1 for d in distances[: params.k] if d <= params.r)

    # Distance component
    if params.r >= 1.0:
        n_d = 0.0
    else:
        n_d = max(0.0, (d_min - params.r) / (1.0 - params.r))

    # Density component
    if params.k <= 0:
        n_rho = 0.0
    else:
        n_rho = 1.0 - (rho_r / float(params.k))

    score = params.alpha * n_d + params.beta * n_rho

    return NoveltyComponents(
        d_min=d_min,
        rho_r=rho_r,
        n_d=n_d,
        n_rho=n_rho,
        score=score,
    )


