# Graph Runtime

## Backend selection

If `NEO4J_URI`, `NEO4J_USERNAME`, and `NEO4J_PASSWORD` are present and
connectivity succeeds, `Neo4jGraphRepository` is selected. Otherwise the
runtime uses `NETWORKX_FALLBACK` when enabled and records the reason.

## Real Neo4j operations

The adapter executes parameterized Cypher to:

- merge observed entities, devices, and transfers;
- detect accounts sharing a device;
- count distinct senders to a shared beneficiary/mule candidate;
- find return paths for circular transfers;
- find dense connected transfer subgraphs as fraud-ring candidates;
- export observed nodes/relationships to the dashboard.

No graph endpoint returns a bundled mock topology. The dashboard renders the
actual `/graph/topology` response and displays its backend/status.

## Health and failure

`/health/ready` requires an available Neo4j backend and available models.
Connectivity/query exceptions become explicit failed graph results. NetworkX
results are labelled fallback, not Neo4j.

## Validation result

Neo4j credentials were not present. A temporary local Docker validation was
attempted, but the Neo4j image could not be downloaded after repeated external
registry/CDN TLS handshake timeouts. Real Cypher execution is therefore an open
deployment gate. NetworkX evidence queries and explicit Neo4j-offline behavior
are covered by tests.

