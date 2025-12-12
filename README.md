# Semantic Ledger Protocol (SLP)

A distributed protocol for measuring conceptual novelty, establishing idea lineage, and rewarding meaningful contributions across human and AI-generated content.

## Problem

 - Knowledge is being absorbed into private LLMs with no shared economic value.
 - Creators have no visibility into how their ideas influence model behavior.
 - The economy rewards attention, not insight.
 - Valuable idea is not necessary links to economic reward.
 - Internet monetization is not always fair to creators.

## Introduction

The Semantic Ledger Protocol introduces an alternative: an economic and computational layer that evaluates originality at the conceptual level and allocates rewards accordingly.

SLP measures the conceptual distance between new submissions and existing knowledge, records the lineage of ideas, and distributes royalties to contributors whose concepts form the foundation for later work.

## Vision

Content forms a lineage-directed acyclic graph where every idea has an author and a semantic ancestry. Each new submission computes a novelty diff against prior concepts, quantifying true contribution. Royalties flow along this lineage, rewarding both originators of breakthrough ideas and later authors who successfully develop them.

This shifts incentives toward generating genuine novelty. In the age of AI where models compress vast human work into internal representations and tend to average toward familiar patterns this provides:

 - Traceable lineage from AI outputs back to human creators.
 - A mechanism for compensating upstream contributors.
 - A structured cost for publishing to prevent spam and fund network operation.

Rewards for nodes running compute and serving the semantic graph.

## Example

### Stage 1 - Foundational idea

A writer submits a short concept T1:
"Cities behave like living organisms: they grow, adapt, and metabolize information."

Novelty Score:0.82

Parents: T0 (networlk genesis-level concept)

Explanation:
The idea is relatively original within the current semantic graph.

### Stage 2 - A refinement that builds on it

Another author submits T2:
"A city`s transportation system acts as its circulatory system, distributing energy and resources."

Novelty Score:0.41

Parent: T1

Trajectory similarity shows T2 is conceptually downstream from T1:
 - Same metaphor frame ("cities as living organisms")
 - More specific organ-level analogy ("circulatory system")
 - Clear semantic continuation

Royalty distribution for T2:
 - New author (T2): 41%
 - T1`s author: 59% (due to inherited conceptual skeleton)

### Stage 3 - A different branch of elaboration

A third author submits T3:
"In living cities, information flow - not transportation - is the true lifeblood."

Novelty Score:0.47

Parents:
 - T1 (dominant)
 - Partial link to T2 (weaker, because it flips the framing)

Explanation:
T3 builds on T1s central metaphor but diverges sharply from T2.
It becomes a sibling, not a child, of T2.

Royalty distribution:
 - T3 author: 47%
 - T1 author: 53%
 - (No significant royalty to T2; its influence is minimal)

### Stage 4 - A synthesis that connects branches

A writer merges both branches into a deeper insight T4:
"A city`s circulatory and informational flows interact like biological feedback loops - transport enables data exchange, and data reorganizes transport."

Novelty Score:0.36

Parents (weighted):
 - T2: 52%
 - T3: 34%
 - T1: 14%

This is a semantic interpolation:
 - It inherits the organism metaphor from T1
 - Draws transport concepts from T2
 - Draws information-as-lifeblood from T3

Introduces a new integrated mechanism ("feedback loops")

Royalty split for T4:
 - T4 author: 36%
 - T2 author: 52% of remaining 64%
 - T3 author: 34% of remaining 64%
 - T1 author: 14% of remaining 64%
 - T1 continues to earn small but persistent royalties across the tree.

### Stage 5 - A near-duplicate derivative (low novelty)

Someone submits T5:
"Cities evolve by balancing transportation needs with information flow."

Novelty Score:0.11

Parents (dominant):
 - T2
 - T3

Explanation:
T5 is essentially a paraphrase of the established domain.
The system registers it as extremely low novelty.

Royalty distribution:
 - T5 author: 11%
 - T2, T3, T1 authors: receive the remaining 89% proportionally

This illustrates how low-novelty text mostly rewards previous contributors.

### Stage 6 - Behavior over time

As dozens or hundreds of submissions accumulate:
 - T1 becomes the conceptual trunk.
 - T2 and T3 become major branches.
 - T4 becomes a key connector node.
 - T5 and similar nodes contribute mostly upstream.

Early contributors gain long-term value for foundational concepts.
Later contributors earn when genuinely adding new structure.



                           ┌────────────────────────────────┐
                           │   T1 (N=0.82)                  │
                           │   "Cities as living organisms" │
                           └──────────────┬─────────────────┘
                                          │
                     ┌────────────────────┼───────────────────────┐
                     │                    │                       │
                     │ 59%                │ 53%                   │ 14%
                     ▼                    ▼                       ▼

        ┌───────────────────────┐   ┌────────────────────────┐   (minor influence
        │  T2 (N=0.41)          │   │  T3 (N=0.47)           │    on later nodes)
        │  "Transport as        │   │  "Information flow is  │
        │   circulatory system" │   │   the true lifeblood"  │
        └───────────┬───────────┘   └───────────┬────────────┘
                    │                           │
                    │ 52%                       │ 34%
                    └──────────────┬────────────┘
                                   ▼
                      ┌────────────────────────────────────────────┐
                      │  T4 (N=0.36)                               │
                      │  "Transport + information as feedback      │
                      │   loops"                                   │
                      └──────────────┬─────────────────────────────┘
                                     │
                                     │ dominates parent linkage
                                     ▼
                      ┌─────────────────────────────────────────────┐
                      │  T5 (N=0.11)                                │
                      │  "Cities evolve by balancing transport      │
                      │    and information flow"                    │
                      └─────────────────────────────────────────────┘


## Core Mechanism

### Novelty Engine

The Novelty Engine defines how conceptual novelty is measured and integrated.

### Semantic Embeddings
Each submission is converted into a vector trajectory using a standardized, protocol-defined embedding model.

### Conceptual Distance
The embedding is compared against the existing Concept Graph. Distance to nearest concepts determines novelty.

### Novelty Score (N)
A scalar representing how much new conceptual information is introduced. High scores indicate new primitives or breakthroughs; low scores indicate derivations or restatements.

### Integration
Every submission is linked to its closest conceptual parents. This establishes irrefutable, algorithmic provenance.

### Concept Lineage

Concept - TBD. As of current view - it could be embedding vector trajectory segment.

Each concept becomes a node in the global graph with:
 - authorship
 - vector representation
 - upstream parent concepts
 - novelty metadata

This lineage enables automated royalty allocation and downstream contribution tracing.

### Semantic State

The shared semantic state is a distributed graph containing:
 - concepts
 - lineage relationships
 - novelty scores
 - ownership records

The structure expands over time as new concepts are proposed and validated.

## Economic Layer

SLP incorporates a computationally grounded incentive structure.

### Publishing Cost

A fee proportional to compute and storage required to evaluate and integrate a submission. Discourages spam and low-signal content.

### Algorithmic Lineage

New concepts are linked automatically to their semantic parents, preventing citation fraud and enabling reproducible provenance.

### Royalties

Authors of high-novelty concepts receive ongoing micro-fees as downstream ideas reference or build upon their work.

### System Economics

A submission is rational only if expected royalty yield exceeds publication cost. This creates a natural quality filter without manual moderation.

### Infrastructure Node Rewards

Nodes providing inference, storage, and validation earn proportional rewards based on their role in maintaining the semantic state.

### Distributed Consensus

Nodes reach agreement on:
 - novelty scores
 - lineage links
 - reward distributions
 - embedding checkpoint updates

Consensus ensures global consistency and prevents manipulation of novelty scoring.

### Protocol Components

 1. Novelty Engine: Formal definition of conceptual distance and scoring.
 2. Lineage Model: Rules for authorship attribution and propagation.
 3. Concept Graph: Data structure for concepts, embeddings, and metadata.
 4. Consensus Rules: Validation, conflict resolution, and state synchronization.
 5. Economic Rules: Publishing fees, royalty mechanics, and node incentives.
 6. Security: Defenses against synthetic novelty attacks, concept squatting or hijacking.

## Technical Viability

Transformers enable fine-grained semantic understanding. A practical PoC can:
 - Extract hidden-state trajectories.
 - Compare segment-level distances.
 - Compute novelty relative to existing trajectories.
 - Scale to multimodal representations.
 - This low-level semantic comparison forms the backbone of SLP’s novelty diff.


### Goals of This Specification and PoC

 - Define the vision and requirements of the protocol.
 - Test technical viability and demand for the system on text based data.

## Status

Early-stage conceptual specification.
PoC draft.

## Running the Prototype (Docker)

Prerequisites:

- Docker
- Docker Compose v2

Build and start an interactive shell:

```bash
docker-compose build
docker-compose run --rm slp-core
```

You will see a shell prompt inside the container. Type any line of text and press Enter:

- The line is embedded and integrated.
- The system prints a novelty score and a parent.

Commands inside the shell:

- `/help` – show basic usage.
- `/exit` or `/quit` – exit the shell.

## Next steps
- Make trajectory segments matching and lineage


## Contributing

Contributions focused on specification clarity, edge cases, and protocol-level mechanics are welcome.
Questions, critiques, and proposals should be submitted as issues.
