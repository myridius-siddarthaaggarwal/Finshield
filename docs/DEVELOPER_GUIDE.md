# 🛠️ FinShield — Developer & Local Contribution Guide

> **Target Audience**: Hackathon Teammates, Software Engineers, AI/ML Contributors  
> **Repository**: `Finshield`

---

## 💻 1. Local Prerequisites & Environment Setup

Ensure you have the following installed on your local machine:

- **Python**: Version `3.11` or newer
- **Node.js**: Version `20` or newer with `npm`
- **Git**: Installed and configured with your name & email

---

## ⚡ 2. Step-by-Step Local Setup

### Step 1: Clone Repository & Create Virtual Environment

```bash
# Clone the repository
git clone https://github.com/your-username/Finshield.git
cd Finshield

# Create Python virtual environment
# On Windows:
py -m venv .venv
.\.venv\Scripts\activate

# On macOS/Linux:
python3 -m venv .venv
source .venv/bin/activate
```

### Step 2: Install Python Backend Dependencies

```bash
# On Windows PowerShell:
.\.venv\Scripts\pip install -r backend\requirements.txt

# On macOS/Linux:
pip install -r backend/requirements.txt
```

### Step 3: Seed Local Database

This creates the SQLite database `backend/finshield.db` and populates all 13 users, 7 benchmark cases, dimension scores, controls, votes, and audit histories:

```bash
# Navigate into backend directory:
cd backend

# On Windows:
..\.venv\Scripts\python -m app.db.init_db

# On macOS/Linux:
python3 -m app.db.init_db

# Return to root directory (optional):
cd ..
```

### Step 4: Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

---

## 🏃 3. Running Dev Servers Locally

### Terminal 1: Run Backend API (FastAPI)

```bash
# Navigate into backend directory:
cd backend

# On Windows:
..\.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000

# On macOS/Linux:
python3 -m uvicorn app.main:app --reload --port 8000
```

- **Backend API**: `http://localhost:8000`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`

### Terminal 2: Run Frontend (React + Vite)

```bash
# In Finshield/frontend directory:
cd frontend
npm run dev
```

- **Frontend UI**: `http://localhost:5173`

---

## 🧪 4. Running the Automated Test Suite

We have comprehensive unit tests covering the deterministic and micro-agent layers:

1. `backend/tests/test_fsm.py` — Deterministic state machine valid & invalid transitions.
2. `backend/tests/test_scoring_engine.py` — Weighted risk math, controls reduction, confidence gate.
3. `backend/tests/test_screening.py` — Sanctions and FATF high-risk corridor lookups.
4. `backend/tests/test_micro_agents.py` — Domain micro-agent evaluation, parallel execution, and strict circuit breaker loop hardstop (`MAX_INTERACTION_DEPTH = 1`).
5. `backend/tests/test_requirement_expansion.py` — AI SME autonomous expansion, domain gap analysis, public compliance API integration, and benchmark presets.

Run all tests:

```bash
# In Finshield/backend directory:
# On Windows:
& "..\.venv\Scripts\pytest.exe" -v

# On macOS/Linux:
pytest -v
```

All 25 test cases must pass with 100% success rate.

---

## 🚀 5. How to Improve & Extend the Codebase

### A. Working with the Specialized Micro-Agent Fleet

The AI reasoning engine uses a decomposed fleet of four micro-agents in [`backend/app/services/agents/`](file:///c:/Users/202140/OneDrive%20-%20RCG%20Global%20Services,%20Inc/Desktop/Finshield/backend/app/services/agents/):

- `aml_agent.py` (`agent_aml`) — 35% weight: FATF R.10 CDD, structuring velocity, money mule rings.
- `cft_agent.py` (`agent_cft`) — 20% weight: FATF R.6/15, OFAC sanctions, state-sponsored cyber finance.
- `fraud_agent.py` (`agent_fraud`) — 25% weight: FCA Consumer Duty 2023, UK PSR APP Scam 50:50 reimbursement liability.
- `compliance_agent.py` (`agent_compliance`) — 20% weight: EU MiCA CASP licensing, OCC TPRM 2023, FinCEN 2026.

Each micro-agent loads its prompt from [`prompts/micro_agents/<agent_id>_v1.0.json`](file:///c:/Users/202140/OneDrive%20-%20RCG%20Global%20Services,%20Inc/Desktop/Finshield/prompts/micro_agents/).

### B. Configuring the Circuit Breaker Loop Hardstop

To prevent circular switching and infinite token-burning loops between agents:
1. Open [`backend/app/services/agents/orchestrator.py`](file:///c:/Users/202140/OneDrive%20-%20RCG%20Global%20Services,%20Inc/Desktop/Finshield/backend/app/services/agents/orchestrator.py).
2. The orchestrator enforces `MAX_INTERACTION_DEPTH = 1` and tracks `visited_agents`.
3. If an agent attempts to re-consult a visited agent or exceed the depth limit, a `HARDSTOP_ENFORCED` event is logged and execution safely continues without circular stalls.

### C. Integrating Public Open Compliance APIs

Open compliance verification is handled by [`backend/app/services/public_compliance_api.py`](file:///c:/Users/202140/OneDrive%20-%20RCG%20Global%20Services,%20Inc/Desktop/Finshield/backend/app/services/public_compliance_api.py):
- Connects live to the **OpenSanctions API** (`https://api.opensanctions.org/match/default`) for PEP & Sanctions screening.
- Maintains consolidated offline datasets for FATF High-Risk/Grey Lists, OFAC SDN registries, and UK FCA alerts.
- To configure an OpenSanctions API key, set `OPENSANCTIONS_API_KEY` in `.env`. The system operates seamlessly with or without an active key via robust fallback.

### D. Extending the Autonomous Requirement Expander ("AI SME")

The requirement expander converts vague product briefs into production-grade risk specifications:
1. Service: [`backend/app/services/requirement_expansion_service.py`](file:///c:/Users/202140/OneDrive%20-%20RCG%20Global%20Services,%20Inc/Desktop/Finshield/backend/app/services/requirement_expansion_service.py).
2. Versioned Prompt: [`prompts/requirement_expansion/v1.0.0_2026-09-17.json`](file:///c:/Users/202140/OneDrive%20-%20RCG%20Global%20Services,%20Inc/Desktop/Finshield/prompts/requirement_expansion/v1.0.0_2026-09-17.json).
3. Benchmark Presets: Presets are defined in `requirement_expansion_service.py` under `BENCHMARK_PRESETS` for instant hackathon demonstrations.

### E. Adding a New Benchmark Case

To add a new pre-seeded case:

1. Open [`backend/app/db/init_db.py`](file:///c:/Users/202140/OneDrive%20-%20RCG%20Global%20Services,%20Inc/Desktop/Finshield/backend/app/db/init_db.py).
2. Instantiate a new `RiskCase` with its parameters, dimension scores, controls, and committee votes.
3. Re-run `python -m app.db.init_db` (inside the `backend` directory).

### F. Adding a New Regulatory Framework

1. Open [`governed_data_layer/regulatory_frameworks.json`](file:///c:/Users/202140/OneDrive%20-%20RCG%20Global%20Services,%20Inc/Desktop/Finshield/governed_data_layer/regulatory_frameworks.json).
2. Add a new framework entry with `id`, `authority`, `code`, `title`, and `summary`.
3. The AI and frontend will immediately incorporate it into the citation engine!

### G. Adding a New Geography Multiplier

1. Open [`governed_data_layer/geography_risk_table.json`](file:///c:/Users/202140/OneDrive%20-%20RCG%20Global%20Services,%20Inc/Desktop/Finshield/governed_data_layer/geography_risk_table.json).
2. Add or adjust the country's `risk_multiplier` (e.g., `1.8` for UAE, `1.9` for Nigeria, `3.0` for Sanctioned).

---

## 🤖 6. Using the FinShield Git Automation Agent

We have built a dedicated Git Agent CLI in `agents/git_agent/git_agent.py`:

```bash
# 1. Check repository status
python agents/git_agent/git_agent.py status

# 2. Stage and commit with conventional formatting
python agents/git_agent/git_agent.py commit -m "add new sanction rule" -s backend -t feat

# 3. Create a feature branch for your task
python agents/git_agent/git_agent.py branch feature/my-feature-name

# 4. Pull latest changes from remote
python agents/git_agent/git_agent.py pull

# 5. One-command sync (stage, commit, pull, and push)
python agents/git_agent/git_agent.py sync -m "feat(frontend): polish committee voting cards"
```
