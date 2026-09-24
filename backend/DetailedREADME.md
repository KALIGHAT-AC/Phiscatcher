# Phiscatcher — Phishing Traffic Analysis Using Wireshark

# 📘 Phiscatcher — Phishing Traffic Analysis Using Wireshark

## Executive summary

Phiscatcher is a local, live network-flow monitor. TShark captures selected packet fields from a configured interface; a Node.js backend forwards each packet as JSON to a persistent Python process; Python groups packets into bidirectional flows, calculates 34 traffic/domain features, and predicts a phishing probability with a saved scikit-learn pipeline. Node.js combines that probability with a small rule score, stores the completed flow in MongoDB, and emits a Socket.IO event. A React dashboard displays summary cards, two charts, and the latest-flow table.

This describes the code present in this repository, not a claim that every path runs successfully on every machine. In particular, the frontend’s initial request URL does not match the registered backend route, the training data is absent, MongoDB and local capture setup are external requirements, and the large serialized model was not deserialized during this read-only audit.

## What the project does

The application observes live IPv4/IPv6 packets with TShark and analyzes packet metadata in short-lived inactivity-delimited groups called flows. It does not accept a URL to scan, launch a browser, capture to a PCAP file, inspect full HTTP/TLS payloads, or determine that a particular page is a phishing page. It classifies observed flows using traffic statistics and DNS query-name characteristics. The result is an automated risk estimate, not proof of malicious intent.

### Actual workflow

```text
Network interface 5 (hard-coded at startup)
  → TShark selected fields, delimited text on stdout
  → backend/services/tsharkService.js parses a packet object
  → JSON line on child-process stdin
  → ml/packet_processor.py groups packets; expires a flow after 5 s inactivity
  → 34 named features → saved preprocessing + Random Forest pipeline
  → newline-delimited JSON result on Python stdout
  → backend/services/pythonService.js parses the result
  → backend/services/scoringService.js computes rule/final scores
  → backend/server.js writes a MongoDB document
  → Socket.IO `new-flow` event carrying the saved document
  → React updates recent-flow state and summary counters
```

The frontend also tries to fetch initial records and stats over HTTP. As currently written, its latest-flow request uses `GET /api/flows`, but the backend registers `GET /api/flows/latest-flows`. Therefore `Promise.all` in the initial loader rejects when that route returns 404; the catch logs the failure and the dashboard then renders default stats/empty recent flows. Live Socket.IO events can still update the UI if the backend, capture, Python model, and database are all working.

## Project structure

This tree includes project files, not `.git`, installed `node_modules`, or generated/cache contents. `backend/.env` exists locally and is intentionally not described or reproduced here.

```text
Phiscatcher/
├── .gitattributes                     # LF normalization; Git LFS handling for .pkl
├── .gitignore                         # ignores env files, Python caches/venvs, node_modules, dist
├── LICENSE                            # MIT
├── README.md                          # this implementation-based guide
├── backend/
│   ├── .env                           # local sensitive configuration; values omitted
│   ├── package.json / package-lock.json
│   ├── server.js                      # Express, startup/shutdown, persistence and event pipeline
│   ├── config/db.js                   # Mongoose connection using MONGO_URI
│   ├── controllers/
│   │   ├── dashboardController.js     # aggregate counts by classification
│   │   └── flowController.js          # latest five stored flows
│   ├── models/Flow.js                 # MongoDB/Mongoose flow schema
│   ├── routes/
│   │   ├── dashboardRoutes.js         # GET /api/dashboard/stats
│   │   └── flowRoutes.js              # GET /api/flows/latest-flows
│   ├── services/
│   │   ├── pythonService.js           # Python child process, JSON-line input/output
│   │   ├── scoringService.js          # heuristic and blended scores/classification
│   │   └── tsharkService.js           # TShark process and field parsing
│   └── socket/socket.js               # Socket.IO server and singleton accessor
├── frontend/
│   ├── README.md                      # mostly unmodified React/Vite starter guide
│   ├── package.json / package-lock.json
│   ├── vite.config.js                 # Vite plus Tailwind Vite plugin
│   ├── eslint.config.js               # ESLint, React Hooks, React Refresh config
│   ├── index.html                     # browser entry; title remains `vite-project`
│   ├── public/{favicon.svg,icons.svg} # public SVG assets
│   └── src/
│       ├── main.jsx                   # React root and global CSS entry
│       ├── App.jsx                    # initial REST loading, Socket.IO, dashboard layout/state
│       ├── App.css                    # starter styles; dashboard mainly uses utility classes
│       ├── index.css                  # Tailwind import and global styling
│       ├── services/api.js            # Axios client and initial REST calls
│       ├── components/
│       │   ├── Header.jsx             # brand and LIVE indicator
│       │   ├── StatCard.jsx           # reusable metric card
│       │   ├── TrafficChart.jsx       # recent-flow count area chart
│       │   ├── ThreatChart.jsx        # classification distribution donut chart
│       │   └── FlowTable.jsx          # latest five flows and score badges
│       └── assets/{hero.png,react.svg,vite.svg} # hero and starter assets; not part of data pipeline
└── ml/
    ├── packet_processor.py            # live flow aggregation, feature calculation and inference
    ├── train_model.py                 # offline training script; expects absent dataset files
    ├── test_model.py                  # separate dataset test script; paths/columns differ
    ├── inspect_data.py                # dataset exploration helper
    ├── feature_importance.py          # reads saved pipeline and writes importance CSV
    ├── feature_importance.csv         # 34 recorded feature-importance rows
    └── phishing_model.pkl             # serialized fitted pipeline (~278 MB); not safely inspected internally
```

No test directory, dataset folder, `.env.example`, Wireshark profile/filter, PCAP, browser automation code, Scapy code, or separate documentation directory appears in the project files. `node_modules` is installed locally but ignored by Git; it is dependency content rather than application source.

## Architecture and data flow

### Capture and packet parsing

`backend/server.js` loads dotenv, creates Express/HTTP/Socket.IO, connects MongoDB, starts Python, and after one second calls `startTshark("5")`. `backend/services/tsharkService.js` starts the hard-coded executable `C:\Program Files\Wireshark\tshark.exe` with interface `5`, line-buffered fields output, and `|` as the separator. Requested fields are epoch timestamp, frame length, IPv4 source/destination/protocol/TTL, IPv6 source/destination/next-header/hop-limit, TCP and UDP ports, DNS query name and query type.

Each complete stdout line is split into those 16 columns. The service chooses IPv4 fields before IPv6 where present, TCP ports before UDP ports, converts lengths/ports to numbers, and creates an object with `timestamp`, `packetLength`, `srcIp`, `dstIp`, `srcPort`, `dstPort`, `protocol`, `ttl`, `dnsQuery`, and `dnsQueryType`. The code forwards this object to Python and logs it. The capture arguments do not save a PCAP. TTL, DNS query type and several captured fields are not used by the Python feature calculations.

### Node.js ↔ Python process pipe

`backend/services/pythonService.js` spawns `python ml/packet_processor.py` with the project root as working directory. It serializes each packet object with `JSON.stringify`, adds a newline, and writes it to the persistent child’s stdin. Python reads one JSON object per line from stdin. Python writes human-readable startup logs and compact JSON result lines to stdout; Node buffers partial chunks, splits on newlines, parses JSON, and emits the internal `flow_result` event. Python diagnostics go to stderr. This is local process stdin/stdout, not HTTP or a network socket.

### Flow grouping and expiry

`ml/packet_processor.py` ignores packets with invalid/non-positive timestamps or missing IP addresses. `create_flow_key` sorts the two `(IP, port)` endpoints and adds protocol, so packets in either direction map to the same key. The stored flow retains the IP/port direction of its first packet. Packets contribute lengths and direction-specific lengths; DNS query names are normalized to lowercase and saved in a list.

After each packet, the script expires every flow whose `current packet timestamp - last packet timestamp` is at least `FLOW_TIMEOUT = 5.0` seconds. It emits one result when the flow expires. There is no independent timer: if packet input stops completely, the loop cannot expire a quiet remaining flow. Flow keys do not include a generation/start time, so a later packet matching a prior key after that key has expired begins a new flow. This is packet inactivity aggregation, not TCP-session tracking based on SYN/FIN/RST.

### Prediction, persistence, and user interface

Python builds a pandas one-row DataFrame with the 34 `LIVE_FEATURES` columns, calls `predict` and `predict_proba` on the loaded `joblib` artifact, looks up the probability for class `1`, and returns packet metadata, features, numeric prediction, and probability. Node computes scores, creates a Mongoose `Flow`, then emits the saved document via `io.emit("new-flow", savedFlow)`. Save and event emission are inside the same `try`: if MongoDB creation fails, no live event is emitted.

`frontend/src/App.jsx` separately loads initial flow/stat data with Axios and opens a Socket.IO connection to `http://localhost:8000`. On `new-flow`, it prepends the record to `recentFlows` (deduplicated by `_id`, capped at five) and increments the in-memory counters. Reloading retrieves aggregate counts and recent items through REST, subject to the route mismatch above. The area chart maps the recent five records to ordinal positions; it is not a time-series packet-rate chart. The donut chart counts the classifications among those same recent five, not all database history.

## Technology and skill inventory

### Frontend

| Technology | Use and location | Effect if removed |
|---|---|---|
| React 19, JSX, hooks (`useState`, `useEffect`) | `App.jsx`, `main.jsx`, all components; dashboard state, component rendering and lifecycle subscriptions | Dashboard does not render or update |
| Vite 7 and React Vite plugin | `frontend/package.json`, `vite.config.js`; dev server and bundling | Frontend scripts/build stop using configured Vite workflow |
| Tailwind CSS 4 and `@tailwindcss/vite` | `index.css`, utility classes in components; layout, colors, responsive styling | Most dashboard presentation loses styling |
| CSS, HTML, SVG | `index.css`, starter `App.css`, `index.html`, public/assets SVG | Base page, global rules, and icons/branding change |
| Axios | `services/api.js`; HTTP GET for latest flows/stats | Initial REST retrieval breaks |
| Socket.IO client | `App.jsx`; subscribes to `new-flow` | No push updates; only initial REST data could populate UI |
| Recharts | `TrafficChart.jsx`, `ThreatChart.jsx` | Charts fail to render |
| Lucide React | Header, stat cards, flow table icons | Icons fail or must be replaced |

Dashboard presentation uses a deep navy/indigo background, translucent bordered cards, slate text, emerald/amber/red status colors, and a spinner in `App.jsx` while initial loading is pending. The header’s green LIVE badge is a visual label; it is not a health check.

### Backend and communication

| Technology / skill | Use and location | Effect if removed |
|---|---|---|
| Node.js, ES modules | All backend `.js`; orchestrates processes, APIs, scoring and persistence | Backend cannot run |
| Express 5 | `server.js`, `routes/*`; REST endpoints and JSON middleware | REST API unavailable |
| CORS | `server.js`; Express CORS middleware; Socket.IO separately allows `http://localhost:5173` | Cross-origin browser calls may be blocked |
| `child_process.spawn` | `tsharkService.js`, `pythonService.js`; starts capture and Python processes | No live capture/inference pipeline |
| Promises/async callbacks/events | controllers, database, child process streams, internal `EventEmitter` | Async data flow and process events break |
| Socket.IO 4 | `socket/socket.js`, `server.js`; backend real-time event transport | UI gets no push event |
| REST/JSON | Express controllers and Axios service | Initial stats/history fetch unavailable |
| dotenv/environment variables | `server.js` loads dotenv; `config/db.js` reads `MONGO_URI`, server reads `PORT` | Configuration cannot be read as currently written |

The Python child is long-lived; the Node internal `EventEmitter` carries parsed flow results from the service module into `server.js`. Neither mechanism is Socket.IO. Socket.IO is used only between the backend and browser.

### Python, machine learning, and data processing

| Technology / skill | Use and location | Effect if removed |
|---|---|---|
| Python 3 | `ml/*.py`; packet aggregation, feature extraction and model utilities | Inference process unavailable |
| pandas | `packet_processor.py`, `train_model.py`, utility scripts; DataFrames/CSV | Current model input and dataset scripts fail |
| NumPy | `train_model.py` import | It is imported but no meaningful direct `np` use is visible in that file |
| scikit-learn | `train_model.py`: split, transformer, imputers, encoder, pipeline, Random Forest and metrics | Model training pipeline cannot run |
| joblib / pickle serialization | Processor loads `phishing_model.pkl`; training/importance/test scripts load or save pipelines | Inference/training artifact handling fails |
| Random Forest | `train_model.py`; 150-tree binary classifier with balanced class weight | Replacing it changes the trained classification method |
| Feature engineering / statistics | `packet_processor.py`; flow aggregates, packet distributions, DNS name statistics and entropy | Model has no live feature vector |
| JSON Lines over stdio | Python main loop and Node process services | Components cannot exchange packets/results |

Training uses `SimpleImputer(strategy="median")` for numeric columns and most-frequent imputation plus `OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)` for categorical columns. `ColumnTransformer` builds the preprocessing pipeline. No numeric scaler/normalizer is configured. Training uses `train_test_split(test_size=0.20, random_state=42, stratify=y)` and `RandomForestClassifier(n_estimators=150, random_state=42, n_jobs=-1, class_weight="balanced")`. The whole pipeline is saved using `joblib.dump`.

The declared training inputs `ml/dataset/output-of-benign-pcap-3.csv` and `ml/dataset/output-of-phishing-pcap.csv` are not present. Training and its reported evaluation cannot be reproduced from this checkout alone. `ml/test_model.py` instead reads a root-relative `output-of-phishing-pcap.csv` and drops columns that do not match the training script’s selected feature approach; it is an auxiliary, inconsistent test path. `inspect_data.py` is also a manual CSV exploration helper. `feature_importance.csv` is an existing 34-row output; its recorded numbers are evidence of a prior feature-importance run, not a fresh validation of the binary model artifact.

### Capture, persistence, tooling, and testing

| Technology / skill | Use and location | Effect if removed |
|---|---|---|
| Wireshark/TShark | TShark executable and fields arguments in `tsharkService.js`; Wireshark is the associated capture/analyzer suite | Live packet source unavailable; no other capture code exists |
| TCP/IP, IPv4/IPv6, TCP/UDP, DNS concepts | Fields captured in `tsharkService.js`; IP/ports/protocol/DNS drive flows/features | The selected flow input/feature signals change |
| MongoDB, Mongoose | `config/db.js`, `models/Flow.js`, controllers, server | Persistent history and initial stats/history routes unavailable |
| npm/package-lock | `backend` and `frontend` manifests/locks; dependency installation and script versions | Reproducible JS dependency installation changes |
| ESLint | `frontend/eslint.config.js`; JS/JSX, hooks and refresh rules | Configured frontend linting is lost (no lint script is declared) |
| Git LFS configuration | `.gitattributes` marks `.pkl` for LFS; repository behavior for model artifact changes | Large model tracking may differ |
| Testing | `ml/test_model.py` is a manual prediction script; no automated test files or test scripts were found | No checked-in automated suite to remove; the manual helper would be lost |

Not evidenced in application code: FastAPI, Playwright/browser automation, Scapy, Chart.js, React Router, a separate state-management library, a Python requirements file, a package-based Python environment definition, CORS configuration for arbitrary origins, or a dedicated logging/testing framework.

## Machine learning and exact feature list

The source defines **34 features**, matching the supplied clue. The same ordered list appears in `ml/train_model.py` and `ml/packet_processor.py`. The Python processor constructs a DataFrame using that list, so ordering and names are explicit. There are 24 flow/packet-statistic features and 10 DNS/domain features. The model's categorical values are `dns_top_level_domain` and `dns_second_level_domain`; the other 32 are numeric. During training, categorical values are ordinal-encoded; live unknown values use `-1`. Missing numeric values are median-imputed and missing categories use the most common category. No scaling is defined.

| # | Feature | Calculation in `packet_processor.py` | Why it may help distinguish traffic |
|---:|---|---|---|
| 1 | `duration` | Last packet timestamp minus first, clamped at zero | Captures short/long connection behavior |
| 2 | `packets_numbers` | Count of all packet lengths in flow | Overall activity volume |
| 3 | `receiving_packets_numbers` | Count of lengths classified as receiving | Directional imbalance |
| 4 | `sending_packets_numbers` | Count of lengths classified as sending | Directional imbalance |
| 5 | `total_bytes` | Sum of all packet lengths | Total transfer size |
| 6 | `receiving_bytes` | Sum of receiving lengths | Inbound volume |
| 7 | `sending_bytes` | Sum of sending lengths | Outbound volume |
| 8 | `packets_rate` | Packet count / max(duration, 0.001) | Activity intensity |
| 9 | `packets_len_rate` | Total bytes / max(duration, 0.001) | Byte throughput |
| 10 | `min_packets_len` | Minimum observed packet length | Small-packet behavior |
| 11 | `max_packets_len` | Maximum observed packet length | Large-packet behavior |
| 12 | `mean_packets_len` | Arithmetic mean of lengths | Typical packet size |
| 13 | `median_packets_len` | Median length | Robust typical size |
| 14 | `mode_packets_len` | Most frequent length, tie via Counter order | Repeated packet-size pattern |
| 15 | `min_receiving_packets_len` | Minimum receiving length; zero if none | Inbound packet pattern |
| 16 | `max_receiving_packets_len` | Maximum receiving length; zero if none | Inbound packet pattern |
| 17 | `mean_receiving_packets_len` | Mean receiving length; zero if none | Inbound typical size |
| 18 | `median_receiving_packets_len` | Median receiving length; zero if none | Inbound size distribution |
| 19 | `mode_receiving_packets_len` | Mode receiving length; zero if none | Repeated inbound size |
| 20 | `min_sending_packets_len` | Minimum sending length; zero if none | Outbound packet pattern |
| 21 | `max_sending_packets_len` | Maximum sending length; zero if none | Outbound packet pattern |
| 22 | `mean_sending_packets_len` | Mean sending length; zero if none | Outbound typical size |
| 23 | `median_sending_packets_len` | Median sending length; zero if none | Outbound size distribution |
| 24 | `mode_sending_packets_len` | Mode sending length; zero if none | Repeated outbound size |
| 25 | `dns_domain_name_length` | Length of normalized whole query name | Long/odd names may be suspicious signals |
| 26 | `dns_subdomain_name_length` | Length of labels before final two labels | Long nested names may be unusual |
| 27 | `dns_top_level_domain` | Last dot-separated label | TLD may correlate with training patterns |
| 28 | `dns_second_level_domain` | Penultimate label | Domain token may correlate with training patterns |
| 29 | `character_entropy` | Shannon entropy in bits over characters of full normalized domain | Measures character diversity/randomness |
| 30 | `numerical_percentage` | Digit count / alphanumeric count × 100 | Numeric-heavy names may be unusual |
| 31 | `max_continuous_alphabet_len` | Longest consecutive alphabetic run | Captures long letter sequences |
| 32 | `max_continuous_consonants_len` | Longest consecutive alphabetic non-vowel run | Captures hard-to-read consonant runs |
| 33 | `vowels_consonant_ratio` | Vowel count / consonant count, or zero | Captures domain letter composition |
| 34 | `conv_freq_vowels_consonants` | Absolute vowel/consonant count difference / total letters | Captures letter balance |

Domain features use the latest DNS query name observed in the flow; absent DNS yields empty strings and zero numeric domain values. These are heuristic signals, not definitive indicators: the source provides no calibration or feature-level explanations for each prediction. The model returns a binary prediction (`0`/`1`) and probability for class `1`; class `1` is mapped to “phishing” in training labels (`Benign`→0, `Phishing`→1). The backend's final three-way labels are then based on the blended score, not directly on the binary prediction.

The project does not show live model training: `packet_processor.py` loads the existing artifact at startup. The artifact is a large pickle-based joblib file. It was not loaded or executed during this audit because deserializing pickle content can execute code. Source and the checked-in feature-importance CSV were inspected instead; artifact internals and exact trained `classes_` therefore remain unconfirmed independently.

## Rules, score, and classification

`backend/services/scoringService.js` starts rule score at zero and adds:

- ML probability ≥ 0.80: +40; else ≥ 0.60: +25; else ≥ 0.40: +10.
- Destination port in `[21, 23, 25, 445, 3389]`: +15.
- `dns_second_level_domain`, case-insensitively, contains any of `login`, `verify`, `secure`, `account`, `update`, `confirm`, `wallet`: +20 once.
- Rule score is capped at 100.

The final score is `(phishingProbability × 100 × 0.7) + (ruleScore × 0.3)`. Thus the 70%/30% clue is verified. Severity and classification share thresholds: score ≥75 → `HIGH` / `PHISHING`; score ≥40 → `MEDIUM` / `SUSPICIOUS`; otherwise `LOW` / `BENIGN`. The probability itself is not thresholded to create the displayed label; it contributes to both ML score and a probability-based rule bonus. No HTTP URL, TLS certificate, HTTP header, redirect, or packet-payload rules are present.

## API, database, and live updates

| Method and path | Actual behavior |
|---|---|
| `GET /api/dashboard/stats` | Returns counts of all stored documents, split into BENIGN/SUSPICIOUS/PHISHING |
| `GET /api/flows/latest-flows` | Returns latest five MongoDB documents sorted by `createdAt` descending |
| `GET /api/flows` | Not registered, although the frontend currently requests it |

`Flow.js` stores addresses, ports, protocol, start/end/duration, prediction/probability, ML/rule/final scores, severity, classification, feature object, and Mongoose timestamps. `config/db.js` reads `MONGO_URI`. The code does not establish that MongoDB Atlas specifically is used; that depends on the secret connection URI. No database credentials are reproduced here.

Socket.IO is attached to the HTTP server and configured with origin `http://localhost:5173`. On successful database creation, the saved document is emitted to all connected clients under `new-flow`. The React client is hard-coded to `http://localhost:8000`; environment-based frontend API configuration is not present.

## Setup and running (as encoded in the project)

Prerequisites visible in source: Node.js/npm, Python with `pandas`, `joblib`, and the scikit-learn training/runtime dependencies installed, Wireshark/TShark at the hard-coded Windows path, a usable capture interface matching number `5`, and a reachable MongoDB URI in backend environment configuration. The repository has no Python requirements file and does not contain the CSV training datasets. The backend expects `MONGO_URI`; `PORT` defaults to `8000`. Treat `backend/.env` as sensitive.

```powershell
# Terminal 1
cd backend
npm install
npm start

# Terminal 2
cd frontend
npm install
npm run dev
```

The backend starts Python and TShark itself. Confirm capture permissions, TShark installation/path, interface selection, Python command/dependencies, and database availability in your own authorized environment. The frontend Vite config does not declare a proxy; API and Socket.IO URLs are hard-coded to localhost. The steps above describe the scripts, not a guarantee that the current route mismatch or external setup has been resolved.

## Screenshots / Demos

Replace these intentional placeholders with real screenshots when available. No screenshot files are currently included.

### Dashboard

![Dashboard](screenshots/dashboard.png)

### Live flow analysis

![Live flow analysis](screenshots/live-flow-analysis.png)

### Detection result

![Detection result](screenshots/detection-result.png)

### Traffic and threat charts

![Traffic and threat charts](screenshots/traffic-threat-charts.png)

## Safety, limitations, and status

Capture only traffic on systems/networks you own or are authorized to inspect. Captured addresses and DNS names can be sensitive. This implementation captures live selected fields; it does not save a PCAP or read encrypted application contents. A model classification is a statistical signal, not a forensic conclusion.

**Implemented in source:** live TShark process invocation, packet field parsing, Python flow aggregation, 34 feature calculations, saved-model inference path, JS rules and blended labels, MongoDB schema/queries, REST handlers, Socket.IO event emission, and React dashboard components.

**Present but locally dependent / not independently validated:** actual model artifact compatibility, model quality, capture permissions/interface availability, database connectivity, and live operation. Training datasets are absent; training is not reproducible from this checkout. The model artifact was not deserialized during the audit.

**Known incomplete or inconsistent:** initial frontend flow URL does not match backend route; `ml/test_model.py` uses different data paths/columns; root and frontend READMEs previously described features not present in source (the root README is replaced by this one; frontend README remains generic starter documentation); `index.html` retains the Vite title. The dashboard's chart labels are based on latest five records. The `LIVE` badge is decorative.

**Not found / only previously documented as intended:** user URL scanning, Playwright, Scapy, packet capture files/PCAP archive, HTTP/TLS inspection, FastAPI, threat-intelligence integration, route navigation, charted packet throughput, authentication, and automated project tests.

## Viva preparation

### 30-second explanation

“Phiscatcher is a local live network-flow monitoring dashboard. TShark reads selected packet metadata, Node.js passes packets to a persistent Python process, and Python groups them into flows and calculates 34 traffic and DNS-domain features. A saved Random Forest pipeline returns a phishing probability. The backend adds heuristic rules, blends ML and rule scores 70/30, stores completed results in MongoDB, and pushes them to a React dashboard with Socket.IO.”

### One-minute explanation

“The backend starts TShark on a configured interface and asks it to output packet fields as delimited text. Node converts each line into a JSON packet and writes it to Python over stdin. Python uses IP addresses, ports, and protocol to group both directions of traffic into the same flow, tracks packet sizes and DNS query names, and emits a flow when no packet has arrived for five seconds. It calculates 34 features: packet counts, bytes, rates and size statistics, plus DNS-name length, entropy, digits, letter runs and domain labels. A pre-trained scikit-learn pipeline produces a binary prediction and phishing probability. JavaScript adds port/domain/probability rules, calculates a 70/30 blended score, and assigns benign, suspicious, or phishing. MongoDB stores each completed result and Socket.IO pushes it to the dashboard. The frontend also requests initial data via REST; the latest-flows URL currently mismatches the backend route.”

### Three-minute explanation / architecture

“The project has three running parts. TShark is the packet-field collector, Node.js is the orchestrator and API server, and Python is the flow and ML processor. TShark is the command-line companion to Wireshark: here it reads live interface traffic and emits selected fields, but the code does not write a PCAP file. Node reads TShark stdout, parses timestamp, frame size, IP endpoints, protocol, ports and DNS question, then serializes each packet as one JSON line to Python stdin. Python maintains a map of flows. It sorts endpoint pairs when forming the key, which allows reverse-direction packets to join the same conversation, but remembers the first packet's direction for sending/receiving statistics. Once a flow has been inactive for five seconds according to a later packet timestamp, Python calculates features and makes a prediction with the saved model. It prints one JSON result line on stdout, which Node parses. The scoring service adds rules and assigns a final label. Server code persists the document to MongoDB; after a successful save it emits `new-flow` to browser clients. React fetches initial stats/history over REST and uses Socket.IO for new-flow pushes. Its cards count all stored classifications initially, while its charts and table concern only five recent flows. One known issue is the initial request goes to `/api/flows`, while the backend route is `/api/flows/latest-flows`.”

### ML and 34 features

“The training script combines labeled benign and phishing CSVs, maps the labels to 0 and 1, selects 34 features, imputes missing values, ordinal-encodes the two domain-category columns, then trains a 150-tree Random Forest using a stratified 80/20 split and class balancing. The complete preprocessing and model pipeline is saved as a joblib pickle. At runtime the Python processor loads that artifact once and uses the same ordered feature names to make a one-row DataFrame. It calls `predict` and `predict_proba`; class 1's probability is sent to Node. The live feature groups are nine flow totals/rates, fifteen total/sending/receiving packet-size/count statistics, and ten domain properties. The training CSVs are absent in this checkout, so the training/evaluation cannot be reproduced here. The artifact is present but its internals were not deserialized as part of this read-only audit.”

If asked to name the features, use the numbered table above; it is the exact ordered list from the runtime and training source.

### TShark, Python, and Random Forest

- **Why TShark/Wireshark?** TShark supplies machine-readable live packet fields; Wireshark is useful for human inspection of traffic. This code invokes TShark directly and does not currently create PCAP files or invoke the Wireshark GUI.
- **Why Python?** The implemented feature aggregation and scikit-learn inference live in Python. Node and Python exchange newline-delimited JSON over a child process pipe.
- **Why Random Forest?** The training source specifies an ensemble of 150 decision trees, class-balanced training, and probability output. Different trees can learn different combinations of traffic/domain features; the project uses the resulting class-1 probability as one scoring input. No claim about measured generalization should be made without accessible data and a verified evaluation.
- **How is phishing detected?** The model probability is combined with a rule score using 70% model score and 30% rules. Rules add points for probability bands, five destination ports, and selected words in the second-level DNS label. Final score thresholds create the three labels.

### Frontend, real-time data, and storage

“React calls the REST API through Axios for initial information, renders stat cards, charts and a table, then opens a Socket.IO client to port 8000. Each `new-flow` event adds the saved record to the latest-five list and increments local counters. MongoDB persists flow metadata, score fields and features using a Mongoose schema. The database URI is supplied through `MONGO_URI`; the source alone does not prove that the server is MongoDB Atlas.”

## Important discrepancy checklist

| Supplied clue | Finding |
|---|---|
| TShark captures live packets | **Verified** in `tsharkService.js`; it emits selected fields, no PCAP save |
| Node manages TShark | **Verified** via `spawn` and stdout parsing |
| Node communicates with persistent Python | **Verified** via stdin/stdout JSON lines |
| Python aggregates packets into flows | **Verified**, bidirectional endpoint key and 5-second inactivity threshold |
| Python extracts 34 features | **Verified**, exact list above |
| Random Forest produces phishing probability | **Partially verified**: training source says RandomForest; runtime expects model `predict_proba`; binary artifact wasn't deserialized |
| Node combines ML score and JS rule score | **Verified** |
| 70% ML + 30% rules | **Verified**, `scoringService.js` |
| benign/suspicious/phishing labels | **Verified**, final-score bands in backend |
| MongoDB Atlas stores flow history | **Partially verified**: MongoDB/Mongoose persistence is present; Atlas specifically depends on URI and is not confirmed |
| Socket.IO provides real-time updates | **Verified** for post-save `new-flow` push |
| React renders cards/charts/latest flows | **Verified**; threat chart reflects latest five only, traffic chart is ordinal recent-flow count |
| User-submitted URL/browser/Playwright analysis from old README | **Not found** in runtime source |
| Original documentation matched implementation | **Contradicted**; it outlined an intended, different system |

## Bootloader status

No additional bootloader was added. The frontend already has a minimal loading state in `App.jsx` while the initial API calls are pending. Adding a timed branded intro would delay a dashboard whose loading/data path already has a route mismatch, and would not improve startup readiness; the existing application code was therefore left untouched.

## License

The repository includes an MIT license; see [LICENSE](LICENSE).
