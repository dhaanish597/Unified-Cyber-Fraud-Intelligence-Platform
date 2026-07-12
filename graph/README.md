# /graph

Graph schema, GraphSAGE training, centrality computation, and embedding export.

- GraphSAGE (PyTorch Geometric) trained on the Elliptic Bitcoin dataset — node embeddings +
  licit/illicit classification. Inductive: new nodes get embeddings without full retraining.
- Account/device/IP graph built from `/data/processed` — Neo4j Aura if `.env` has credentials,
  otherwise an in-memory `networkx` fallback. Code must detect and degrade gracefully.
- Centrality features per entity: PageRank, betweenness, Louvain community id.
- Exports an entity -> {centrality features, community, mule_cluster_flag} lookup consumed by the
  fusion risk engine in `/api`.

See root `CLAUDE.md` for the Neo4j-vs-networkx fallback rule.
