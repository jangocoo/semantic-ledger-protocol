## Semantic Ledger Protocol – State and Concept Graph Model (v0 Draft)

### 1. Scope

This document specifies the **semantic state** maintained by SLP nodes and the **Concept Graph** data model. It is paired with the Core Mechanism specification (`spec/core-mechanism.md`) and defines:

- Canonical objects stored in state.
- Graph and index structures for concepts and lineage.
- Deterministic state transitions for new submissions.
- Checkpointing and versioning considerations.

Consensus, networking, and economics are out of scope and are treated as external consumers of this state.

---

### 2. State Overview

At time \(t\), a node maintains a semantic state \(S_t\) consisting of:

- A set of concepts \(\mathcal{C}_t\).
- A Concept Graph \(G_t = (\mathcal{C}_t, E_t)\) where edges encode lineage.
- Auxiliary indices for efficient neighbor queries and lineage traversal.
- A set of protocol parameters and versions active for the current epoch.

We distinguish between:

- **Consensus state**: fields that all honest nodes MUST agree on.
- **Local state**: implementation-specific indices and caches that do not affect consensus.

---

### 3. Core Data Structures

#### 3.1 Concept

Each concept \(c \in \mathcal{C}_t\) is represented as:

- `id`: globally unique identifier (e.g., hash-based).
- `embedding`: vector \(x \in \mathbb{R}^d\) or its canonical serialized form.
- `embedding_version`: identifier of the embedding model used.
- `authorship`: list of author identifiers.
- `parents`: ordered list of parent concept IDs.
- `novelty_score`: scalar \(N(c) \in \mathbb{R}_{\ge 0}\).
- `metadata`:
  - `timestamp`: submission or consensus inclusion time.
  - `is_near_duplicate`: boolean.
  - `primary_duplicate_id`: optional concept ID.
  - `submission_references`: optional user-supplied references.
  - Additional opaque key/value pairs reserved for higher layers.

**Consensus fields** (MUST match across nodes):

- `id`, `embedding_version`, `parents`, `novelty_score`,
- `authorship`, `metadata.timestamp`,
- `metadata.is_near_duplicate`, `metadata.primary_duplicate_id`.

The raw `embedding` MAY be represented in consensus or reconstructed from a hashed/quantized form, depending on protocol design; this is left flexible for v0.

#### 3.2 Concept Graph

The Concept Graph \(G_t = (\mathcal{C}_t, E_t)\) is a directed graph where:

- Vertices: concepts.
- Edges: lineage links.
  - An edge \(e = (p \rightarrow c)\) exists for each `p` in `c.parents`.

By construction:

- A concept can have 0 or more parents.
- Parent edges generally point from earlier to later concepts in time.

No explicit acyclicity constraint is enforced at the state level, but the Core Mechanism’s parent selection based on existing neighbors and monotonically growing state implies a DAG in normal operation.

---

### 4. Indices and Local Structures

Nodes maintain additional structures to support efficient queries. These structures are **local** and do not affect consensus as long as they remain consistent with the canonical concept set.

#### 4.1 Concept Store

An implementation-agnostic view:

- `ConceptStore`:
  - Keyed by `concept_id`.
  - Stores consensus fields and optionally embeddings in canonical or compressed form.

Operations:

- `GetConcept(id) -> Concept?`
- `PutConcept(concept)`

#### 4.2 Embedding Index

For each `embedding_version` \(v\), nodes maintain an index to support k-NN search:

- `EmbeddingIndex[v]`:
  - Stores `concept_id` and embedding (or pointer) pairs.
  - Supports `kNN(x, k) -> [(concept_id, distance)]`.

Implementations MAY use any internal structure (e.g., exact search, tree-based, or approximate methods) as long as protocol-level determinism requirements from the Core Mechanism are satisfied.

#### 4.3 Lineage Indices

To enable efficient graph traversal:

- `ParentsIndex`:
  - Maps `concept_id -> [parent_ids]` (redundant with `Concept.parents` but convenient).
- `ChildrenIndex`:
  - Maps `concept_id -> [child_ids]` (reverse edges).

These indices are derived from the canonical Concept Graph and MUST be reconstructible from the concept set alone.

---

### 5. State Parameters and Versions

The state also includes protocol-level parameters that govern embedding, neighborhood, and novelty computation for the current epoch.

#### 5.1 Parameter Set

For each active `embedding_version` and novelty definition, an associated parameter set is stored:

- `embedding_version`: identifier.
- `novelty_version`: identifier of the novelty function.
- `k`: neighbor count for k-NN.
- `r`: novelty radius.
- `alpha`, `beta`: novelty weight coefficients.
- `p`: maximum number of parents.
- `tau`: parent distance threshold.
- `delta`: near-duplicate threshold.

These parameters MAY be updated over time via governance or consensus, but updates must respect:

- **P1 (Epoch-Scoped Parameters)**:  
  For a given epoch \(e\), a fixed parameter set applies to all submissions finalized in that epoch.

- **P2 (Reproducibility)**:  
  Nodes MUST keep a record of which parameter set applied to each concept (explicitly, or implicitly by epoch reference) to enable exact recomputation of novelty and lineage if required.

---

### 6. Canonical State Transition

The Core Mechanism defines the algorithmic steps for integrating a new submission. The state model here clarifies how those steps manifest as changes in stored structures.

#### 6.1 Precondition

Given:

- A state \(S_t\) with concept set \(\mathcal{C}_t\) and indices.
- A submission \(s\) that has passed any non-core validation (e.g., authorization, fee payment).
- The active parameter set `params` for the current epoch.

#### 6.2 Transition Steps

Conceptually, integrating a new submission performs:

1. Compute embedding and nearest neighbors (per Core Mechanism).
2. Compute novelty score, parents, and duplicate flags.
3. Derive a new concept ID.
4. Append the new concept to the concept set.
5. Update graph and indices.

Pseudocode focusing on state mutation:

```startLine:endLine:spec/state-model.md
function ApplyConceptStateTransition(S_t, new_concept):
  # 1. Insert into concept store
  S_t.ConceptStore.PutConcept(new_concept)

  # 2. Update Concept Graph edges
  for parent_id in new_concept.parents:
    S_t.ParentsIndex[new_concept.id].append(parent_id)
    S_t.ChildrenIndex[parent_id].append(new_concept.id)

  # 3. Update embedding index for the concept's embedding_version
  v = new_concept.embedding_version
  S_t.EmbeddingIndex[v].Insert(new_concept.id, new_concept.embedding)

  # 4. Return updated state
  return S_t
```

The ordering between the Core Mechanism’s `IntegrateSubmission` (which computes `new_concept`) and this function is implementation-dependent, but the combined operation MUST be deterministic given the same inputs.

---

### 7. Concept ID Derivation

SLP does not prescribe a specific concept ID scheme in v0, but any scheme MUST satisfy:

- **C1 (Collision Resistance)**:  
  It must be computationally infeasible to deliberately create different concepts with the same ID.

- **C2 (Determinism)**:  
  Given the same submission payload, embedding, parents, and relevant metadata, all honest nodes compute the same ID.

One candidate scheme:

- Compute a hash over a canonical serialization of:
  - `embedding_version`
  - `embedding` (quantized or hashed)
  - `parents` (ordered)
  - `authorship`
  - `metadata.timestamp`

Exact serialization and hashing algorithms MUST be specified in a future document; here we only assert invariants.

---

### 8. Checkpoints and Snapshots

To support scalability and long-term reproducibility, nodes maintain **state checkpoints**:

- A checkpoint at logical height \(h\) contains:
  - A root commitment to the concept set and graph (e.g., Merkle root or hash tree).
  - The active parameter set(s) at that height.
  - Optional metadata (e.g., wall-clock timestamp).

**Requirement SM-1 (Checkpoint Determinism)**  
Given the same sequence of accepted submissions and parameter updates, all honest nodes MUST derive identical checkpoint commitments at the same heights.

Nodes MAY prune or archive older concepts, embeddings, and indices as long as:

- They can still validate new submissions against the required history (or rely on light-client proofs).
- They preserve or can reconstruct all consensus-relevant data for finalized checkpoints.

---

### 9. Query Surface (Read-Only)

The state model enables a set of canonical queries that higher layers and external clients can rely on. These queries are read-only and do not modify state.

#### 9.1 Concept and Lineage Queries

Examples:

- `GetConcept(id) -> Concept?`
- `GetParents(id) -> [Concept]`
- `GetChildren(id) -> [Concept]`
- `GetAncestors(id, depth_limit?) -> [Concept]`
- `GetDescendants(id, depth_limit?) -> [Concept]`

Traversal semantics (e.g., ordering, deduplication) should be clearly defined in client APIs but do not affect the consensus state.

#### 9.2 Novelty and Neighborhood Queries

Examples:

- `GetNovelty(id) -> float`
- `GetNeighbors(id, k) -> [(Concept, distance)]`  
  (where neighbors are based on embeddings and the active or historical parameter set).

These queries may require re-running portions of the Core Mechanism (e.g., k-NN) over stored embeddings, but MUST NOT change any consensus fields.

#### 9.3 Checkpoint Queries

Examples:

- `GetStateCheckpoint(height_or_epoch) -> { root_hash, parameters }`
- `ListCheckpoints(range) -> [checkpoint_headers]`

---

### 10. Open Questions

The following aspects of the state model are intentionally under-specified and require further design:

- How to represent embeddings in consensus:
  - Full float vectors vs. quantized vs. hashed commitments.
- How to handle cross-embedding-version relationships in the Concept Graph.
- Efficient proof systems for inclusion and lineage (e.g., Merkle proofs).
- Archival vs. active storage policies and their impact on Core Mechanism behavior.

These questions will be refined alongside prototype implementations and performance experiments.


