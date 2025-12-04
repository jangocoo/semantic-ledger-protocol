from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Iterable

from .embeddings import EmbeddingBackend
from .novelty import cosine_distance, NoveltyParams, compute_novelty, NoveltyComponents


@dataclass
class Submission:
    payload: str
    authorship: List[str]
    timestamp: float
    references: List[str] | None = None


@dataclass
class Concept:
    id: str
    embedding: List[float]
    embedding_version: str
    authorship: List[str]
    parents: List[str]
    novelty_score: float
    metadata: Dict[str, object] = field(default_factory=dict)


@dataclass
class CoreParams:
    embedding_version: str
    novelty: NoveltyParams
    k: int
    p: int
    tau: float
    delta: float


@dataclass
class CoreState:
    concepts: Dict[str, Concept] = field(default_factory=dict)

    def concepts_for_version(self, embedding_version: str) -> Iterable[Concept]:
        return (c for c in self.concepts.values() if c.embedding_version == embedding_version)


def _k_nn(
    x: List[float], candidates: Iterable[Concept], k: int
) -> List[Tuple[Concept, float]]:
    scored: List[Tuple[Concept, float]] = []
    for c in candidates:
        d = cosine_distance(x, c.embedding)
        scored.append((c, d))
    scored.sort(key=lambda cd: cd[1])
    return scored[:k]


def derive_concept_id(submission: Submission, embedding: List[float], parents: List[str]) -> str:
    """Derive a deterministic concept ID from submission + embedding + parents.

    This is a placeholder; a production implementation would use a
    canonical serialization and cryptographic hash.
    """
    # Simple stable representation for prototype purposes.
    key = (
        submission.payload,
        tuple(submission.authorship),
        round(submission.timestamp, 6),
        tuple(parents),
        tuple(round(v, 6) for v in embedding[:8]),  # sample of vector
    )
    return f"c-{hash(key)}"


@dataclass
class IntegrateResult:
    state: CoreState
    concept: Concept
    novelty: NoveltyComponents
    neighbors: List[Tuple[Concept, float]]


def integrate_submission(
    submission: Submission,
    state: CoreState,
    params: CoreParams,
    backend: EmbeddingBackend,
) -> IntegrateResult:
    """Apply the Core Mechanism to a submission and update state."""
    # 1. Embed
    x = backend.embed(submission.payload)

    # 2. Find neighbors for this embedding_version
    candidates = list(state.concepts_for_version(params.embedding_version))
    neighbors = _k_nn(x, candidates, k=params.k)
    distances = [d for _, d in neighbors]

    # 3. Compute novelty
    novelty = compute_novelty(distances, params.novelty)

    # 4. Determine parents
    parents: List[str] = []
    for c, d in neighbors:
        if d <= params.tau and len(parents) < params.p:
            parents.append(c.id)

    is_near_duplicate = False
    primary_duplicate_id: str | None = None
    d_min = novelty.d_min
    if d_min is not None and neighbors and d_min <= params.delta:
        is_near_duplicate = True
        primary_duplicate_id = neighbors[0][0].id

    # 5. Allocate concept ID
    concept_id = derive_concept_id(submission, x, parents)

    # 6. Create concept object
    metadata: Dict[str, object] = {
        "timestamp": submission.timestamp,
        "is_near_duplicate": is_near_duplicate,
        "primary_duplicate_id": primary_duplicate_id,
        "submission_references": submission.references or [],
    }
    concept = Concept(
        id=concept_id,
        embedding=x,
        embedding_version=params.embedding_version,
        authorship=submission.authorship,
        parents=parents,
        novelty_score=novelty.score,
        metadata=metadata,
    )

    # 7. Update state
    state.concepts[concept_id] = concept

    return IntegrateResult(
        state=state,
        concept=concept,
        novelty=novelty,
        neighbors=neighbors,
    )


