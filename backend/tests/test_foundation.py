import asyncio

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.investigation.orchestrator import InvestigationOrchestrator
from app.main import create_app
from app.schemas.analysis import AnalysisSession


class BlockingOrchestrator(InvestigationOrchestrator):
    async def run(self, session: AnalysisSession, cancellation_event: asyncio.Event) -> None:
        await cancellation_event.wait()


def make_client(*, timeout: float = 1, max_concurrent: int = 2, retention: float = 3600, orchestrator=None) -> TestClient:
    return TestClient(create_app(Settings(
        analysis_timeout_seconds=timeout,
        max_concurrent_analyses=max_concurrent,
        session_retention_seconds=retention,
    ), orchestrator))


def test_startup_health_and_openapi() -> None:
    with make_client() as client:
        assert client.get("/api/health").json()["status"] == "ok"
        assert client.get("/openapi.json").status_code == 200


def test_url_validation_and_status_lookup() -> None:
    with make_client(orchestrator=BlockingOrchestrator()) as client:
        assert client.post("/api/analysis", json={"target_url": "ftp://example.com"}).status_code == 422
        response = client.post("/api/analysis", json={"target_url": "https://example.com/path"})
        assert response.status_code == 202
        analysis_id = response.json()["analysis_id"]
        assert response.json()["status"] == "queued"
        assert client.get(f"/api/analysis/{analysis_id}").json()["analysis_id"] == analysis_id
        assert client.get("/api/analysis/not-real").status_code == 404


def test_cancellation_and_websocket_event_history() -> None:
    with make_client(orchestrator=BlockingOrchestrator()) as client:
        analysis_id = client.post("/api/analysis", json={"target_url": "https://example.com"}).json()["analysis_id"]
        with client.websocket_connect(f"/api/analysis/{analysis_id}/ws") as websocket:
            event = websocket.receive_json()
            assert event["analysis_id"] == analysis_id
            assert event["event_type"] in {"status_changed", "analysis_started"}
            cancelled = client.post(f"/api/analysis/{analysis_id}/cancel")
            assert cancelled.status_code == 200
            assert cancelled.json()["status"] == "cancelled"
            event_types = [websocket.receive_json()["event_type"] for _ in range(2)]
            assert "analysis_cancelled" in event_types


def test_timeout() -> None:
    with make_client(timeout=0.01, orchestrator=BlockingOrchestrator()) as client:
        analysis_id = client.post("/api/analysis", json={"target_url": "https://example.com"}).json()["analysis_id"]
        import time
        time.sleep(0.05)
        assert client.get(f"/api/analysis/{analysis_id}").json()["status"] == "timeout"


def test_concurrency_limit_leaves_extra_work_queued() -> None:
    with make_client(max_concurrent=1, orchestrator=BlockingOrchestrator()) as client:
        first = client.post("/api/analysis", json={"target_url": "https://one.example"}).json()["analysis_id"]
        second = client.post("/api/analysis", json={"target_url": "https://two.example"}).json()["analysis_id"]
        import time
        time.sleep(0.02)
        assert client.get(f"/api/analysis/{first}").json()["status"] == "running"
        assert client.get(f"/api/analysis/{second}").json()["status"] == "queued"


def test_expired_terminal_sessions_are_cleaned_up() -> None:
    with make_client(retention=0, orchestrator=BlockingOrchestrator()) as client:
        analysis_id = client.post("/api/analysis", json={"target_url": "https://example.com"}).json()["analysis_id"]
        assert client.post(f"/api/analysis/{analysis_id}/cancel").status_code == 200
        import time
        time.sleep(0.02)
        client.post("/api/analysis", json={"target_url": "https://next.example"})
        assert client.get(f"/api/analysis/{analysis_id}").status_code == 404
