from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Any, Sequence

import math
import random


@dataclass(frozen=True)
class EmbeddingVersion:
    """Identifier and configuration for an embedding backend."""

    name: str
    dim: int


class EmbeddingBackend(Protocol):
    """Protocol for pluggable embedding backends.

    Implementations must be deterministic for a given payload and version.
    """

    version: EmbeddingVersion

    def embed(self, payload: str) -> list[float]:
        """Return an L2-normalized embedding vector of length version.dim."""


def l2_normalize(vec: Sequence[float]) -> list[float]:
    norm_sq = sum(v * v for v in vec)
    if norm_sq <= 0.0:
        return [0.0] * len(vec)
    norm = math.sqrt(norm_sq)
    return [v / norm for v in vec]


class ToyHashEmbeddingBackend:
    """Simple deterministic hashing-based embedding for experimentation.

    NOTE: This is not semantically meaningful. It provides a stable
    vectorization suitable for testing the Core Mechanism flow without
    any external model dependencies.
    """

    def __init__(self, dim: int = 64, seed: int = 0) -> None:
        self.version = EmbeddingVersion(name=f"toy-hash-dim{dim}", dim=dim)
        self._dim = dim
        self._seed = seed

    def embed(self, payload: str) -> list[float]:
        # Simple normalization; real pipeline would follow spec/core-mechanism.
        text = " ".join(payload.strip().split())
        # Derive an integer seed from the text and base seed for determinism.
        combined_seed_str = f"{self._seed}:{text}"
        text_seed = hash(combined_seed_str)
        rnd = random.Random(text_seed)
        vec = [rnd.uniform(-1.0, 1.0) for _ in range(self._dim)]
        return l2_normalize(vec)


