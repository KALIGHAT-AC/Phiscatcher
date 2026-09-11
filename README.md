# 📘 Phiscatcher — Phishing Traffic Analysis Using Wireshark

*A responsive web tool made to capture & analyse packets using Wireshark to conclude whether the site is for Phishing or not*

---

## 🌱 Overview

**Phiscatcher** is a cybersecurity-focused web application designed to analyse network traffic generated during controlled phishing simulations and identify indicators associated with phishing activity.

The project combines a simulated phishing environment, automated browser interaction, packet capture, Wireshark-based traffic analysis, statistical processing, real-time visualization, and threat detection mechanisms into a single analysis pipeline.

The system is designed for **educational, research, and authorized security-testing purposes**, using controlled environments and synthetic credentials rather than real user credentials.

### 🔄 Core Workflow

```text
Simulated Phishing Website
            ↓
     Browser Interaction
            ↓
       Network Traffic
            ↓
       Packet Capture
            ↓
          .pcap
            ↓
        Wireshark
            ↓
     Traffic Analysis
            ↓
   Threat Indicators / Risk
            ↓
       Visualization
            ↓
      Final Assessment
```

---

## 🛠️ Tech Stack

### 🎨 Frontend

- **React**
- **TailwindCSS**
- **Lucide React**
- **Chart.js**

### ⚙️ Backend

- **Python**
- **FastAPI**

### 🌐 Browser Automation

- **Playwright**

### 📡 Packet Capture

- **Scapy**

### 🔍 Packet Analysis

- **Wireshark**

### 🗄️ Database

- **MongoDB (Optional / Planned)**

> Database integration is currently optional and may be enabled depending on the final project requirements.

### 🤖 Detection & Intelligence

- **Model Training**
- Rule-based threat indicators
- Risk scoring
- Traffic-based phishing indicators

---

## ✨ Features

### 🎭 Simulated Phishing Environment

- Controlled phishing/login webpage
- Synthetic credential submission
- Simulated user interaction
- Safe environment for phishing analysis
- No requirement for real credentials

### 🌐 Automated Browser Interaction

- Automated browsing using **Playwright**
- Simulated login scenarios
- Normal browsing scenarios
- Automated traffic generation
- Repeatable testing scenarios

### 📡 Packet Capture

- Network interface detection
- Live packet capture using **Scapy**
- Configurable capture filters
- `.pcap` file generation
- Raw packet storage

### 🔍 Wireshark Analysis

- Wireshark-compatible PCAP files
- DNS traffic analysis
- TCP traffic analysis
- HTTP traffic analysis
- TLS traffic analysis
- IP traffic analysis
- Redirect analysis
- Session analysis

### 📊 Traffic Statistics

- Total packet count
- Protocol distribution
- Source/destination information
- Traffic volume
- Packet-level statistics
- Session statistics
- DNS statistics
- TCP statistics
- HTTP statistics
- TLS statistics

### 📈 Real-Time Visualization

- Real-time traffic statistics
- Live packet monitoring
- Real-time graphs
- Protocol distribution charts
- Traffic timeline
- Capture status monitoring

### 🚨 Phishing Detection

- Suspicious traffic indicators
- Rule-based detection
- Risk scoring
- Suspicious redirects
- Suspicious DNS behaviour
- HTTP-related indicators
- Network-level evidence
- Final phishing/security verdict

### 📋 Analysis Dashboard

- Overall risk score
- Traffic statistics
- Protocol charts
- Packet tables
- DNS information
- HTTP information
- TLS information
- Security alerts
- Evidence panels
- Traffic/session timeline

### 🧪 Testing & Research

- Automated test scenarios
- Backend analysis testing
- Detection testing
- Integration testing
- PCAP processing
- Model training support

---

## 📂 Project Structure

```text
Phishing-Traffic-Analysis/

├── frontend/
│   ├── public/
│   │   ├── favicon.ico
│   │   └── ...
│   ├── src/
│   │   ├── assets/
│   │   │   ├── images/
│   │   │   └── icons/
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
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── LiveAnalysis.jsx
│   │   │   ├── CaptureHistory.jsx
│   │   │   ├── CaptureDetails.jsx
│   │   │   └── Settings.jsx
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   └── websocket.js
│   │   ├── hooks/
│   │   │   ├── useWebSocket.js
│   │   │   └── useAnalysis.js
│   │   ├── utils/
│   │   │   ├── formatters.js
│   │   │   ├── risk.js
│   │   │   └── constants.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── routes_capture.py
│   │   │   ├── routes_analysis.py
│   │   │   ├── routes_history.py
│   │   │   └── routes_health.py
│   │   ├── websocket/
│   │   │   └── live_stream.py
│   │   ├── capture/
│   │   │   ├── capture_manager.py
│   │   │   ├── interface_detector.py
│   │   │   └── filters.py
│   │   ├── analysis/
│   │   │   ├── packet_analyzer.py
│   │   │   ├── protocol_analyzer.py
│   │   │   ├── dns_analyzer.py
│   │   │   ├── http_analyzer.py
│   │   │   ├── tls_analyzer.py
│   │   │   ├── ip_analyzer.py
│   │   │   ├── redirect_analyzer.py
│   │   │   └── credential_analyzer.py
│   │   ├── detection/
│   │   │   ├── indicators.py
│   │   │   ├── rules.py
│   │   │   ├── scoring.py
│   │   │   └── verdict.py
│   │   ├── models/
│   │   │   ├── packet.py
│   │   │   ├── traffic.py
│   │   │   ├── alert.py
│   │   │   ├── analysis.py
│   │   │   └── capture.py
│   │   ├── database/
│   │   │   ├── connection.py
│   │   │   ├── repositories.py
│   │   │   └── schemas.py
│   │   ├── services/
│   │   │   ├── analysis_service.py
│   │   │   ├── capture_service.py
│   │   │   └── threat_intel_service.py
│   │   ├── config/
│   │   │   └── settings.py
│   │   └── utils/
│   │       ├── logger.py
│   │       ├── timestamps.py
│   │       └── helpers.py
│   ├── requirements.txt
│   └── .env
│
├── simulator/
│   ├── website/
│   │   ├── public/
│   │   ├── src/
│   │   │   ├── components/
│   │   │   ├── pages/
│   │   │   ├── App.jsx
│   │   │   └── main.jsx
│   │   ├── package.json
│   │   └── ...
│   ├── playwright/
│   │   ├── browser.py
│   │   ├── scenarios/
│   │   │   ├── normal_login.py
│   │   │   ├── phishing_login.py
│   │   │   └── browsing.py
│   │   └── config.py
│   └── server/
│       └── ...
│
├── packet-captures/
│   ├── raw/
│   │   ├── capture_001.pcap
│   │   ├── capture_002.pcap
│   │   └── ...
│   └── processed/
│       ├── capture_001.json
│       └── ...
│
├── wireshark/
│   ├── filters/
│   │   ├── http_filters.txt
│   │   ├── dns_filters.txt
│   │   ├── tcp_filters.txt
│   │   └── tls_filters.txt
│   └── profiles/
│       └── ...
│
├── tests/
│   ├── backend/
│   │   ├── test_capture.py
│   │   ├── test_analysis.py
│   │   ├── test_detection.py
│   │   └── test_scoring.py
│   ├── frontend/
│   │   └── ...
│   └── integration/
│       └── test_pipeline.py
│
├── docs/
│   ├── architecture/
│   │   ├── system-architecture.md
│   │   ├── data-flow.md
│   │   └── detection-flow.md
│   ├── wireshark/
│   │   └── analysis-notes.md
│   └── API.md
│
├── scripts/
│   ├── start_backend.py
│   ├── start_capture.py
│   ├── stop_capture.py
│   └── cleanup.py
│
├── .gitignore
├── README.md
└── LICENSE
```

---

## 🚀 Getting Started

Follow the steps below to set up **Phiscatcher** locally.

### 1️⃣ Clone the Repository

Open a terminal and run:

```bash
git clone https://github.com/KALIGHAT-AC/Phiscatcher.git
```

Navigate into the project:

```bash
cd Phiscatcher
```

---

### 2️⃣ Frontend Setup

Navigate to the frontend directory:

```bash
cd frontend
```

Install the required dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173/
```

---

### 3️⃣ Backend Setup

Open another terminal and navigate to the backend:

```bash
cd backend
```

Create a Python virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment on Windows:

```bash
venv\\Scripts\\activate
```

Install the backend dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The backend will normally be available at:

```text
http://127.0.0.1:8000/
```

FastAPI's interactive API documentation can be accessed at:

```text
http://127.0.0.1:8000/docs
```

---

### 4️⃣ Playwright Setup

After installing the Python dependencies, install the Playwright browser binaries:

```bash
playwright install
```

The simulator can then be used to automate controlled browsing and login scenarios.

Available scenarios include:

```text
normal_login.py
phishing_login.py
browsing.py
```

---

### 5️⃣ Packet Capture Setup

Phiscatcher uses **Scapy** for packet capture.

On Windows, packet capture may require **Npcap** to be installed and configured correctly.

The capture system is responsible for:

```text
Network Interface
       ↓
Scapy Capture
       ↓
Packet Filtering
       ↓
PCAP Generation
       ↓
packet-captures/raw/
```

Depending on the operating-system configuration, packet capture may require elevated privileges.

---

### 6️⃣ Wireshark Setup

Install Wireshark on the system and make sure it can access the generated `.pcap` files.

Captured files will be stored under:

```text
packet-captures/raw/
```

Processed analysis data can be stored under:

```text
packet-captures/processed/
```

Wireshark filters used by the project are maintained under:

```text
wireshark/filters/
```

---

### 7️⃣ Running the Complete Project

A typical development setup will contain multiple running components:

```text
Terminal 1 → React Frontend
Terminal 2 → FastAPI Backend
Terminal 3 → Simulator / Playwright
Terminal 4 → Packet Capture / Analysis
```

The complete pipeline is:

```text
Frontend
   ↓
FastAPI
   ↓
Simulation
   ↓
Playwright
   ↓
Network Traffic
   ↓
Scapy
   ↓
PCAP
   ↓
Wireshark / Analysis Engine
   ↓
Detection & Risk Scoring
   ↓
Frontend Dashboard
```

---

## 🔗 API Integration

The React frontend communicates with the FastAPI backend through the services located in:

```text
frontend/src/services/
```

### REST API

API communication is handled through:

```text
frontend/src/services/api.js
```

Backend API routes are organized under:

```text
backend/app/api/
```

Current route modules include:

```text
routes_capture.py
routes_analysis.py
routes_history.py
routes_health.py
```

### WebSocket

Real-time traffic updates are handled through WebSockets.

Frontend:

```text
frontend/src/services/websocket.js
frontend/src/hooks/useWebSocket.js
```

Backend:

```text
backend/app/websocket/live_stream.py
```

This allows live capture information and analysis statistics to be streamed to the dashboard.

---

## 📊 Analysis Pipeline

Phiscatcher processes traffic through several analysis stages.

### Packet Analysis

```text
Captured Packet
      ↓
Packet Analyzer
      ↓
Protocol Detection
      ↓
Protocol-Specific Analysis
```

### Protocol Analysis

The backend provides dedicated analyzers for:

- DNS
- TCP
- HTTP
- TLS
- IP
- Redirects

### Threat Detection

Traffic characteristics are passed through:

```text
Indicators
    ↓
Rules
    ↓
Risk Scoring
    ↓
Verdict
```

The final assessment can use multiple network-level indicators rather than relying on a single packet or characteristic.

---

## 📈 Dashboard

The dashboard is designed to provide a centralized view of the captured traffic.

It can include:

- Overall risk score
- Packet count
- Traffic volume
- Protocol distribution
- Live traffic graphs
- Packet-level information
- DNS information
- HTTP information
- TLS information
- Security alerts
- Evidence
- Session timeline
- Capture status

---

## 🖼️ Screenshots & Demo

> 🚧 **SCREENSHOTS COMING SOON!**

Screenshots and demonstration material will be added once the frontend, dashboard, packet-capture pipeline, and analysis workflow are completed.

---

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
