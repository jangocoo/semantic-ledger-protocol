## Semantic Ledger Protocol – Core Mechanism (v0 Draft)

### 1. Scope and Objectives

The Core Mechanism defines how the Semantic Ledger Protocol (SLP) measures conceptual novelty, establishes algorithmic lineage, and updates the shared semantic state.

This document specifies:

- The embedding pipeline for turning submissions into vectors.
- The distance and neighborhood model over embeddings.
- The novelty score function \(N\).
- The lineage construction algorithm and its invariants.
- Determinism requirements for distributed implementations.

Economic logic, consensus, and security are treated here only as external interfaces; they are defined in separate documents.

---

### 2. Fundamental Objects and Notation

#### 2.1 Submissions and Concepts

- **Submission** \(s\): A payload proposed to the protocol, consisting of:
  - `payload`: opaque content (text, code, media descriptors, etc.).
  - `authorship`: one or more author identifiers.
  - `timestamp`: wall-clock or logical time at submission.
  - `references` (optional): user-supplied links to existing concepts.

- **Concept** \(c\): A submission that has been accepted into the global semantic state. Each concept has:
  - `id`: a globally unique identifier.
  - `embedding`: a vector \(x \in \mathbb{R}^d\).
  - `embedding_version`: identifier of the embedding model/checkpoint.
  - `authorship`: copied from submission.
  - `parents`: ordered list of parent concept IDs.
  - `novelty_score`: scalar \(N(c) \in \mathbb{R}_{\ge 0}\).
  - `metadata`: auxiliary fields (timestamps, validity flags, domain tags, etc.).

#### 2.2 Embedding Space

- Let \(X = \mathbb{R}^d\) be the embedding space.
- Let \(d: X \times X \rightarrow \mathbb{R}_{\ge 0}\) be the distance function, derived from a similarity kernel (e.g., cosine distance).
- For a fixed embedding version \(v\), we assume:
  - A deterministic embedding function \(E_v(\cdot)\).
  - A fixed dimensionality \(d\).

**Requirement CM-1 (Deterministic Embeddings)**  
Given `embedding_version = v` and identical submission payload, all honest nodes MUST compute the same embedding vector \(x = E_v(s)\) up to permitted numerical tolerance.

---

### 3. Embedding Pipeline

The embedding pipeline converts a submission into a normalized vector.

#### 3.1 Embedding Model Versioning

- The protocol maintains a registry of embedding model versions:
  - `embedding_version` \(v \in V\).
  - For each \(v\), SLP defines:
    - Model architecture & checkpoint.
    - Tokenization & preprocessing rules.
    - Numeric precision rules (e.g., float32).

**Requirement CM-2 (Versioned Models)**  
Every concept MUST store the `embedding_version` used for its embedding. Nodes MUST NOT implicitly re-embed historical concepts with newer models without a state transition protocol.

#### 3.2 Preprocessing and Tokenization

For text-only v0 (generalized later to multimodal):

- **Preprocessing** steps (order is normative):
  1. Normalize Unicode.
  2. Lowercase or case-preserving rules (defined per version).
  3. Strip or normalize whitespace.
  4. Apply any protocol-defined content filters (e.g., length truncation).

- **Tokenization**:
  - Defined by the embedding model version \(v\).
  - MUST be deterministic for a given `payload` and \(v\).

#### 3.3 Vector Generation and Normalization

Given preprocessed tokens \(\tau\), the model yields a raw embedding \(z \in \mathbb{R}^d\).

- **Normalization** (v0 default):
  - L2-normalize: \(x = \frac{z}{\lVert z \rVert_2}\) if \(\lVert z \rVert_2 > 0\); otherwise, use a defined fallback (e.g., all zeros with a validity flag).

**Requirement CM-3 (Embedding Normalization)**  
For a given `embedding_version`, all nodes MUST apply the same normalization rule to ensure consistent distance calculations.

---

### 4. Distance and Neighborhood Model

#### 4.1 Distance Function

For v0, SLP uses **cosine distance** between normalized embeddings:

- Similarity: \(\text{sim}(x, y) = x \cdot y\).
- Distance: \(d(x, y) = 1 - \text{sim}(x, y)\).

Because embeddings are L2-normalized, \(d(x, y) \in [0, 2]\).

**Requirement CM-4 (Canonical Distance)**  
Implementations MUST use cosine distance over normalized vectors (or an equivalent numerically stable formulation) for the canonical novelty score computation.

#### 4.2 Neighborhood Definition

Given a new embedding \(x\) and an existing concept set \(C\) (for a fixed embedding_version \(v\)):

- Define \(k\)-nearest neighbors:
  - \( \mathcal{N}_k(x) = \{ c_1, \dots, c_k \} \subseteq C\),
  - ordered such that \(d(x, c_1) \le \dots \le d(x, c_k)\).

- v0 default:
  - \(k\) is a protocol parameter, globally fixed per embedding_version.
  - Search is over all concepts with the same `embedding_version`.

**Requirement CM-5 (Deterministic Neighbor Set)**  
For a given \(x\), `embedding_version`, \(k\), and concept set \(C\), honest nodes MUST return the same ordered neighbor set \(\mathcal{N}_k(x)\). Approximate methods MAY be used internally but MUST yield the same result as exact search within specified bounds.

#### 4.3 Multi-part Submissions (Optional v0 Extension)

For submissions containing multiple semantic units (e.g., sections, code + commentary), the protocol MAY define:

- Multiple embeddings \(x_1, \dots, x_m\).
- An aggregation rule (e.g., mean vector, max-novelty over parts).

In v0, this is left as an extension; the base Core Mechanism assumes a single vector per concept.

---

### 5. Novelty Score Function \(N\)

The novelty score \(N\) measures how much new conceptual information a submission introduces relative to the existing Concept Graph.

#### 5.1 Intuition

- High novelty:
  - The embedding lies far from existing concepts (low local density).
  - Or it occupies a sparsely populated region of the space.
- Low novelty:
  - The embedding is close to many existing concepts.
  - It resembles restatements, paraphrases, or incremental variations.

#### 5.2 Raw Distance Statistics

Given \(x\) and \(\mathcal{N}_k(x)\) with distances \(d_1 \le \dots \le d_k\):

- **Nearest distance**: \(d_{\min} = d_1\).
- **Mean neighbor distance**: \(\bar{d} = \frac{1}{k} \sum_{i=1}^k d_i\).
- **Density proxy**: For a radius \(r\), \(\rho_r(x) = |\{ i : d_i \le r \}|\).

#### 5.3 v0 Novelty Function

v0 defines a simple, interpretable novelty score combining rank and distance:

1. Choose protocol parameters per embedding_version:
   - \(k\): neighbor count.
   - \(r\): novelty radius (expected “close” concept distance scale).
   - \(\alpha, \beta \ge 0\): weighting coefficients.
2. Compute:
   - Normalized distance component:
     \[
     n_d = \max\left(0, \frac{d_{\min} - r}{1 - r}\right)
     \]
     (clamped to \([0, 1]\), assuming most meaningful distances are within \([0, 1]\)).
   - Density component:
     \[
     n_\rho = 1 - \frac{\rho_r(x)}{k}
     \]
3. Combine:
   \[
   N(x) = \alpha \cdot n_d + \beta \cdot n_\rho
   \]

Interpretation:

- \(N(x) \approx 0\): concept is close to many neighbors (low novelty).
- \(N(x) \approx \alpha + \beta\): concept is far from neighbors and in a sparse region (high novelty).

**Requirement CM-6 (Novelty Determinism)**  
Given \(x\), `embedding_version`, \(k\), \(r\), \(\alpha\), \(\beta\), and the concept set \(C\), nodes MUST compute identical \(N(x)\) up to agreed numeric tolerance.

#### 5.4 Alternative / Future Novelty Models

The protocol MAY define alternative novelty functions (e.g., based on local density estimation, rank-based statistics, or Bayesian models). Such alternatives MUST:

- Be versioned (e.g., `novelty_version`).
- Be fully specified so they are deterministic given the same inputs.
- Specify how economic components interpret mixed-version scores.

---

### 6. Lineage Construction

The lineage algorithm links a new concept to its closest conceptual parents.

#### 6.1 Parent Selection

Given neighbors \(\mathcal{N}_k(x) = \{c_1, \dots, c_k\}\) with distances \(d_1 \le \dots \le d_k\):

- Protocol parameter: \(p\) (max number of parents).
- Threshold parameter: \(\tau\) (maximum allowable distance for a parent).

Parent selection rule:

1. Initialize `parents = []`.
2. For \(i = 1\) to \(k\):
   - If \(d_i \le \tau\):
     - Append \(c_i.id\) to `parents`.
   - If `len(parents) == p`:
     - Stop.
3. If `parents` is empty:
   - Option A (v0 default): allow empty parents, concept is considered a “semantic root”.
   - Option B (extension): attach a synthetic root node per embedding_version.

Parents are ordered by increasing distance (closest first).

**Requirement CM-7 (Lineage Stability)**  
Given identical neighbor distances and protocol parameters \((k, p, \tau)\), honest nodes MUST select the same ordered parent list.

#### 6.2 Handling Near-Duplicates

To prevent redundant proliferation, v0 defines a **near-duplicate** rule:

- If \(d_{\min} \le \delta\) for a near-duplicate threshold \(\delta < \tau\):
  - The submission MAY be classified as a near-duplicate of \(c_1\).
  - Policy decisions (reject, flag, or accept with low novelty) are handled at higher layers.

Core Mechanism requirement:

- **Requirement CM-8 (Duplicate Flagging)**  
  Implementations MUST expose:
  - `is_near_duplicate` flag (boolean).
  - `primary_duplicate_id` (the ID of \(c_1\)).
  - These are derived deterministically from \(d_{\min}\), \(\delta\), and neighbor ordering.

#### 6.3 Lineage Invariants

The lineage graph MUST satisfy:

- No explicit restriction on cycles at the semantic layer, but with distance-based parenthood and monotonic timestamps, cycles SHOULD be impossible in normal operation.
- A concept’s parents MUST have:
  - The same `embedding_version` OR a clear cross-version mapping (out of scope for v0).
  - Earlier or equal submission time (subject to consensus order).

---

### 7. State Transition for a New Submission

This section defines the deterministic state transition applied when integrating a new valid submission.

#### 7.1 Inputs

Given:

- Global state snapshot:
  - Concept set \(C\) with embeddings, versions, and metadata.
  - Protocol parameters for the active epoch:
    - `embedding_version`.
    - \(k, r, \alpha, \beta, p, \tau, \delta\).
- Submission \(s\).

#### 7.2 Transition Algorithm (Pseudocode)

Pseudocode for the canonical Core Mechanism state transition:

```startLine:endLine:spec/core-mechanism.md
function IntegrateSubmission(s, state, params):
  # 1. Embed
  v = params.embedding_version
  x = E_v(preprocess(s.payload))

  # 2. Find neighbors
  C_v = { c in state.concepts where c.embedding_version == v }
  neighbors = kNN(x, C_v, k=params.k, distance=cosine_distance)
  # neighbors is a list of (concept, distance) sorted by distance

  if neighbors is empty:
    d_min = None
    rho_r = 0
  else:
    d_min = neighbors[0].distance
    rho_r = count(d <= params.r for (_, d) in neighbors)

  # 3. Compute novelty components
  if d_min is None:
    n_d = 1.0
    n_rho = 1.0
  else:
    n_d = max(0, (d_min - params.r) / (1 - params.r))
    n_rho = 1 - (rho_r / params.k)

  N = params.alpha * n_d + params.beta * n_rho

  # 4. Determine parents
  parents = []
  for (c, d) in neighbors:
    if d <= params.tau and len(parents) < params.p:
      parents.append(c.id)

  is_near_duplicate = False
  primary_duplicate_id = None
  if d_min is not None and d_min <= params.delta:
    is_near_duplicate = True
    primary_duplicate_id = neighbors[0].concept.id

  # 5. Allocate concept ID
  concept_id = DeriveConceptId(s, x, parents)

  # 6. Create concept object
  new_concept = Concept(
    id = concept_id,
    embedding = x,
    embedding_version = v,
    authorship = s.authorship,
    parents = parents,
    novelty_score = N,
    metadata = {
      "timestamp": s.timestamp,
      "is_near_duplicate": is_near_duplicate,
      "primary_duplicate_id": primary_duplicate_id,
      "submission_references": s.references,
    }
  )

  # 7. Update state
  state.concepts.add(new_concept)

  return state, new_concept
```

**Requirement CM-9 (State Transition Determinism)**  
Given the same prior state snapshot, submission, and parameters, all honest nodes MUST derive identical `new_concept` and resulting state.

---

### 8. Determinism, Precision, and Consensus Surface

#### 8.1 Numeric Precision

- Implementations MUST specify:
  - Numeric precision for embeddings and distances (e.g., float32).
  - Rounding rules for distance comparisons and thresholds.
- For consensus purposes, the canonical representation of:
  - `embedding` MAY be quantized (e.g., 16-bit or fixed-point).
  - `novelty_score` SHOULD be represented with a fixed precision (e.g., scaled integer).

#### 8.2 Consensus-Relevant Outputs

For each accepted submission, nodes are expected to agree on:

- `concept_id`.
- `embedding_version`.
- `parents` (ordered list).
- `novelty_score` (canonical representation).
- `is_near_duplicate` and `primary_duplicate_id`.

Local implementations MAY maintain additional metadata, indices, and caches, but MUST NOT modify these consensus-relevant fields.

---

### 9. Open Questions and Future Extensions

The following uncertainties are explicitly left for further research and experimentation:

- **U1 – Embedding standardization**: How frequently embedding models can be updated without destabilizing novelty scores and lineage.
- **U2 – Metric & topology**: Whether alternative metrics (e.g., angular distance, learned kernels) provide better alignment with human judgments.
- **U3 – Novelty calibration**: Exploring density-based, rank-based, or Bayesian formulations that better handle heterogeneous regions of embedding space.
- **U4 – Lineage robustness**: Optimal choices of \(p, \tau, \delta\) and more sophisticated parent selection (e.g., diversity-promoting parent sets).
- **U5 – Graph scalability**: Distributed indexing strategies and approximate neighbor search that remain reproducible at the protocol level.
- **U6 – Update & checkpoint rules**: Protocols for re-embedding and re-scoring legacy concepts when models change.
- **U7 – Adversarial behavior**: More advanced near-duplicate detection, collusion patterns, and defenses against synthetic novelty attacks.

These questions will be addressed in subsequent versions of this document and in dedicated experimental reports.


