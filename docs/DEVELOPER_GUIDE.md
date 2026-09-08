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
# On Windows:
.\.venv\Scripts\python -m app.db.init_db

# On macOS/Linux:
python -m app.db.init_db
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
# In Finshield root directory:
# On Windows:
.\.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000

# On macOS/Linux:
python -m uvicorn app.main:app --reload --port 8000
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

We have comprehensive unit tests covering:
1. `backend/tests/test_fsm.py` — Deterministic state machine valid & invalid transitions.
2. `backend/tests/test_scoring_engine.py` — Weighted risk math, controls reduction, confidence gate.
3. `backend/tests/test_screening.py` — Sanctions and FATF high-risk corridor lookups.

Run all tests:
```bash
# In Finshield/backend directory:
# On Windows:
& "..\.venv\Scripts\pytest.exe" -v

# On macOS/Linux:
pytest -v
```

---

## 🚀 5. How to Improve & Extend the Codebase

### A. Adding a New Benchmark Case
To add a new pre-seeded case:
1. Open [`backend/app/db/init_db.py`](file:///c:/Users/202140/OneDrive%20-%20RCG%20Global%20Services,%20Inc/Desktop/Finshield/backend/app/db/init_db.py).
2. Instantiate a new `RiskCase` with its parameters, dimension scores, controls, and committee votes.
3. Re-run `python -m app.db.init_db`.

### B. Adding a New Regulatory Framework
1. Open [`governed_data_layer/regulatory_frameworks.json`](file:///c:/Users/202140/OneDrive%20-%20RCG%20Global%20Services,%20Inc/Desktop/Finshield/governed_data_layer/regulatory_frameworks.json).
2. Add a new framework entry with `id`, `authority`, `code`, `title`, and `summary`.
3. The AI and frontend will immediately incorporate it into the citation engine!

### C. Adding a New Geography Multiplier
1. Open [`governed_data_layer/geography_risk_table.json`](file:///c:/Users/202140/OneDrive%20-%20RCG%20Global%20Services,%20Inc/Desktop/Finshield/governed_data_layer/geography_risk_table.json).
2. Add or adjust the country's `risk_multiplier` (e.g., `1.8` for UAE, `1.9` for Nigeria, `3.0` for Sanctioned).

### D. Tuning Prompts
1. Navigate to [`prompts/risk_scoring/`](file:///c:/Users/202140/OneDrive%20-%20RCG%20Global%20Services,%20Inc/Desktop/Finshield/prompts/risk_scoring/).
2. Create a new semantic version file: `v1.3.0_YYYY-MM-DD.json`.
3. Update `system_prompt` and `output_schema`.

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
