# 🔑 FinShield — Environment Variables & API Configuration Guide

> **Target Audience**: Developers, DevOps Engineers, Hackathon Team  
> **Configuration File**: `.env` (copy from `.env.example`)  

---

## ⚙️ 1. Complete Environment Variables Matrix

| Variable | Type | Default Value | Purpose / Description |
| :--- | :--- | :--- | :--- |
| **`ANTHROPIC_API_KEY`** | `string` | `""` (Empty / Optional) | Anthropic Claude API Key for live Claude 3.7 Sonnet reasoning. |
| **`LLM_MODEL`** | `string` | `claude-3-7-sonnet-20250219` | Target LLM model identifier. |
| **`LLM_TEMPERATURE`** | `float` | `0.1` | Low temperature for strict regulatory determinism. |
| **`CONFIDENCE_THRESHOLD`** | `float` | `0.70` | Below $70\%$ confidence, system suppresses AI score to prevent bias. |
| **`DATABASE_URL`** | `string` | `sqlite:///./finshield.db` | Database connection string. Swap to PostgreSQL in production. |
| **`SECRET_KEY`** | `string` | `finshield-secret-key-2026` | Secret key used for signing cryptographic JWT tokens. |
| **`ACCESS_TOKEN_EXPIRE_MINUTES`** | `int` | `1440` (24 Hours) | JWT bearer token expiration window. |
| **`CORS_ORIGINS`** | `string` | `http://localhost:5173,http://localhost:3000` | Comma-separated list of allowed frontend origins. |
| **`OPEN_SANCTIONS_API_KEY`** | `string` | `""` (Optional) | API Key for external OpenSanctions live API. |

---

## 🛡️ 2. Graceful Degradation & Offline Fallback Engine

FinShield includes an enterprise **Graceful Degradation Engine** ([`backend/app/services/ai_service.py`](file:///c:/Users/202140/OneDrive%20-%20RCG%20Global%20Services,%20Inc/Desktop/Finshield/backend/app/services/ai_service.py)):

### How it works:
1. **When `ANTHROPIC_API_KEY` is provided**:
   - The system connects to the live Anthropic API (`https://api.anthropic.com/v1/messages`) using Claude 3.7 Sonnet.
   - It sends the versioned system prompt from `prompts/risk_scoring/` with strict JSON schema constraints.
2. **When `ANTHROPIC_API_KEY` is empty, expired, or network is down**:
   - The backend automatically activates the **Calibrated Deterministic Reasoning Engine**.
   - It computes domain-accurate scores and regulatory citations based on the proposal's division, change type, and geography without crashing or stalling.
   - **Result**: Your live demo works **100% reliably** under any conference Wi-Fi or API rate-limit condition!

---

## 🔐 3. Setting Up Your Local `.env` File

Copy the template from `.env.example`:

```bash
# On Windows PowerShell:
Copy-Item .env.example .env

# On macOS/Linux:
cp .env.example .env
```

Edit `.env` to insert your Claude API key:
```ini
ANTHROPIC_API_KEY=sk-ant-api03-your-anthropic-key-here
LLM_MODEL=claude-3-7-sonnet-20250219
DATABASE_URL=sqlite:///./finshield.db
SECRET_KEY=finshield-secret-key-super-secure-change-in-production-2026
```

---

## 🚀 4. Deployment on Railway / Render

When deploying the backend on **Railway.app** or **Render.com**:
1. Connect your GitHub repository `Finshield`.
2. Set the Root Directory to `/`.
3. Set the Build Command: `pip install -r backend/requirements.txt`
4. Set the Start Command: `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variables:
   - `ANTHROPIC_API_KEY` = your live API key
   - `SECRET_KEY` = a secure random string
   - `DATABASE_URL` = (Provided automatically by Railway PostgreSQL or SQLite)
