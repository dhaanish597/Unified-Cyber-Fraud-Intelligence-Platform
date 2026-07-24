from __future__ import annotations

from pathlib import Path
import sys

from fastapi.routing import APIRoute, APIWebSocketRoute

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api.main import app
from api.platform.security import PUBLIC_PATHS, required_roles


def consumer(path: str) -> str:
    if path.startswith("/sdk/") or path.startswith("/banking/"):
        return "Android / Fusion SDK"
    if path.startswith("/graph/"):
        return "Pipeline / dashboard"
    if path.startswith("/threat"):
        return "Pipeline / threat dashboard"
    if path.startswith("/metrics"):
        return "Dashboard / QA"
    if path.startswith("/health") or path.startswith("/platform"):
        return "Operations"
    if path.startswith("/gateway"):
        return "Payment gateway"
    return "Dashboard / operator API"


def main() -> None:
    rows: list[tuple[str, str, str, str, str, str, str]] = []
    for route in app.routes:
        if isinstance(route, APIRoute):
            for method in sorted(route.methods - {"HEAD", "OPTIONS"}):
                public = route.path in PUBLIC_PATHS
                roles = "—" if public else ", ".join(sorted(required_roles(route.path)))
                rows.append(
                    (
                        method,
                        route.path,
                        "Public" if public else "Bearer JWT",
                        roles,
                        consumer(route.path),
                        "JSON or declared media type",
                        "4xx validation/auth; 5xx sanitized",
                    )
                )
        elif isinstance(route, APIWebSocketRoute):
            rows.append(
                (
                    "WS",
                    route.path,
                    "JWT query/header",
                    "admin, analyst, developer, operator, sdk",
                    "Android / dashboard",
                    "connection_ack + pipeline_decision",
                    "4401 auth; 4403 ownership",
                )
            )
    rows.sort(key=lambda row: (row[1], row[0]))
    lines = [
        "# Fusion Risk OS API Reference",
        "",
        "Generated from the executable FastAPI route table. Every authenticated REST response includes "
        "`X-Request-ID` and `X-Response-Time-Ms`. Pipeline responses additionally contain request, "
        "correlation, pipeline, acknowledgement, dependency status, and stage timing fields.",
        "",
        "| Method | Route | Authentication | Roles | Consumer | Response | Errors |",
        "|---|---|---|---|---|---|---|",
    ]
    lines.extend(
        f"| {method} | `{path}` | {auth} | {roles} | {use} | {response} | {errors} |"
        for method, path, auth, roles, use, response, errors in rows
    )
    lines.extend(
        [
            "",
            "## Latency contract",
            "",
            "- HTTP wall time: `X-Response-Time-Ms`.",
            "- Pipeline stage times: `timings.normalization_and_ingest_ms`, `threat_engine_ms`, "
            "`graph_engine_ms`, `model_or_fallback_ms`, and `total_ms`.",
            "- WebSocket delivery is measured by comparing the pipeline timestamp to client receipt time.",
            "",
            "## Error contract",
            "",
            "Authentication middleware returns `{\"error\":{\"code\":\"AUTHORIZATION_FAILED\","
            "\"message\":\"…\",\"request_id\":\"…\"}}`. Pydantic validation returns HTTP 422. "
            "Unavailable model and graph dependencies are represented in successful pipeline responses "
            "with explicit status/error fields rather than fabricated values.",
        ]
    )
    (ROOT / "API_REFERENCE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
