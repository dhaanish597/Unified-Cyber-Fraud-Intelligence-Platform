from __future__ import annotations

import asyncio
import json
import os
import statistics
import subprocess
import sys
import time
import tracemalloc
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from api.main import app
from api.platform.events import platform_event_broker


def percentile(values: list[float], percentile_value: int) -> float | None:
    if not values:
        return None
    return round(statistics.quantiles(values, n=100)[percentile_value - 1], 3)


async def broker_latency_samples(count: int = 30) -> list[float]:
    subscription = await platform_event_broker.subscribe("PERF_SESSION")
    samples: list[float] = []
    try:
        for index in range(count):
            started = time.perf_counter()
            await platform_event_broker.publish(
                {"msg_type": "pipeline_decision", "session_id": "PERF_SESSION", "index": index}
            )
            await subscription.queue.get()
            samples.append((time.perf_counter() - started) * 1000)
    finally:
        await platform_event_broker.unsubscribe(subscription.subscription_id)
    return samples


def main() -> None:
    tracemalloc.start()
    process_started = time.process_time()
    wall_started = time.perf_counter()
    client = TestClient(app)
    auth = client.post(
        "/auth/token",
        json={"client_id": "fusion-test", "client_secret": "fusion-test-local-only"},
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {auth}"}
    device_id = "performance-device"
    client.post(
        "/sdk/device",
        headers=headers,
        json={
            "device_id": device_id,
            "model": "performance-runner",
            "manufacturer": "local",
            "android_version": "14",
            "security_patch": "2026-07-01",
            "screen_lock_enabled": True,
            "root_detected": False,
            "emulator_detected": False,
            "frida_detected": False,
            "debugger_attached": False,
            "overlay_detected": False,
            "timezone": "UTC",
            "locale": "en",
        },
    ).raise_for_status()
    session = client.post(
        "/sdk/session/start",
        headers=headers,
        json={
            "app_id": "performance.runner",
            "tenant_id": "PERFORMANCE",
            "sdk_version": "performance",
            "user_id": "performance-user",
            "device_id": device_id,
            "environment": "TEST",
        },
    )
    session.raise_for_status()
    session_id = session.json()["session_id"]

    http_samples: list[float] = []
    pipeline_samples: list[float] = []
    threat_samples: list[float] = []
    graph_samples: list[float] = []
    model_samples: list[float] = []
    for index in range(40):
        started = time.perf_counter()
        response = client.post(
            "/sdk/request-decision",
            headers=headers,
            json={
                "session_id": session_id,
                "event_type": "TRANSFER_INITIATED",
                "amount": 1_000 + index,
                "beneficiary_id": f"performance-beneficiary-{index % 4}",
            },
        )
        response.raise_for_status()
        body = response.json()
        http_samples.append((time.perf_counter() - started) * 1000)
        pipeline_samples.append(body["timings"]["total_ms"])
        threat_samples.append(body["timings"]["threat_engine_ms"])
        graph_samples.append(body["timings"]["graph_engine_ms"])
        model_samples.append(body["timings"]["model_or_fallback_ms"])

    broker_samples = asyncio.run(broker_latency_samples())
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    wall_elapsed = time.perf_counter() - wall_started
    cpu_elapsed = time.process_time() - process_started
    cold_started = time.perf_counter()
    cold = subprocess.run(
        [sys.executable, "-c", "import api.main"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    cold_import_ms = (time.perf_counter() - cold_started) * 1000

    def size(path: Path) -> int | None:
        return path.stat().st_size if path.exists() else None

    results = {
        "measured_at_epoch": int(time.time()),
        "samples": len(http_samples),
        "backend_http_ms": {"p50": percentile(http_samples, 50), "p95": percentile(http_samples, 95)},
        "pipeline_ms": {"p50": percentile(pipeline_samples, 50), "p95": percentile(pipeline_samples, 95)},
        "threat_ms": {"p95": percentile(threat_samples, 95)},
        "graph_ms": {"p95": percentile(graph_samples, 95)},
        "model_or_fallback_ms": {"p95": percentile(model_samples, 95)},
        "broker_delivery_ms": {"p95": percentile(broker_samples, 95)},
        "cold_import_ms": round(cold_import_ms, 3),
        "cold_import_exit_code": cold.returncode,
        "python_peak_tracemalloc_bytes": peak_memory,
        "cpu_seconds": round(cpu_elapsed, 4),
        "wall_seconds": round(wall_elapsed, 4),
        "cpu_to_wall_ratio": round(cpu_elapsed / wall_elapsed, 4) if wall_elapsed else None,
        "android_artifact_bytes": {
            "debug_apk": size(ROOT / "fusion-reference-bank/app/build/outputs/apk/debug/app-debug.apk"),
            "release_apk": size(ROOT / "fusion-reference-bank/app/build/outputs/apk/release/app-release-unsigned.apk"),
            "release_aab": size(ROOT / "fusion-reference-bank/app/build/outputs/bundle/release/app-release.aab"),
        },
        "notes": [
            "Broker delivery measures server-side publish-to-subscriber queue latency.",
            "Network reconnect and offline queue timing require an emulator/device instrumentation environment.",
            "Memory is Python allocation peak, not operating-system RSS.",
        ],
    }
    output = ROOT / "performance-results.json"
    output.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
