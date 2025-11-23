# Cortex 5 - Day 1 Learnings: The Foundation of an AI Hedge Fund

## 📝 Executive Summary
Day 1 was focused on **Genesis**—creating the universe in which our AI agents will live. We successfully established the infrastructure (Docker, Kubernetes), defined the "Council of Agents" architecture using LangGraph, and implemented the initial communication flow. Crucially, we pivoted from a cloud-dependent LLM (OpenAI) to a local, controllable inference engine (Ollama), ensuring data privacy and cost control.

---

## 1. The "Council of Agents" Architecture
**Concept**: A multi-agent system where specialized agents collaborate to make trading decisions. We moved away from a monolithic LLM approach to a distributed "Micro-Cognition" architecture.

### ASCII Visualization: The Agent Workflow
```ascii
                                    [START]
                                       |
                                       v
+-----------------+           +-----------------+
|   Data Agent    |---------->| Sentiment Agent |
| (Yahoo Finance) |  (Data)   |    (Qdrant)     |
+-----------------+           +-----------------+
                                       |
                                       v
                              +-----------------+
                              |   Quant Agent   |
                              |   (Tech Analysis)|
                              +-----------------+
                                       |
                                       v
                              +-----------------+
                              |    Risk Agent   |
                              |  (Gatekeeper)   |
                              +-----------------+
                                       |
                                       v
                              +-----------------+
                              | Execution Agent |
                              |     (Trade)     |
                              +-----------------+
                                       |
                                       v
                                     [END]
```

**Key Learnings**:
*   **State Management**: The `AgentState` (defined in `src/state.py`) is the "blood" of the system, carrying market data, sentiment scores, and trade signals between agents.
*   **Circular Dependencies**: We learned that defining state in the same file as the graph can lead to circular imports when agents need to reference the state. Solution: Extract `AgentState` to a dedicated `src/state.py`.

---

## 2. Local LLM Inference (Ollama Integration)
**Concept**: Owning the "Brain". We replaced OpenAI with Ollama to run models locally.

**The Pivot**:
*   Initially planned for OpenAI GPT-4.
*   Switched to **Ollama** for local control.
*   Attempted `gemma3:latest` but found it lacked tool-calling support.
*   Standardized on `llama3.2:3b` which supports tool usage effectively.

### ASCII Visualization: Inference Stack
```ascii
+--------------------------------------------------+
|                  Application Layer               |
|  [LangChain / LangGraph] --> [ChatOllama Class]  |
+--------------------------------------------------+
                        |
                        v (HTTP POST /api/chat)
+--------------------------------------------------+
|                 Docker Container                 |
|  [Ollama Service (Port 11434)]                   |
|           |                                      |
|           v                                      |
|    [Model: llama3.2:3b]                          |
+--------------------------------------------------+
```

**Key Learnings**:
*   **Model Selection Matters**: Not all LLMs are created equal. For agentic workflows, **Tool Calling** support is non-negotiable.
*   **Configuration**: Centralizing model config in `.env` allows for hot-swapping "brains" without code changes.

---

## 3. Hybrid Database & Infrastructure
**Concept**: Polyglot Persistence. We set up a hybrid storage layer.

*   **TimescaleDB**: For rigid, high-frequency time-series data (Stock Prices).
*   **Qdrant**: For fluid, high-dimensional vector data (News Sentiment).

### ASCII Visualization: Infrastructure Map
```ascii
[Host Machine]
      |
      +--- [Docker Compose Network: hedge-net]
                |
                +--- [Service: timescaledb] (Port 5432)
                |
                +--- [Service: qdrant]      (Port 6333)
                |
                +--- [Service: ollama]      (Port 11434)
```

**Key Learnings**:
*   **Dev-Prod Parity**: Using `kind` (Kubernetes in Docker) allows us to simulate a full K8s cluster locally, ensuring that our deployment manifests are battle-tested before ever touching a cloud provider.

---

## 4. What We Achieved
1.  **Codebase Scaffolding**: Python project structure, linting (`ruff`), and dependency management.
2.  **Infrastructure as Code**: `docker-compose.yml` and K8s manifests.
3.  **Agent Implementation**: 5 functional agents with defined roles and tools.
4.  **Verification**: Successfully ran the full agent loop using local LLMs.

## 5. Next Steps (Day 2 Preview)
*   **Brain Transplant**: Give the agents real logic. Currently, they are "hollow shells" with mocked tools.
*   **Data Pipeline**: Connect the Data Agent to real Yahoo Finance data and store it in TimescaleDB.
*   **Memory**: Implement the RAG pipeline for the Sentiment Agent using Qdrant.
