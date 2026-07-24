from __future__ import annotations

import threading
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any

import networkx as nx

from .config import PlatformSettings, platform_settings


ROOT = Path(__file__).resolve().parents[2]
GRAPHSAGE_MODEL = ROOT / "graph" / "models" / "graphsage.pt"
GRAPHSAGE_METADATA = ROOT / "graph" / "models" / "metadata.json"


def graphsage_status() -> dict[str, Any]:
    if not GRAPHSAGE_MODEL.exists() or not GRAPHSAGE_METADATA.exists():
        return {
            "status": "UNAVAILABLE",
            "model": None,
            "version": None,
            "reason": "GRAPHSAGE_ARTIFACT_NOT_CONFIGURED",
        }
    return {
        "status": "AVAILABLE",
        "model": str(GRAPHSAGE_MODEL),
        "version": GRAPHSAGE_METADATA.stat().st_mtime_ns,
        "reason": None,
    }


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
        default_factory=graphsage_status
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

    def topology(self, limit: int = 500) -> dict[str, Any]:
        with self._lock:
            nodes = [
                {"id": str(node_id), **dict(data)}
                for node_id, data in list(self.graph.nodes(data=True))[:limit]
            ]
            allowed = {node["id"] for node in nodes}
            links = [
                {
                    "source": str(source),
                    "target": str(target),
                    **dict(data),
                }
                for source, target, data in self.graph.edges(data=True)
                if str(source) in allowed and str(target) in allowed
            ][:limit]
        return {"nodes": nodes, "links": links}


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
            if params["subject_id"]:
                row = session.run(
                    """
                    MATCH (subject:Entity {id: $subject_id})
                    MATCH (subject)-[:TRANSFERRED_TO*1..4]-(member:Entity)
                    WITH collect(DISTINCT member) + subject AS members
                    UNWIND members AS source
                    MATCH (source)-[edge:TRANSFERRED_TO]->(target)
                    WHERE target IN members
                    WITH members, count(DISTINCT edge) AS edge_count
                    WHERE size(members) >= 5 AND edge_count >= 5
                    RETURN [member IN members | member.id] AS member_ids,
                           edge_count
                    LIMIT 1
                    """,
                    subject_id=params["subject_id"],
                ).single()
                if row:
                    members = sorted(set(row["member_ids"]))
                    findings.append(
                        GraphFinding(
                            "FRAUD_RING_CANDIDATE",
                            "HIGH",
                            members,
                            [
                                {
                                    "node_count": len(members),
                                    "transfer_edge_count": row["edge_count"],
                                }
                            ],
                        )
                    )
        return findings

    def topology(self, limit: int = 500) -> dict[str, Any]:
        with self.driver.session() as session:
            rows = session.run(
                """
                MATCH (source)-[relationship]->(target)
                RETURN coalesce(source.id, elementId(source)) AS source_id,
                       labels(source)[0] AS source_kind,
                       coalesce(target.id, elementId(target)) AS target_id,
                       labels(target)[0] AS target_kind,
                       type(relationship) AS relation,
                       relationship.amount AS amount,
                       relationship.transaction_id AS transaction_id
                LIMIT $limit
                """,
                limit=max(1, min(limit, 2_000)),
            )
            node_map: dict[str, dict[str, Any]] = {}
            links: list[dict[str, Any]] = []
            for row in rows:
                source = str(row["source_id"])
                target = str(row["target_id"])
                node_map[source] = {"id": source, "kind": row["source_kind"]}
                node_map[target] = {"id": target, "kind": row["target_kind"]}
                links.append(
                    {
                        "source": source,
                        "target": target,
                        "relation": row["relation"],
                        "amount": row["amount"],
                        "transaction_id": row["transaction_id"],
                    }
                )
        return {"nodes": list(node_map.values()), "links": links}


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
        try:
            connected = self.repository.verify_connectivity()
        except Exception:
            connected = False
        return {
            "status": "AVAILABLE" if connected else "FAILED",
            "backend": self.repository.backend_name,
            "neo4j_configured": bool(self.settings.neo4j_uri),
            "fallback_reason": self.error_code,
            "graphsage": graphsage_status(),
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
                graphsage=graphsage_status(),
            )
        except Exception:
            return GraphResult(
                status="FAILED",
                backend=self.repository.backend_name,
                latency_ms=round((time.perf_counter() - started) * 1000.0, 3),
                error_code="GRAPH_QUERY_FAILED",
                graphsage=graphsage_status(),
            )

    def topology(self, limit: int = 500) -> dict[str, Any]:
        started = time.perf_counter()
        try:
            data = self.repository.topology(limit)
            return {
                "status": (
                    "FALLBACK"
                    if self.repository.backend_name == "NETWORKX_FALLBACK"
                    else "EXECUTED"
                ),
                "backend": self.repository.backend_name,
                "graphsage": graphsage_status(),
                "latency_ms": round((time.perf_counter() - started) * 1000.0, 3),
                **data,
            }
        except Exception:
            return {
                "status": "FAILED",
                "backend": self.repository.backend_name,
                "graphsage": graphsage_status(),
                "latency_ms": round((time.perf_counter() - started) * 1000.0, 3),
                "error_code": "GRAPH_TOPOLOGY_QUERY_FAILED",
                "nodes": [],
                "links": [],
            }


graph_runtime = GraphRuntime()
