# Cortex 5 - Day 1 Learnings: The Foundation of an AI Hedge Fund
## Interview Preparation Guide

**Objective**: Translate the technical work of Day 1 into articulate, high-level concepts suitable for a System Design or AI Engineering interview.

---

## 1. The "Council of Agents" Pattern
**Concept**: Instead of one giant LLM trying to do everything, we split responsibilities into specialized "Agents". This mimics a real human organization.

**Interview Soundbite**: *"I implemented a Multi-Agent System using LangGraph, where state is shared but execution is distributed. It's like a microservices architecture, but for cognition."*

### ASCII Visualization: The State Graph
```ascii
       [ Shared State Memory (The "Table") ]
       | Market Data | Sentiment | Signals |
       +-----------------------------------+
                        ^
                        | (Read/Write)
      +-----------------+-----------------+
      |                 |                 |
+-----+-----+     +-----+-----+     +-----+-----+
| Data Agent|     | Quant     |     | Risk      |
| (Fetcher) |     | Agent     |     | Agent     |
+-----------+     +-----------+     +-----------+
      |                 |                 |
[Yahoo Finance]   [Math Models]    [Rule Engine]
```

**Key Takeaway**:
*   **Nodes**: The Agents (Compute).
*   **Edges**: The flow of control (Workflow).
*   **State**: The context passed between them (Memory).

---

## 2. Hybrid Database Architecture
**Concept**: Different data types require different storage engines. One size does not fit all.

**Interview Soundbite**: *"I chose a hybrid approach: TimescaleDB for high-frequency market data because of its compression and time-series optimizations, and Qdrant for semantic search on news because of its efficient HNSW index."*

### ASCII Visualization: The Data Lakehouse
```ascii
          [ Application Layer ]
                    |
        +-----------+-----------+
        |                       |
        v                       v
+---------------+       +---------------+
|  TimescaleDB  |       |    Qdrant     |
| (Relational)  |       |   (Vector)    |
+---------------+       +---------------+
| time | price  |       | vector | meta |
| 10:00| 150.20 |       | [0.1..]| "CEO"|
| 10:01| 150.25 |       | [0.9..]| "Buy"|
+---------------+       +---------------+
        ^                       ^
        |                       |
   [Structured]           [Unstructured]
   (Ticks, OHLCV)         (News, Tweets)
```

**Key Takeaway**:
*   **SQL (Timescale)**: Exact, aggregatable, time-ordered.
*   **Vector (Qdrant)**: Fuzzy, semantic, similarity-based.

---

## 3. Local Kubernetes (Kind) vs. Cloud
**Concept**: Simulating a production environment locally ensures "Dev-Prod Parity".

**Interview Soundbite**: *"To ensure deployment readiness without incurring cloud costs, I used Kind (Kubernetes in Docker). This allows me to define standard K8s manifests (Deployments, Services, PVCs) that can be applied to AWS EKS later with zero changes."*

### ASCII Visualization: Kind Cluster
```ascii
+--------------------------------------------------+
|                  HOST MACHINE                    |
|                                                  |
|  +--------------------------------------------+  |
|  |             Docker Container               |  |
|  |  +--------------------------------------+  |  |
|  |  |           Kind Node (K8s)            |  |  |
|  |  |                                      |  |  |
|  |  |  [Pod: API]  [Pod: DB]  [Pod: UI]    |  |  |
|  |  |      |           |          |        |  |  |
|  |  +------+-----------+----------+--------+  |  |
|  |         |           |          |           |  |
|  +---------|-----------|----------|-----------+  |
|            |           |          |              |
|         Port 80    Port 5432   Port 3000         |
+--------------------------------------------------+
```

**Key Takeaway**:
*   **Kind**: Runs K8s nodes *inside* Docker containers.
*   **Port Mapping**: Bridges the container world to your localhost.

---

## 4. Vibe Coding & Agentic Workflow
**Concept**: Moving from "Syntax" to "Intent".

**Interview Soundbite**: *"I utilized an Agent-First development workflow. Instead of writing boilerplate, I defined the 'Vibe' (Intent/Spec) and orchestrated AI agents to generate the implementation. My role shifted from 'Typist' to 'Architect' and 'Reviewer'."*

**The Loop**:
1.  **Prompt**: "Create a Risk Agent that rejects trades > 2%."
2.  **Generate**: AI writes the Python class.
3.  **Review**: Human checks logic.
4.  **Refine**: "Add a check for volatility too."

---

## 5. What We Learned Today (Summary)
1.  **Infrastructure is Code**: We didn't click buttons; we wrote Docker Compose and K8s manifests.
2.  **State is King**: In AI agents, managing the `State` object is more important than the prompt itself.
3.  **Separation of Concerns**: Data ingestion is separate from Analysis, which is separate from Execution.

**Next Steps**: Tomorrow, we fill these empty vessels (Agents) with real logic and data.
