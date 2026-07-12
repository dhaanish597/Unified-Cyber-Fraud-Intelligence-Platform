# Architecture: Built Slice vs. Production Layer

This diagram illustrates the current "built slice" (what is implemented in this repository) versus the full "production layer" (what would be deployed in a live bank environment).

```mermaid
flowchart TD
    %% Styling
    classDef built fill:#e6f3ff,stroke:#0066cc,stroke-width:2px,color:#000
    classDef deck fill:#f9f9f9,stroke:#999,stroke-width:2px,stroke-dasharray: 5 5,color:#555
    classDef core fill:#ffe6e6,stroke:#cc0000,stroke-width:2px,color:#000

    %% Production / Deck-Only Layer
    subgraph Prod["Production Layer (Deck-Only)"]
        direction TB
        SIEM["Bank SIEM (Splunk/Elastic)\n(Raw Cyber Logs)"]:::deck
        CoreBanking["Core Banking System\n(Live Transactions)"]:::deck
        Kafka["Kafka Event Stream\n(Real-time Data Bus)"]:::deck
        Hadoop["Data Lake\n(Historical Storage)"]:::deck
        
        SIEM -->|Cyber Alerts| Kafka
        CoreBanking -->|Txn Events| Kafka
        Kafka --> Hadoop
    end

    %% Built Slice
    subgraph Built["Built Slice (This Repository)"]
        direction TB
        
        subgraph Data["Data Generation & Graph (data/ & graph/)"]
            PaySim["PaySim Simulator\n(Synthesized Txns)"]:::built
            CyberOverlay["Cyber Overlay\n(Injected Compromise Flags)"]:::built
            GraphEngine["NetworkX Graph\n(PageRank, Centrality)"]:::built
            
            PaySim --> CyberOverlay
            CyberOverlay --> GraphEngine
        end
        
        subgraph ML["Machine Learning Pipeline (ml/)"]
            LGBM["LightGBM\n(Supervised Fraud Model)"]:::built
            IsoForest["Isolation Forest\n(Unsupervised Anomaly Model)"]:::built
            Fusion["Fusion Logic\n(Feature Concatenation)"]:::built
            
            GraphEngine --> Fusion
            CyberOverlay --> Fusion
            Fusion --> LGBM
            Fusion --> IsoForest
        end
        
        subgraph Serving["Serving Layer (api/ & web/)"]
            RiskAPI["FastAPI Risk Engine\n(Inference API)"]:::core
            Dashboard["React/Vite Dashboard\n(Fraud Ops UI)"]:::built
            
            LGBM --> RiskAPI
            IsoForest --> RiskAPI
            RiskAPI <-->|REST / JSON| Dashboard
        end
    end

    %% Connections across layers
    Kafka -.->|Extract/Load| PaySim
    Hadoop -.->|Batch Training| ML
```
