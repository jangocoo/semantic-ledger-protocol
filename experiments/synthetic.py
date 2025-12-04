from __future__ import annotations

from dataclasses import dataclass
from typing import List, Iterable

import time

from core.embeddings import ToyHashEmbeddingBackend
from core.novelty import NoveltyParams
from core.state import (
    CoreParams,
    CoreState,
    Submission,
    integrate_submission,
)


@dataclass
class SyntheticRunResult:
    concept_ids: List[str]
    novelty_scores: List[float]


def make_default_core_params() -> CoreParams:
    novelty_params = NoveltyParams(k=8, r=0.3, alpha=1.0, beta=1.0)
    return CoreParams(
        embedding_version="toy-hash-dim64",
        novelty=novelty_params,
        k=8,
        p=4,
        tau=0.6,
        delta=0.1,
    )


def run_synthetic_sequence(
    payloads: Iterable[str],
    authorship: List[str] | None = None,
    params: CoreParams | None = None,
) -> SyntheticRunResult:
    """Run a simple synthetic sequence through the core prototype."""
    backend = ToyHashEmbeddingBackend(dim=64, seed=0)
    if params is None:
        params = make_default_core_params()

    if authorship is None:
        authorship = ["synthetic-author"]

    state = CoreState()
    concept_ids: List[str] = []
    novelty_scores: List[float] = []

    for i, payload in enumerate(payloads):
        submission = Submission(
            payload=payload,
            authorship=authorship,
            timestamp=time.time() + i,
        )
        result = integrate_submission(submission, state, params, backend)
        concept_ids.append(result.concept.id)
        novelty_scores.append(result.concept.novelty_score)

    return SyntheticRunResult(concept_ids=concept_ids, novelty_scores=novelty_scores)


