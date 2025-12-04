from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from .state import CoreState, Concept


SCHEMA = """
CREATE TABLE IF NOT EXISTS concepts (
    id TEXT PRIMARY KEY,
    embedding_version TEXT NOT NULL,
    embedding_json TEXT NOT NULL,
    authorship_json TEXT NOT NULL,
    parents_json TEXT NOT NULL,
    novelty_score REAL NOT NULL,
    timestamp REAL NOT NULL,
    is_near_duplicate INTEGER NOT NULL,
    primary_duplicate_id TEXT,
    submission_references_json TEXT NOT NULL,
    payload TEXT
);
"""


def open_db(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.executescript(SCHEMA)
    return conn


def load_state_from_db(conn: sqlite3.Connection) -> CoreState:
    state = CoreState()
    cur = conn.execute(
        "SELECT id, embedding_version, embedding_json, authorship_json, "
        "parents_json, novelty_score, timestamp, is_near_duplicate, "
        "primary_duplicate_id, submission_references_json "
        "FROM concepts ORDER BY timestamp ASC"
    )
    for (
        cid,
        embedding_version,
        embedding_json,
        authorship_json,
        parents_json,
        novelty_score,
        timestamp,
        is_near_duplicate,
        primary_duplicate_id,
        refs_json,
    ) in cur.fetchall():
        embedding = json.loads(embedding_json)
        authorship = json.loads(authorship_json)
        parents = json.loads(parents_json)
        refs = json.loads(refs_json)
        metadata = {
            "timestamp": timestamp,
            "is_near_duplicate": bool(is_near_duplicate),
            "primary_duplicate_id": primary_duplicate_id,
            "submission_references": refs,
        }
        concept = Concept(
            id=cid,
            embedding=embedding,
            embedding_version=embedding_version,
            authorship=authorship,
            parents=parents,
            novelty_score=novelty_score,
            metadata=metadata,
        )
        state.concepts[cid] = concept
    return state


def persist_concept(conn: sqlite3.Connection, concept: Concept, payload: str | None) -> None:
    metadata = concept.metadata
    conn.execute(
        """
        INSERT OR REPLACE INTO concepts (
            id, embedding_version, embedding_json, authorship_json,
            parents_json, novelty_score, timestamp, is_near_duplicate,
            primary_duplicate_id, submission_references_json, payload
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            concept.id,
            concept.embedding_version,
            json.dumps(concept.embedding),
            json.dumps(concept.authorship),
            json.dumps(concept.parents),
            float(concept.novelty_score),
            float(metadata.get("timestamp", 0.0)),
            int(bool(metadata.get("is_near_duplicate", False))),
            metadata.get("primary_duplicate_id"),
            json.dumps(metadata.get("submission_references", [])),
            payload,
        ),
    )
    conn.commit()


def get_lineage_chain(state: CoreState, concept_id: str) -> list[Concept]:
    """Return ancestors from the given concept back to the earliest root."""
    chain: list[Concept] = []
    current_id = concept_id
    visited: set[str] = set()
    while current_id in state.concepts and current_id not in visited:
        visited.add(current_id)
        c = state.concepts[current_id]
        chain.append(c)
        if not c.parents:
            break
        current_id = c.parents[0]
    return chain


