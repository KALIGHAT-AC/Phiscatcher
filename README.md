# 📘 Phiscatcher — Phishing Traffic Analysis Using Wireshark

> A responsive web tool that investigates a user-supplied website URL, captures and analyses its observable network traffic, and presents evidence-based statistics to assess whether the site is likely phishing or legitimate.

## Overview

**Phiscatcher is a phishing-website detector, not a phishing simulator.** It does not create, host, or provide phishing pages.

A user submits an arbitrary URL—whether suspicious or known to be genuine. Phiscatcher validates and investigates that URL in a controlled browser workflow, observes available URL, domain, DNS, HTTP(S), redirect, TLS, and network-traffic signals, then produces a risk score, evidence, statistics, and a phishing-versus-legitimate verdict.

The verdict is an assessment based on observable indicators; it is not proof of malicious intent and should be reviewed alongside the supporting evidence.

## Workflow and Architecture

```text
User-supplied URL
        │
        ▼
URL validation and normalization
        │
        ├─────────────┬─────────────┬──────────────┐
        ▼             ▼             ▼              ▼
 URL/domain       DNS lookup     HTTP(S)      TLS/certificate
 feature scan                   and redirects    inspection
        │             │             │              │
        └─────────────┴──────┬──────┴──────────────┘
                              ▼
             Controlled browser investigation
             (Playwright; no form submission or credential entry)
                              │
                              ▼
                  Observable network traffic
                              │
                              ▼
                Packet capture and PCAP storage
                         (Scapy planned)
                              │
                              ▼
            Protocol statistics and PCAP analysis
       (Scapy plus Wireshark/TShark integration — TBD)
                              │
                              ▼
        Detection indicators → rules → risk score → verdict
                              │
                              ▼
     Dashboard, evidence, history, and optional live updates
```

### Important design decision: Wireshark and TShark

Wireshark is part of the intended analysis workflow and generated PCAP files should remain inspectable in it. The final programmatic integration—such as Scapy-only parsing, calling **TShark** for selected fields, or a hybrid approach—has **not yet been decided**. This README deliberately does not claim a final Wireshark-versus-TShark architecture.

## Planned Features

- URL entry, validation, normalization, and scan controls
- URL, hostname, domain, subdomain, port, path, and query-feature analysis
- DNS resolution and DNS-record observations
- HTTP/HTTPS response inspection and redirect-chain analysis
- TLS and certificate metadata inspection, where available
- Controlled browser visits with Playwright to observe page requests, resources, and redirects
- Packet capture, PCAP storage, and packet/protocol statistics
- DNS, TCP, HTTP, TLS, and IP traffic analysis from observable data
- Phishing indicators from URL, domain, DNS, HTTP(S), TLS, and traffic behaviour
- Rule engine, explainable evidence, risk scoring, and phishing/likely-legitimate verdicts
- Dashboard with protocol charts, traffic charts, packet views, alerts, timelines, and evidence panels
- Optional real-time scan statistics over WebSockets
- Scan history and capture-detail views; MongoDB remains optional/TBD
- ML model training and inference as an additional detection signal
- Unit, frontend, and integration testing
- Architecture, API, packet-analysis, and setup documentation

## Tech Stack

| Area | Planned technology |
| --- | --- |
| Frontend | React, Vite, Tailwind CSS, Lucide React |
| Backend | FastAPI (Python) |
| Browser investigation | Playwright |
| Packet capture | Scapy |
| Packet analysis | Wireshark; programmatic TShark/Scapy approach TBD |
| Visualisation | Chart.js |
| Data persistence | None initially; MongoDB optional/TBD |
| Detection | Rule-based indicators, risk scoring, model training/inference |
| Live updates | WebSockets (planned) |

## Project Structure

The following is the intended project layout. Names may evolve as the implementation is built.

```text
Phiscatcher/
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/{images,icons}/
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   ├── StatCard.jsx
│   │   │   ├── RiskScore.jsx
│   │   │   ├── TrafficChart.jsx
│   │   │   ├── ProtocolChart.jsx
│   │   │   ├── PacketTable.jsx
│   │   │   ├── DNSPanel.jsx
│   │   │   ├── HTTPPanel.jsx
│   │   │   ├── TLSPanel.jsx
│   │   │   ├── AlertPanel.jsx
│   │   │   ├── EvidencePanel.jsx
│   │   │   ├── Timeline.jsx
│   │   │   └── CaptureStatus.jsx
│   │   ├── pages/{Home,Dashboard,LiveAnalysis,CaptureHistory,CaptureDetails,Settings}.jsx
│   │   ├── services/{api,websocket}.js
│   │   ├── hooks/{useWebSocket,useAnalysis}.js
│   │   ├── utils/{formatters,risk,constants}.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/{routes_scan,routes_analysis,routes_history,routes_health}.py
│   │   ├── websocket/live_stream.py
│   │   ├── investigation/
│   │   │   ├── url_analyzer.py
│   │   │   ├── domain_analyzer.py
│   │   │   ├── dns_analyzer.py
│   │   │   ├── http_analyzer.py
│   │   │   ├── redirect_analyzer.py
│   │   │   ├── tls_analyzer.py
│   │   │   └── browser_scanner.py
│   │   ├── capture/{capture_manager,interface_detector,filters}.py
│   │   ├── analysis/{packet_analyzer,protocol_analyzer,dns_traffic_analyzer,tcp_analyzer,http_traffic_analyzer,tls_traffic_analyzer,ip_analyzer}.py
│   │   ├── detection/{indicators,rules,scoring,verdict}.py
│   │   ├── models/{packet,traffic,alert,analysis,capture,scan}.py
│   │   ├── database/{connection,repositories,schemas}.py  # optional/TBD
│   │   ├── services/{analysis_service,capture_service,threat_intel_service}.py
│   │   ├── config/settings.py
│   │   └── utils/{logger,timestamps,helpers}.py
│   ├── requirements.txt
│   └── .env.example
├── packet-captures/
│   ├── raw/                         # generated PCAP files; do not commit
│   └── processed/                   # derived scan data; do not commit sensitive data
├── wireshark/
│   ├── filters/{http,dns,tcp,tls}_filters.txt
│   └── profiles/
├── tests/
│   ├── backend/{test_capture,test_analysis,test_detection,test_scoring}.py
│   ├── frontend/
│   └── integration/test_pipeline.py
├── docs/
│   ├── architecture/{system-architecture,data-flow,detection-flow}.md
│   ├── wireshark/analysis-notes.md
│   └── API.md
├── scripts/{start_backend,start_capture,stop_capture,cleanup}.py
├── .gitignore
├── README.md
└── LICENSE
```

## Getting Started

### Prerequisites

- Git
- Node.js (current LTS recommended) and npm
- Python 3.10+ and pip
- A supported browser for Playwright
- Wireshark for PCAP inspection
- Npcap on Windows if required by the chosen capture configuration

> Packet capture can require administrator privileges and OS-specific configuration. Follow your operating system's security requirements and capture only traffic you are authorized to inspect.

### 1. Clone the repository

```bash
git clone https://github.com/KALIGHAT-AC/Phiscatcher.git
cd Phiscatcher
```

### 2. Set up the frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite development server normally runs at `http://localhost:5173`.

### 3. Set up the backend

In a second terminal:

```bash
cd backend
python -m venv venv
```

Activate the virtual environment:

```powershell
# Windows PowerShell
.\venv\Scripts\Activate.ps1
```

```bash
# macOS/Linux
source venv/bin/activate
```

Install dependencies and start FastAPI:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API normally runs at `http://127.0.0.1:8000`, with interactive API documentation at `http://127.0.0.1:8000/docs`.

### 4. Install the browser runtime

Once Playwright is included in the backend dependencies, install its browser binaries:

```bash
playwright install
```

Playwright's role is to visit and observe the **user-submitted URL** in a controlled browser session. It is not used to host a phishing page, simulate a login, or submit credentials.

### 5. Configure packet capture and analysis

- Install Wireshark to open and inspect generated `.pcap` files.
- Install/configure Npcap on Windows if the capture implementation requires it.
- Confirm that the selected capture interface and privileges are appropriate.
- Keep raw captures out of version control and handle them as potentially sensitive artifacts.

The exact automated analysis path (Scapy, TShark, or hybrid) is a project design decision still to be finalized.

### 6. Run a scan

1. Start the frontend and backend.
2. Open the frontend in your browser.
3. Enter an `http` or `https` website URL that you are authorized to investigate.
4. Start the scan and review the status, statistics, evidence, risk score, and verdict.
5. If enabled, inspect the generated PCAP in Wireshark and consult the scan history for prior results.

## Usage

Phiscatcher combines multiple classes of evidence:

```text
URL/domain signals + DNS observations + HTTP(S)/redirect behaviour
+ TLS metadata + browser-observed activity + PCAP/protocol statistics
→ indicators → rules/model signals → risk score → evidence-backed verdict
```

Examples of planned outputs include:

- normalized URL and destination information
- redirect chain and final destination
- DNS records and resolved addresses
- response/header and certificate metadata, where observable
- protocol and packet-count summaries
- triggered indicators with explanations
- risk band and phishing/likely-legitimate assessment

Encrypted HTTPS payloads must be treated correctly: the project can report observable metadata and traffic characteristics, but must not claim to read credentials or encrypted content merely from a PCAP.

## API and Real-Time Updates

The frontend is planned to communicate with FastAPI via REST endpoints under `backend/app/api/`. WebSocket support may stream scan progress, capture status, and live statistics to the dashboard. Endpoint contracts and event schemas will be documented in [`docs/API.md`](docs/API.md) as the API is implemented.

## Screenshots / Demo

Screenshots and a live demonstration will be added as the dashboard and scan workflow are implemented.

```text
[ Dashboard screenshot placeholder ]
[ Live analysis screenshot placeholder ]
[ Evidence and risk-score screenshot placeholder ]
```

## Safety and Authorized Use

Use Phiscatcher only for URLs, systems, networks, and traffic that you own or are explicitly authorized to assess. A submitted URL can cause a browser to contact external systems, and packet captures may contain sensitive metadata. Do not use the project to probe systems without permission, submit credentials, bypass controls, or collect data beyond the authorized scope.

Run browser investigations with appropriate isolation and avoid interacting with forms or downloads unless the project has an approved, safe procedure for doing so.

## Future Scope

- Finalize the Scapy/Wireshark/TShark integration design
- Add configurable capture filtering and safer browser isolation
- Add calibrated risk-score thresholds and evaluation datasets
- Add trained-model inference with explainable feature reporting
- Add optional MongoDB-backed scan history
- Add threat-intelligence integrations subject to approved data sources
- Export scan reports and evidence bundles
- Add role-based access, retention controls, and privacy protections
- Expand automated test coverage and performance testing

## 👥 Team & Contributions

### Contributors

* **Frontend Development** →
* **Backend Development** →
* **Packet Capture & Analysis** →
* **Browser Automation** →
* **Threat Detection & Model Training** →
* **Documentation & Testing** →

### 🤝 Contribution Guidelines

Contributions are welcome.

For team development, contributors are encouraged to:

1. Clone the repository.
2. Create a dedicated branch.
3. Make the required changes.
4. Test the changes locally.
5. Commit the changes with a meaningful message.
6. Push the branch.
7. Open a Pull Request.
8. Wait for review before merging into `main`.

Example:

```bash
git checkout -b feature/your-feature
```

After making changes:

```bash
git add .
git commit -m "Add your feature"
git push origin feature/your-feature
```

Then create a Pull Request on GitHub.

---

## ⚠️ Disclaimer

Phiscatcher is intended strictly for:

- Educational purposes
- Cybersecurity research
- Controlled laboratory environments
- Authorized security testing
- Phishing-analysis demonstrations

All simulated credentials and traffic should be synthetic.

**Do not use this project to collect, intercept, or analyze credentials or network traffic belonging to users, systems, or organizations without explicit authorization.**

---

## 📄 License

This project is licensed under the terms specified in the project's [LICENSE](./LICENSE) file.

---

<p align="center">

### 🛡️ Phiscatcher

*Capture the traffic. Analyse the evidence. Catch the phish.*

</p>
