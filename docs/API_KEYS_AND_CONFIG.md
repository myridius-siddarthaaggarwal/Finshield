# 🔑 FinShield — Environment Variables & API Configuration Guide

> **Target Audience**: Developers, DevOps Engineers, Hackathon Team  
> **Configuration File**: [`.env`](file:///c:/Users/202140/OneDrive%20-%20RCG%20Global%20Services,%20Inc/Desktop/Finshield/.env) (copy from [`.env.example`](file:///c:/Users/202140/OneDrive%20-%20RCG%20Global%20Services,%20Inc/Desktop/Finshield/.env.example))  

---

## ⚙️ 1. Complete Environment Variables Matrix

| Variable | Type | Default Value | Purpose / Description |
| :--- | :--- | :--- | :--- |
| **`LLM_PROVIDER`** | `string` | `auto` | Active AI provider: `auto` (detects key), `gemini`, or `anthropic`. |
| **`GEMINI_API_KEY`** | `string` | `""` (Empty / Optional) | Google Gemini API Key (Gemini 1.5 Pro, 2.5 Pro, Flash). |
| **`ANTHROPIC_API_KEY`** | `string` | `""` (Empty / Optional) | Anthropic Claude API Key for Claude 3.7 Sonnet reasoning. |
| **`LLM_MODEL`** | `string` | `gemini-1.5-pro` | Model identifier (e.g., `gemini-1.5-pro`, `gemini-2.5-pro`, `claude-3-7-sonnet-20250219`). |
| **`LLM_TEMPERATURE`** | `float` | `0.1` | Low temperature for strict regulatory determinism. |
| **`CONFIDENCE_THRESHOLD`** | `float` | `0.70` | Below $70\%$ confidence, system flags manual assessment path. |
| **`DATABASE_URL`** | `string` | `sqlite:///./finshield.db` | Database connection string. Swap to PostgreSQL in production. |
| **`SECRET_KEY`** | `string` | `finshield-secret-key-2026` | Secret key used for signing cryptographic JWT tokens. |
| **`ACCESS_TOKEN_EXPIRE_MINUTES`** | `int` | `1440` (24 Hours) | JWT bearer token expiration window. |
| **`CORS_ORIGINS`** | `string` | `http://localhost:5173,http://localhost:3000` | Comma-separated list of allowed frontend origins. |
| **`OPEN_SANCTIONS_API_KEY`** | `string` | `""` (Optional) | API Key for external OpenSanctions live API. |

---

## 🔑 2. How to Generate Your Google Gemini API Key

You can generate a Gemini API key directly from Google AI Studio:

1. **Open Google AI Studio**:
   - Go to [https://aistudio.google.com/](https://aistudio.google.com/) or direct URL [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey).
2. **Locate the API Key Section**:
   - **In the left sidebar**: Look at the bottom-left toolbar (right next to your user avatar `PRO`).
   - Click the **Key icon (`🔑`)** (the 4th icon next to the search icon).
3. **Generate Key**:
   - Click **"Create API key"**.
   - Select **"Create API key in new project"** (or choose an existing project).
4. **Copy & Paste into `.env`**:
   - Copy the `AIzaSy...` key.
   - Paste it into your [`.env`](file:///c:/Users/202140/OneDrive%20-%20RCG%20Global%20Services,%20Inc/Desktop/Finshield/.env) file:
     ```ini
     LLM_PROVIDER=gemini
     GEMINI_API_KEY=AIzaSyYourGeneratedKeyHere
     LLM_MODEL=gemini-1.5-pro
     ```

---

## 🛡️ 3. Multi-Provider Architecture & Graceful Fallback Engine

FinShield includes an enterprise multi-provider LLM adapter ([`backend/app/services/llm_client.py`](file:///c:/Users/202140/OneDrive%20-%20RCG%20Global%20Services,%20Inc/Desktop/Finshield/backend/app/services/llm_client.py)):

### Provider Selection Modes:
1. **Google Gemini Pro (`LLM_PROVIDER=gemini` or `auto`)**:
   - Connects to Google's REST API (`https://generativelanguage.googleapis.com/v1beta/models/...:generateContent`).
   - Uses native `responseMimeType: "application/json"` for rock-solid structured output.
2. **Anthropic Claude (`LLM_PROVIDER=anthropic`)**:
   - Connects to the Anthropic Messages API (`https://api.anthropic.com/v1/messages`).
3. **Offline / Fallback (When no key is configured or network is offline)**:
   - Automatically activates the **Calibrated Deterministic Reasoning Engine**.
   - Computes domain-accurate scores and regulatory citations based on the proposal's division, change type, and geography without crashing or stalling.
   - **Result**: Your live demo works **100% reliably** under any conference Wi-Fi or API rate-limit condition!

---

## 🔐 4. Setting Up Your Local `.env` File

Open [`.env`](file:///c:/Users/202140/OneDrive%20-%20RCG%20Global%20Services,%20Inc/Desktop/Finshield/.env) in your editor and configure your preferred provider:

```ini
# --- Option 1: Google Gemini (Gemini Pro / Flash) ---
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSyYourGeminiApiKeyHere
LLM_MODEL=gemini-1.5-pro

# --- Option 2: Anthropic Claude ---
# LLM_PROVIDER=anthropic
# ANTHROPIC_API_KEY=sk-ant-api03-...
# LLM_MODEL=claude-3-7-sonnet-20250219

# --- Option 3: Auto-Detect ---
# LLM_PROVIDER=auto
```

---

## 🚀 5. Deployment on Railway / Render

When deploying the backend on **Railway.app** or **Render.com**:
1. Connect your GitHub repository `Finshield`.
2. Set the Root Directory to `/`.
3. Set the Build Command: `pip install -r backend/requirements.txt`
4. Set the Start Command: `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variables:
   - `GEMINI_API_KEY` = your live Gemini API key
   - `LLM_PROVIDER` = `gemini`
   - `SECRET_KEY` = a secure random string
   - `DATABASE_URL` = (Provided automatically by Railway PostgreSQL or SQLite)
