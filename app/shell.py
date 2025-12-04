from __future__ import annotations

import sys
import time
from pathlib import Path

from core.embeddings import ToyHashEmbeddingBackend
from core.novelty import NoveltyParams
from core.persistence import open_db, load_state_from_db, persist_concept, get_lineage_chain
from core.state import CoreParams, CoreState, Submission, integrate_submission


def make_core_params() -> CoreParams:
    novelty = NoveltyParams(k=8, r=0.3, alpha=1.0, beta=1.0)
    return CoreParams(
        embedding_version="toy-hash-dim64",
        novelty=novelty,
        k=8,
        p=4,
        tau=0.6,
        delta=0.1,
    )


def print_concept_result(state: CoreState, concept_id: str) -> None:
    from core.state import Concept  # local import to avoid cycles in type hints

    concept = state.concepts[concept_id]
    print("\n=== Concept Integrated ===")
    print(f"ID: {concept.id}")
    print(f"Novelty score N: {concept.novelty_score:.4f}")
    meta = concept.metadata
    print(f"Timestamp: {meta.get('timestamp')}")
    print(f"Near duplicate: {bool(meta.get('is_near_duplicate'))}")
    if meta.get("primary_duplicate_id"):
        print(f"Primary duplicate ID: {meta.get('primary_duplicate_id')}")
    print(f"Parents: {concept.parents or '[]'}")

    # Lineage chain
    print("\nLineage (from newest to root):")
    chain = get_lineage_chain(state, concept_id)
    for idx, c in enumerate(chain):
        marker = "->" if idx > 0 else "  "
        print(f"{marker} {c.id} (N={c.novelty_score:.4f})")
    print()


def main() -> None:
    db_path = Path("/data/slp_core.sqlite")
    backend = ToyHashEmbeddingBackend(dim=64, seed=0)
    params = make_core_params()

    conn = open_db(db_path)
    state = load_state_from_db(conn)

    print("Semantic Ledger Protocol - Core Prototype Shell")
    print("Type text and press Enter to submit as a concept.")
    print("Commands: /quit or /exit to leave, /help for help.\n")

    for line in sys.stdin:
        text = line.rstrip("\n")
        if not text:
            continue
        if text in ("/quit", "/exit"):
            break
        if text == "/help":
            print("Enter any non-empty line to submit it as a new concept.")
            print("The system will output a novelty score and lineage chain.\n")
            continue

        submission = Submission(
            payload=text,
            authorship=["shell-user"],
            timestamp=time.time(),
        )
        result = integrate_submission(submission, state, params, backend)
        persist_concept(conn, result.concept, payload=text)
        print_concept_result(state, result.concept.id)

    print("Exiting SLP Core shell.")


if __name__ == "__main__":
    main()


