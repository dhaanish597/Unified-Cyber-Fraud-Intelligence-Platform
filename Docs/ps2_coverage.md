# PS2 Expected Outcomes to UI/API Mapping

This document maps the core value propositions and expected outcomes of the platform to their specific, functional implementations within the UI and API.

| Expected Outcome | API Endpoint / Logic | UI Element |
|---|---|---|
| **Quantify "Fusion Uplift"**<br/>Demonstrate that cyber + tabular beats tabular alone. | `ml/train.py` (Model Evaluation)<br/>`ml/metrics_report.md` | **Dashboard Headline Metric**: "Fusion Uplift: +0.09% Recall" & PR-AUC comparison cards. |
| **Real-time Risk Scoring**<br/>Score incoming transactions instantly. | `api/main.py` -> `POST /score`<br/>Executes LightGBM model. | **Live Feed & Transaction Details**: The primary risk score (0-100) on each row and in the modal. |
| **Explainable Fraud Decisions**<br/>Show why a transaction was flagged. | `api/main.py` -> `POST /score`<br/>Calculates local SHAP values per feature. | **SHAP Force Plot / Feature Importance Bar Chart**: Inside the transaction detail view (modal). |
| **Detect Zero-Day Anomalies**<br/>Catch new patterns unsupervised. | `api/main.py` -> `POST /score`<br/>Executes Isolation Forest model. | **"Anomaly Mode" Badge**: Highlighted when a transaction's behavior strictly deviates from the norm, even if the primary score is borderline. |
| **Graph Context & Link Analysis**<br/>Identify mules via network structure. | `graph/compute_graph.py`<br/>Generates PageRank & degree metrics. | **Network Graph Visualization**: The node-link diagram showing the transaction originator, destination, and multi-hop relationships. |
| **Cyber-Compromise Integration**<br/>Elevate risk when user is compromised. | `api/main.py` -> `POST /score`<br/>Uses `cyber_flag` feature. | **Cyber Alert Timeline**: The dedicated "SIEM Context" timeline showing device login anomalies or malware alerts in the side panel. |
