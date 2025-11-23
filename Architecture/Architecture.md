# Project: Cortex5 (AI Hedge Fund)
## Mission: Generate Funds for Dhitva.foundation

---

## 1. ASCII Architecture Diagram

```ascii
                                      +---------------------------------------------------------------+
                                      |                   USER / ADMIN DASHBOARD                      |
                                      |        (Monitoring, Strategy Config, Portfolio View)          |
                                      +-------------------------------+-------------------------------+
                                                                      |
                                                                      v
+-----------------------------------------------------------------------------------------------------+
|                                          AI AGENT ORCHESTRATION LAYER                               |
|                                     (Framework: LangGraph / AutoGen)                                |
|                                                                                                     |
|  +-------------------+    +-------------------+    +-------------------+    +-------------------+   |
|  | 1. Data Engineer  |    | 2. Sentiment      |    | 3. Quant Analyst  |    | 4. Risk Manager   |   |
|  |      Agent        |    |    Agent          |    |      Agent        |    |      Agent        |   |
|  | (Ingest/Clean)    |<-->| (News/Social)     |<-->| (Model/Backtest)  |<-->| (Compliance/Size) |   |
|  +---------+---------+    +---------+---------+    +---------+---------+    +---------+---------+   |
|            |                        |                        |                        |             |
|            |                        |                        |                        |             |
|            v                        v                        v                        v             |
|  +----------------------------------------------------------------------------------------------+   |
|  |                                  5. Execution Trader Agent                                   |   |
|  |                       (Signal Aggregation & Order Execution)                                 |   |
|  +------------------------------------------+---------------------------------------------------+   |
+---------------------------------------------|-------------------------------------------------------+
                                              |
                                              v
+-----------------------------------------------------------------------------------------------------+
|                                     DATA & PROCESSING LAYER                                         |
+-----------------------------------------------------------------------------------------------------+
|                                                                                                     |
|  [Live Data Stream]                 [Historical Data]                  [News & Social Feeds]        |
|         |                                   |                                    |                  |
|         v                                   v                                    v                  |
|  +-------------+                    +---------------+                    +----------------+         |
|  | Kafka/Redpanda |<----------------|  Batch ETL    |                    |  Vector Ingestion |      |
|  | (Streaming) |                    |  (Airflow)    |                    |  (Embeddings)     |      |
|  +------+------+                    +-------+-------+                    +--------+-------+         |
|         |                                   |                                     |                 |
|         |                                   v                                     v                 |
|         |                        +---------------------+              +-----------------------+     |
|         +----------------------->|    HYBRID DB        |<-------------|   Vector DB (Qdrant)  |     |
|                                  | (Timescale + SQL)   |              | (News/Sentiment/RAG)  |     |
|                                  +---------------------+              +-----------------------+     |
|                                                                                                     |
+-----------------------------------------------------------------------------------------------------+
                                              |
                                              v
+-----------------------------------------------------------------------------------------------------+
|                                     MODEL TRAINING & INFERENCE                                      |
+-----------------------------------------------------------------------------------------------------+
|                                                                                                     |
|  +-----------------------+       +-------------------------+       +-----------------------------+  |
|  |    Local Inference    |       |   Model Registry        |       |      Training Pipeline      |  |
|  | (Ollama / Llama.cpp)  |<----->| (MLflow / S3)           |<----->| (PyTorch / Scikit-Learn)    |  |
|  |   * 7B Param Models   |       | * Versioned Models      |       | * Finetuning (LoRA/QLoRA)   |  |
|  +-----------------------+       +-------------------------+       +-----------------------------+  |
|                                                                                                     |
+-----------------------------------------------------------------------------------------------------+
                                              |
                                              v
                                   +---------------------+
                                   |   AWS DEPLOYMENT    |
                                   | (EKS / EC2 / RDS)   |
                                   +---------------------+
```

---

## 2. Tech Stack Used

### **Core AI & Agents**
*   **Agent Framework**: **LangGraph** (recommended for stateful, graph-based workflows) or **CrewAI** (for role-based orchestration).
*   **LLM Inference (Local)**: **Ollama** (for ease of use) and **Llama.cpp** (for performance/quantization).
*   **Models**:
    *   **General/Reasoning**: Llama-3-8B-Instruct, Mistral-7B-v0.3.
    *   **Financial Specialized**: FinGPT, FinMA (7B variants).
    *   **Embedding Model**: BAAI/bge-m3 or Nomic-embed-text (running locally).

### **Data Storage (Hybrid Approach)**
*   **Vector Database**: **Qdrant** (Best for performance/scale, Rust-based).
*   **Time-Series Database**: **TimescaleDB** (PostgreSQL extension) - ideal for OHLCV and tick data.
*   **Relational Database**: **PostgreSQL** (for transactional data, user info, trade logs).
*   **Object Storage**: **AWS S3** (Data Lake for raw historical files, model artifacts).

### **Data Processing & Pipelines**
*   **Streaming**: **Apache Kafka** or **Redpanda** (C++ alternative, lighter resource footprint).
*   **Batch Processing**: **Apache Spark** (if data > TBs) or **Polars/Pandas** (for single-node efficiency).
*   **Orchestration**: **Apache Airflow** or **Prefect** (Modern, pythonic).

### **Machine Learning & MLOps**
*   **Training/Finetuning**: **PyTorch**, **Hugging Face Transformers**, **PEFT** (for LoRA/QLoRA efficient finetuning).
*   **Experiment Tracking**: **MLflow** (Industry standard).
*   **Feature Store**: **Feast** (Open source feature store).
*   **Live Algorithms**:
    1.  **XGBoost/LightGBM** (Gradient Boosting for structured market data).
    2.  **LSTM/GRU** (Recurrent NNs for sequence prediction).
    3.  **Transformer-based Time Series** (TimeGPT or similar small variants).

### **Infrastructure & Deployment**
*   **Cloud Provider**: **AWS**.
*   **Containerization**: **Docker** & **Kubernetes (EKS)**.
*   **Infrastructure as Code**: **Terraform**.
*   **CI/CD**: **GitHub Actions**.
*   **Monitoring**: **Prometheus** (Metrics) & **Grafana** (Dashboards).

### **Application Layer**
*   **Backend API**: **FastAPI** (High performance Python).
*   **Frontend**: **Next.js** (React framework) + **TailwindCSS** (Styling).
