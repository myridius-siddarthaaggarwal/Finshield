# 🧪 FinShield Test & Quality Assurance Automation Agent

The **FinShield Test Agent** is an automated quality assurance and verification runner. It performs continuous diagnostics across all backend endpoints, unit tests, the Governed Data Layer, prompt schemas, and frontend build readiness.

---

## 🚀 1. CLI Usage

### Run Full Test Suite & Generate Report
```bash
python agents/test_agent/test_agent.py run
```
Output:
```
======================================================================
 🧪 FinShield Quality & Test Report: PASSED
======================================================================
 ✅ Backend Pytest Suite (16 passed in 2.04s)
 ✅ Governed Data Layer Audit (FATF, Regs, Controls, Taxonomies)
 ✅ Prompt Versioning & Schema Audit
 ✅ Frontend Build Integrity (dist/ bundle ready)
======================================================================
 Detailed report written to: agents/test_agent/TEST_REPORT.md
```

### Run Specific Test Modules
```bash
# Backend pytest suite only
python agents/test_agent/test_agent.py backend

# Governed Data Layer integrity audit only
python agents/test_agent/test_agent.py data-layer

# Frontend production build check only
python agents/test_agent/test_agent.py frontend
```

---

## 🔌 2. MCP Server Protocol Mode

The Test Agent can also run as a standard MCP stdio server:

```bash
python agents/test_agent/test_agent.py --mcp
```

### MCP Tools Exposed:
- `run_all_tests`: Executes full test and quality assurance suite.
- `run_backend_tests`: Executes Python pytest suite (16 tests across FSM, hybrid math, screening, and all 7 benchmark cases).
- `audit_governed_data_layer`: Validates JSON schema correctness of FATF risk tables and regulatory libraries.
- `audit_frontend_build`: Verifies frontend production bundle assets.
