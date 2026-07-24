from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any

import networkx as nx

from .config import PlatformSettings, platform_settings


@dataclass
class GraphFinding:
    finding_type: str
    severity: str
    entities: list[str]
    evidence: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "finding_type": self.finding_type,
            "severity": self.severity,
            "entities": self.entities,
            "evidence": self.evidence,
        }


@dataclass
class GraphResult:
    status: str
    backend: str
    findings: list[GraphFinding] = field(default_factory=list)
    latency_ms: float = 0.0
    error_code: str | None = None
    graph_version: str = "graph-schema-v1"
    graphsage: dict[str, Any] = field(
        default_factory=lambda: {
            "status": "UNAVAILABLE",
            "model": None,
            "version": None,
            "reason": "GRAPHSAGE_ARTIFACT_NOT_CONFIGURED",
        }
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "backend": self.backend,
            "findings": [finding.to_dict() for finding in self.findings],
            "latency_ms": self.latency_ms,
            "error_code": self.error_code,
            "graph_version": self.graph_version,
            "graphsage": self.graphsage,
        }


class NetworkXGraphRepository:
    backend_name = "NETWORKX_FALLBACK"

    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self._lock = threading.RLock()

    def verify_connectivity(self) -> bool:
        return True

    def observe(self, event: dict[str, Any]) -> None:
        user = str(event.get("user_id") or event.get("nameOrig") or "")
        account = str(event.get("nameOrig") or "")
        destination = str(event.get("nameDest") or "")
        device = str(event.get("device_id") or "")
        beneficiary = str(event.get("beneficiary_id") or destination)
        transaction_id = str(event.get("txn_id") or event.get("event_id") or "")
        amount = float(event.get("amount", 0.0) or 0.0)
        with self._lock:
            if user:
                self.graph.add_node(user, kind="user")
            if account:
                self.graph.add_node(account, kind="account")
                if user and user != account:
                    self.graph.add_edge(user, account, relation="OWNS")
            subject = account or user
            if subject and device:
                self.graph.add_node(device, kind="device")
                self.graph.add_edge(subject, device, relation="USES_DEVICE")
            if subject and beneficiary and beneficiary != subject:
                self.graph.add_node(beneficiary, kind="account")
                self.graph.add_edge(
                    subject,
                    beneficiary,
                    relation="TRANSFERRED_TO",
                    transaction_id=transaction_id,
                    amount=amount,
                )

    def analyze(self, event: dict[str, Any]) -> list[GraphFinding]:
        account = str(event.get("nameOrig") or event.get("user_id") or "")
        destination = str(event.get("nameDest") or event.get("beneficiary_id") or "")
        device = str(event.get("device_id") or "")
        findings: list[GraphFinding] = []
        with self._lock:
            if device and self.graph.has_node(device):
                users = sorted(
                    {
                        str(source)
                        for source, _, data in self.graph.in_edges(device, data=True)
                        if data.get("relation") == "USES_DEVICE"
                    }
                )
                if len(users) > 1:
                    findings.append(
                        GraphFinding(
                            "SHARED_DEVICE",
                            "HIGH",
                            [device, *users],
                            [{"device_id": device, "linked_accounts": users, "count": len(users)}],
                        )
                    )
            if destination and self.graph.has_node(destination):
                sources = sorted(
                    {
                        str(source)
                        for source, _, data in self.graph.in_edges(destination, data=True)
                        if data.get("relation") == "TRANSFERRED_TO"
                    }
                )
                if len(sources) >= 3:
                    findings.append(
                        GraphFinding(
                            "SHARED_BENEFICIARY",
                            "HIGH",
                            [destination, *sources],
                            [
                                {
                                    "beneficiary": destination,
                                    "source_accounts": sources,
                                    "count": len(sources),
                                }
                            ],
                        )
                    )
                    findings.append(
                        GraphFinding(
                            "MONEY_MULE_CANDIDATE",
                            "HIGH",
                            [destination, *sources],
                            [{"beneficiary": destination, "distinct_senders": len(sources)}],
                        )
                    )
            if account and destination and self.graph.has_node(destination):
                try:
                    return_path = nx.shortest_path(self.graph, destination, account)
                except (nx.NetworkXNoPath, nx.NodeNotFound):
                    return_path = []
                if return_path:
                    findings.append(
                        GraphFinding(
                            "CIRCULAR_TRANSFER",
                            "CRITICAL",
                            [account, destination, *map(str, return_path)],
                            [{"cycle_path": [account, *map(str, return_path)]}],
                        )
                    )
            transfer_graph = nx.DiGraph(
                (
                    source,
                    target,
                )
                for source, target, data in self.graph.edges(data=True)
                if data.get("relation") == "TRANSFERRED_TO"
            )
            if account and account in transfer_graph:
                component = next(
                    (
                        component
                        for component in nx.weakly_connected_components(transfer_graph)
                        if account in component
                    ),
                    set(),
                )
                if len(component) >= 5 and transfer_graph.subgraph(component).number_of_edges() >= 5:
                    findings.append(
                        GraphFinding(
                            "FRAUD_RING_CANDIDATE",
                            "HIGH",
                            sorted(map(str, component)),
                            [
                                {
                                    "node_count": len(component),
                                    "transfer_edge_count": transfer_graph.subgraph(component).number_of_edges(),
                                }
                            ],
                        )
                    )
        return findings


class Neo4jGraphRepository:
    backend_name = "NEO4J"

    def __init__(self, settings: PlatformSettings):
        from neo4j import GraphDatabase

        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_username, settings.neo4j_password),
            connection_timeout=2.0,
            max_connection_pool_size=20,
        )
        self.driver.verify_connectivity()

    def verify_connectivity(self) -> bool:
        self.driver.verify_connectivity()
        return True

    def observe(self, event: dict[str, Any]) -> None:
        params = {
            "subject_id": str(event.get("nameOrig") or event.get("user_id") or ""),
            "destination": str(event.get("nameDest") or event.get("beneficiary_id") or ""),
            "device_id": str(event.get("device_id") or ""),
            "txn_id": str(event.get("txn_id") or event.get("event_id") or ""),
            "amount": float(event.get("amount", 0.0) or 0.0),
        }
        if not params["subject_id"]:
            return
        with self.driver.session() as session:
            session.run(
                """
                MERGE (u:Entity {id: $subject_id})
                FOREACH (_ IN CASE WHEN $device_id = '' THEN [] ELSE [1] END |
                    MERGE (d:Device {id: $device_id})
                    MERGE (u)-[:USES_DEVICE]->(d))
                FOREACH (_ IN CASE WHEN $destination = '' THEN [] ELSE [1] END |
                    MERGE (b:Entity {id: $destination})
                    MERGE (u)-[t:TRANSFERRED_TO {transaction_id: $txn_id}]->(b)
                    SET t.amount = $amount)
                """,
                **params,
            ).consume()

    def analyze(self, event: dict[str, Any]) -> list[GraphFinding]:
        params = {
            "subject_id": str(event.get("nameOrig") or event.get("user_id") or ""),
            "destination": str(event.get("nameDest") or event.get("beneficiary_id") or ""),
            "device_id": str(event.get("device_id") or ""),
        }
        findings: list[GraphFinding] = []
        with self.driver.session() as session:
            if params["device_id"]:
                row = session.run(
                    """
                    MATCH (u:Entity)-[:USES_DEVICE]->(d:Device {id: $device_id})
                    RETURN collect(DISTINCT u.id) AS users
                    """,
                    device_id=params["device_id"],
                ).single()
                users = row["users"] if row else []
                if len(users) > 1:
                    findings.append(
                        GraphFinding(
                            "SHARED_DEVICE",
                            "HIGH",
                            [params["device_id"], *users],
                            [{"device_id": params["device_id"], "linked_accounts": users}],
                        )
                    )
            if params["destination"]:
                row = session.run(
                    """
                    MATCH (u:Entity)-[:TRANSFERRED_TO]->(b:Entity {id: $destination})
                    RETURN collect(DISTINCT u.id) AS users
                    """,
                    destination=params["destination"],
                ).single()
                users = row["users"] if row else []
                if len(users) >= 3:
                    findings.append(
                        GraphFinding(
                            "SHARED_BENEFICIARY",
                            "HIGH",
                            [params["destination"], *users],
                            [{"beneficiary": params["destination"], "source_accounts": users}],
                        )
                    )
                    findings.append(
                        GraphFinding(
                            "MONEY_MULE_CANDIDATE",
                            "HIGH",
                            [params["destination"], *users],
                            [{"beneficiary": params["destination"], "distinct_senders": len(users)}],
                        )
                    )
            if params["subject_id"] and params["destination"]:
                row = session.run(
                    """
                    MATCH path=(b:Entity {id: $destination})-[:TRANSFERRED_TO*1..5]->(u:Entity {id: $subject_id})
                    RETURN [node IN nodes(path) | node.id] AS path LIMIT 1
                    """,
                    **params,
                ).single()
                if row:
                    findings.append(
                        GraphFinding(
                            "CIRCULAR_TRANSFER",
                            "CRITICAL",
                            row["path"],
                            [{"cycle_path": row["path"]}],
                        )
                    )
        return findings


class GraphRuntime:
    def __init__(self, settings: PlatformSettings = platform_settings):
        self.settings = settings
        self.error_code: str | None = None
        if settings.neo4j_uri and settings.neo4j_username and settings.neo4j_password:
            try:
                self.repository = Neo4jGraphRepository(settings)
            except Exception:
                self.error_code = "NEO4J_CONNECTION_FAILED"
                if not settings.graph_fallback_enabled:
                    raise
                self.repository = NetworkXGraphRepository()
        else:
            self.error_code = "NEO4J_NOT_CONFIGURED"
            self.repository = NetworkXGraphRepository()

    def status(self) -> dict[str, Any]:
        return {
            "status": "AVAILABLE" if self.repository.verify_connectivity() else "FAILED",
            "backend": self.repository.backend_name,
            "neo4j_configured": bool(self.settings.neo4j_uri),
            "fallback_reason": self.error_code,
            "graphsage": {
                "status": "UNAVAILABLE",
                "reason": "GRAPHSAGE_ARTIFACT_NOT_CONFIGURED",
            },
        }

    def process(self, event: dict[str, Any]) -> GraphResult:
        started = time.perf_counter()
        try:
            self.repository.observe(event)
            findings = self.repository.analyze(event)
            return GraphResult(
                status="FALLBACK" if self.repository.backend_name == "NETWORKX_FALLBACK" else "EXECUTED",
                backend=self.repository.backend_name,
                findings=findings,
                latency_ms=round((time.perf_counter() - started) * 1000.0, 3),
                error_code=self.error_code,
            )
        except Exception:
            return GraphResult(
                status="FAILED",
                backend=self.repository.backend_name,
                latency_ms=round((time.perf_counter() - started) * 1000.0, 3),
                error_code="GRAPH_QUERY_FAILED",
            )


graph_runtime = GraphRuntime()
