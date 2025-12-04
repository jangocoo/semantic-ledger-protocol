## Semantic Ledger Protocol – Core Mechanism Threat Model (v0 Draft)

### 1. Scope

This document analyzes threats specific to the **Core Mechanism** of SLP and describes how design choices in:

- The embedding pipeline,
- Distance and novelty computation, and
- Lineage construction

contribute to resilience against abuse. Economic and consensus-layer defenses are out of scope except where they directly consume Core Mechanism outputs.

---

### 2. Assets and Security Goals

#### 2.1 Assets

- **Semantic State Integrity**:
  - Correctness of embeddings, novelty scores, and lineage links.
  - Consistency of the Concept Graph across honest nodes.
- **Novelty Signal Quality**:
  - Usefulness of \(N\) as a proxy for conceptual originality.
- **Lineage Correctness**:
  - Accurate attribution of conceptual ancestry (parent links).

#### 2.2 Security Goals (Core Mechanism)

- **G1 – Deterministic Reproducibility**:  
  Any honest node with the same inputs computes identical embeddings, neighbors, novelty scores, and parents.

- **G2 – Robustness to Spam and Low-Signal Content**:  
  High-volume low-quality submissions should have predictably low or uninteresting novelty scores, enabling higher-layer filtering and fee mechanisms.

- **G3 – Resistance to Synthetic Novelty**:  
  Attackers should not be able to systematically inflate novelty scores via trivial perturbations or embedding-space exploits.

- **G4 – Lineage Manipulation Resistance**:  
  It should be hard to misattribute conceptual ancestry (e.g., stealing credit, erasing parents) through gaming of the embedding pipeline or neighborhood search.

---

### 3. Adversary Model

We assume:

- Adversaries may:
  - Submit arbitrary payloads at scale.
  - Coordinate across many identities (sybil behavior).
  - Generate content using powerful models and tools.
  - Attempt to reverse-engineer or probe the embedding model.
- Adversaries cannot:
  - Break standard cryptographic primitives (hashes, signatures).
  - Control a majority of consensus participants (handled elsewhere).
  - Arbitrarily modify honest nodes’ local implementations.

The Core Mechanism must remain correct and predictable even when faced with adversarially crafted submissions.

---

### 4. Threats and Mitigations

#### 4.1 Sybil and Spam Submission Floods

**Threat**:  
An attacker creates many identities and floods the system with low-value submissions, aiming to:

- Increase their share of concepts in the graph.
- Consume compute and storage resources.
- Dilute the meaning of novelty scores.

**Core Mechanism Exposure**:

- Heavy load on embedding and k-NN search.
- Higher local density in regions where the attacker operates.

**Mitigations via Core Mechanism Design**:

- **M1 – Density-Sensitive Novelty**:  
  The novelty score \(N(x)\) incorporates a density component \(n_\rho = 1 - \rho_r(x)/k\).  
  - As attackers pack submissions into a region, \(\rho_r(x)\) increases, driving \(N(x)\) down.
  - This naturally tags spam clusters as low-novelty.

- **M2 – Deterministic Near-Duplicate Flagging**:  
  If submissions are very similar (\(d_{\min} \le \delta\)), they are flagged as near-duplicates with a canonical primary duplicate.  
  - This enables higher layers to reject or discount redundant spam.

- **M3 – Parameterization for Economic Policies**:  
  By making \(k, r, \alpha, \beta\) explicit and deterministic, the protocol exposes clear levers for economic and rate-limiting policies (e.g., increasing fees or throttling in dense regions).

Residual risk is deferred to economic and consensus layers, which can penalize or limit repeated low-novelty submissions.

#### 4.2 Synthetic Novelty Attacks

**Threat**:  
Attackers craft payloads that are semantically trivial variants of existing concepts but are pushed into a sparse region of embedding space to score high novelty.

Examples:

- Adversarial perturbations that exploit embedding model weaknesses.
- Injection of irrelevant or random tokens to move embeddings.

**Core Mechanism Exposure**:

- Novelty \(N\) is determined by geometry in embedding space, which may be vulnerable to adversarial manipulation.

**Mitigations via Core Mechanism Design**:

- **M4 – Robust Preprocessing**:  
  Strict normalization of input (whitespace, casing, truncation, etc.) reduces degrees of freedom for trivial perturbations.

- **M5 – Neighborhood-Based Novelty**:  
  Since \(N\) is defined in relation to neighbors rather than absolute position, attackers must move embeddings away from *all* relevant neighbors, which is more difficult than just moving away from a single point.

- **M6 – Near-Duplicate and Density Checks**:  
  Even if a submission is moved slightly, if it remains within \(\delta\) of an existing concept, it is flagged as a near-duplicate.

- **M7 – Multi-Version Defense (Future)**:  
  Multiple embedding versions or ensembles can be used to cross-check novelty, making single-model attacks more brittle (left for future work).

Residual risk remains, especially for powerful white-box attackers; this motivates ongoing evaluation and periodic model updates.

#### 4.3 Lineage Manipulation and Credit Theft

**Threat**:  
Attackers attempt to:

- Divert parent links away from legitimate predecessors.
- Force themselves into lineage chains of valuable concepts.
- Erase or obscure certain ancestors.

**Core Mechanism Exposure**:

- Parent selection is based purely on embedding similarity and protocol parameters.

**Mitigations via Core Mechanism Design**:

- **M8 – Distance-Ordered Parent Selection**:  
  Parents are chosen as the closest neighbors within a threshold \(\tau\) and up to count \(p\), in deterministic order:
  - Attackers cannot arbitrarily declare themselves as parents; they must be among the nearest neighbors.

- **M9 – Consistent Embedding Versioning**:  
  Parent and child concepts share the same `embedding_version`, preventing attackers from manipulating lineage via inconsistent embeddings (cross-version lineage requires explicit mappings).

- **M10 – Deterministic k-NN and Parameters**:  
  Neighbors, thresholds, and parent counts are fixed and globally known.  
  - There is no local “wiggle room” to arbitrarily include or exclude parents.

Lineage manipulation remains possible to the extent an attacker can create genuinely closer embeddings than the legitimate parent, which is a fundamental limit of any embedding-based system; economic and governance layers can provide additional recourse (e.g., dispute processes).

#### 4.4 Graph Structure Attacks

**Threat**:  
Attackers attempt to:

- Create long chains or stars around their concepts to increase apparent centrality.
- Exploit graph metrics that may drive economic rewards.

**Core Mechanism Exposure**:

- The graph structure emerges from embedding geometry and parameter choices.

**Mitigations via Core Mechanism Design**:

- **M11 – Novelty-Weighted Lineage**:  
  Since \(N\) is attached to each concept, downstream reward systems can:
  - Discount low-novelty nodes, limiting benefits of shallow, spammy chains.

- **M12 – Bounded Parent Count**:  
  Limiting parents to \(p\) prevents attackers from arbitrarily attaching to many ancestors in a single step.

Graph-based rewards SHOULD be designed to be robust to such manipulations; this is addressed in economic-layer specs.

---

### 5. Design Choices that Support Security

The following Core Mechanism properties are explicitly motivated by threat considerations:

- **Deterministic Pipelines and Parameters**:
  - Make it trivial to detect divergence or misbehavior across nodes.
  - Reduce the attack surface for protocol-level ambiguity.

- **Density-Aware Novelty**:
  - Naturally penalizes clustered spam and sybil behavior.

- **Explicit Near-Duplicate Semantics**:
  - Provide a structured way to detect and respond to repeated submissions.

- **Strict Versioning (Embedding and Novelty)**:
  - Localizes the impact of model changes.
  - Enables coordinated upgrades with clear expectations.

---

### 6. Assumptions and Limitations

- **Embedding Model Robustness**:  
  The security of the Core Mechanism relies on the underlying embedding model being reasonably robust and semantically meaningful; this is an empirical property, not a guarantee.

- **Adversary Capabilities**:  
  Highly sophisticated attackers with white-box access to the embedding model may still craft adversarial examples that manipulate novelty or lineage.

- **No Content Semantics Beyond Embeddings**:  
  v0 does not include higher-level semantic checks (e.g., symbolic reasoning about content). All semantic judgments are mediated by the embedding model.

These limitations motivate the experimental and evaluation work described elsewhere, as well as additional layers of defense (economic, governance, content filters).

---

### 7. Future Work

Areas for further research and hardening include:

- Robustness benchmarks for novelty under adversarial perturbations.
- Multi-model or ensemble-based novelty definitions.
- Formal analysis of sybil strategies in embedding space.
- Integration with economic penalties and reputation systems for persistent abuse.

Threat analysis will evolve alongside changes to the Core Mechanism and embedding models, and SHOULD be revisited with each major version.


