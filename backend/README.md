# Phiscatcher backend foundation

This directory currently contains only the FastAPI foundation: configuration, API contracts, in-memory analysis sessions, lifecycle events, cancellation, timeout handling, concurrency control, and WebSocket subscriptions. It does not visit submitted URLs or produce analysis findings.

## Run

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

OpenAPI is at `http://127.0.0.1:8000/docs`.

## API

- `GET /api/health`
- `POST /api/analysis` with `{ "target_url": "https://example.com" }`
- `GET /api/analysis/{analysis_id}`
- `POST /api/analysis/{analysis_id}/cancel`
- `WS /api/analysis/{analysis_id}/ws`

WebSocket messages contain `event_type`, `analysis_id`, `timestamp`, `status`, `message`, and optional `payload`. Only genuine foundation lifecycle events are emitted.

## Tests

```powershell
cd backend
python -m pytest tests -q
```

The intentionally unimplemented work includes URL visits, Playwright, packet capture/PCAPs, Wireshark/TShark, protocol/DNS/HTTP/TLS analysis, detection, scoring, verdicts, ML, and persistence.
