#!/usr/bin/env python3
"""
FinShield Test & Quality Assurance Automation Agent
Runs automated test suites, validates the Governed Data Layer, audits database health,
verifies benchmark cases, and exposes an MCP protocol interface.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional


# Set stdout to utf-8 if possible
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass


class TestAgent:
    def __init__(self, project_root: Optional[str] = None):
        self.root = Path(project_root) if project_root else Path(__file__).resolve().parents[2]
        self.backend_dir = self.root / "backend"
        self.data_layer_dir = self.root / "governed_data_layer"
        self.prompts_dir = self.root / "prompts"
        self.frontend_dir = self.root / "frontend"

    def run_backend_tests(self) -> Dict[str, Any]:
        """Runs the pytest suite across backend/tests/."""
        start_time = time.time()
        venv_pytest = self.root / ".venv" / "Scripts" / "pytest.exe"
        cmd = [str(venv_pytest) if venv_pytest.exists() else "pytest", "tests/", "-v", "--tb=short"]

        try:
            res = subprocess.run(
                cmd,
                cwd=str(self.backend_dir),
                capture_output=True,
                text=True
            )
            duration = round(time.time() - start_time, 2)
            passed = res.returncode == 0
            
            # Parse test summary
            output_lines = res.stdout.splitlines()
            summary_line = [l for l in output_lines if "passed" in l or "failed" in l]
            summary_text = summary_line[-1] if summary_line else ("Passed" if passed else "Failed")

            return {
                "name": "Backend Pytest Suite",
                "passed": passed,
                "duration_seconds": duration,
                "summary": summary_text,
                "raw_output": res.stdout[-800:] if len(res.stdout) > 800 else res.stdout,
                "stderr": res.stderr
            }
        except Exception as e:
            return {
                "name": "Backend Pytest Suite",
                "passed": False,
                "duration_seconds": round(time.time() - start_time, 2),
                "summary": f"Execution error: {str(e)}",
                "raw_output": "",
                "stderr": str(e)
            }

    def audit_governed_data_layer(self) -> Dict[str, Any]:
        """Audits JSON schema validity and completeness of the Governed Data Layer."""
        start_time = time.time()
        files = {
            "geography_risk_table.json": "jurisdictions",
            "regulatory_frameworks.json": "frameworks",
            "control_library.json": "controls",
            "risk_taxonomies.json": "dimensions"
        }

        results = []
        all_passed = True

        for fname, expected_key in files.items():
            fpath = self.data_layer_dir / fname
            if not fpath.exists():
                results.append({"file": fname, "status": "FAIL", "reason": "File does not exist"})
                all_passed = False
                continue

            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if expected_key not in data:
                        results.append({"file": fname, "status": "FAIL", "reason": f"Missing key '{expected_key}'"})
                        all_passed = False
                    else:
                        count = len(data[expected_key])
                        results.append({"file": fname, "status": "PASS", "items_count": count})
            except json.JSONDecodeError as e:
                results.append({"file": fname, "status": "FAIL", "reason": f"Invalid JSON: {str(e)}"})
                all_passed = False

        return {
            "name": "Governed Data Layer Audit",
            "passed": all_passed,
            "duration_seconds": round(time.time() - start_time, 3),
            "files_audited": results
        }

    def audit_prompt_templates(self) -> Dict[str, Any]:
        """Verifies semantic versioned prompt templates in prompts/."""
        start_time = time.time()
        prompts = list(self.prompts_dir.rglob("*.json"))
        results = []
        all_passed = True

        if not prompts:
            return {"name": "Prompt Templates Audit", "passed": False, "reason": "No prompt templates found"}

        for p in prompts:
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    has_prompt = "system_prompt" in data
                    has_schema = "output_schema" in data or "version" in data
                    if has_prompt and has_schema:
                        results.append({"prompt": p.name, "version": data.get("version", "1.0.0"), "status": "PASS"})
                    else:
                        results.append({"prompt": p.name, "status": "FAIL", "reason": "Missing system_prompt or schema"})
                        all_passed = False
            except Exception as e:
                results.append({"prompt": p.name, "status": "FAIL", "reason": str(e)})
                all_passed = False

        return {
            "name": "Prompt Versioning & Schema Audit",
            "passed": all_passed,
            "duration_seconds": round(time.time() - start_time, 3),
            "prompts_audited": results
        }

    def audit_frontend_build(self) -> Dict[str, Any]:
        """Checks if the frontend production build assets exist and are valid."""
        start_time = time.time()
        dist_dir = self.frontend_dir / "dist"
        has_index = (dist_dir / "index.html").exists()
        has_assets = (dist_dir / "assets").exists() and len(list((dist_dir / "assets").glob("*"))) > 0

        passed = has_index and has_assets
        return {
            "name": "Frontend Build Integrity",
            "passed": passed,
            "duration_seconds": round(time.time() - start_time, 3),
            "dist_exists": dist_dir.exists(),
            "has_index_html": has_index,
            "assets_count": len(list((dist_dir / "assets").glob("*"))) if (dist_dir / "assets").exists() else 0
        }

    def run_all_tests(self) -> Dict[str, Any]:
        """Executes all diagnostics and produces a comprehensive quality report."""
        print("[TestAgent] Starting FinShield Full Diagnostic & Verification Suite...", file=sys.stderr)
        
        backend_res = self.run_backend_tests()
        data_layer_res = self.audit_governed_data_layer()
        prompts_res = self.audit_prompt_templates()
        frontend_res = self.audit_frontend_build()

        all_passed = (
            backend_res["passed"] and
            data_layer_res["passed"] and
            prompts_res["passed"] and
            frontend_res["passed"]
        )

        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_status": "PASSED" if all_passed else "FAILED",
            "all_passed": all_passed,
            "suites": {
                "backend_tests": backend_res,
                "governed_data_layer": data_layer_res,
                "prompt_templates": prompts_res,
                "frontend_build": frontend_res
            }
        }

        self._save_markdown_report(report)
        return report

    def _save_markdown_report(self, report: Dict[str, Any]):
        """Generates TEST_REPORT.md in agents/test_agent/ directory."""
        report_file = self.root / "agents" / "test_agent" / "TEST_REPORT.md"
        status_emoji = "✅ ALL SYSTEMS OPERATIONAL" if report["all_passed"] else "❌ ISSUES DETECTED"

        md = f"""# 🧪 FinShield Automated Verification & Test Report

> **Generated At**: `{report['timestamp']}`  
> **Overall Status**: **{status_emoji}**  

---

## 📊 Summary of Test Suites

| Test Suite | Status | Execution Time | Summary / Details |
| :--- | :---: | :--- | :--- |
| **Backend Pytest Suite** | {'✅ PASS' if report['suites']['backend_tests']['passed'] else '❌ FAIL'} | {report['suites']['backend_tests']['duration_seconds']}s | {report['suites']['backend_tests']['summary']} |
| **Governed Data Layer Audit** | {'✅ PASS' if report['suites']['governed_data_layer']['passed'] else '❌ FAIL'} | {report['suites']['governed_data_layer']['duration_seconds']}s | 4 Reference tables verified (FATF, Regs, Controls, Taxonomies) |
| **Prompt Versioning Audit** | {'✅ PASS' if report['suites']['prompt_templates']['passed'] else '❌ FAIL'} | {report['suites']['prompt_templates']['duration_seconds']}s | Semantic prompt schemas valid |
| **Frontend Build Integrity** | {'✅ PASS' if report['suites']['frontend_build']['passed'] else '❌ FAIL'} | {report['suites']['frontend_build']['duration_seconds']}s | Production bundle ready in `frontend/dist/` |

---

## 🔍 Detailed Backend Test Output
```
{report['suites']['backend_tests']['raw_output']}
```
"""
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(md)


# ==============================================================================
# MCP Protocol Server Handler (JSON-RPC 2.0 over Stdio)
# ==============================================================================

MCP_TEST_TOOLS = [
    {
        "name": "run_all_tests",
        "description": "Run full test suite: backend pytest, governed data layer audit, prompt validation, and frontend build check.",
        "inputSchema": { "type": "object", "properties": {} }
    },
    {
        "name": "run_backend_tests",
        "description": "Run Python FastAPI unit and integration tests with pytest.",
        "inputSchema": { "type": "object", "properties": {} }
    },
    {
        "name": "audit_governed_data_layer",
        "description": "Audit JSON validity and completeness of the Governed Data Layer (FATF tables, regulatory frameworks, controls).",
        "inputSchema": { "type": "object", "properties": {} }
    },
    {
        "name": "audit_frontend_build",
        "description": "Check if frontend production assets are built and ready for deployment.",
        "inputSchema": { "type": "object", "properties": {} }
    }
]


def run_mcp_server():
    agent = TestAgent()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            req = json.loads(line)
            req_id = req.get("id")
            method = req.get("method")
            params = req.get("params", {})

            if method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": { "tools": {} },
                        "serverInfo": {
                            "name": "finshield-test-agent",
                            "version": "1.0.0"
                        }
                    }
                }
            elif method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": { "tools": MCP_TEST_TOOLS }
                }
            elif method == "tools/call":
                tool_name = params.get("name")

                if tool_name == "run_all_tests":
                    res = agent.run_all_tests()
                elif tool_name == "run_backend_tests":
                    res = agent.run_backend_tests()
                elif tool_name == "audit_governed_data_layer":
                    res = agent.audit_governed_data_layer()
                elif tool_name == "audit_frontend_build":
                    res = agent.audit_frontend_build()
                else:
                    res = f"Error: Unknown tool '{tool_name}'"

                text_content = json.dumps(res, indent=2) if isinstance(res, (dict, list)) else str(res)
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{ "type": "text", "text": text_content }]
                    }
                }
            else:
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": { "code": -32601, "message": f"Method '{method}' not found" }
                }

            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()

        except Exception as e:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": { "code": -32603, "message": str(e) }
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser(description="FinShield Automated Test & QA Agent")
    parser.add_argument("--mcp", action="store_true", help="Run as an MCP stdio server")
    subparsers = parser.add_subparsers(dest="command", help="Test commands")

    subparsers.add_parser("run", help="Run full diagnostic test suite")
    subparsers.add_parser("backend", help="Run backend tests only")
    subparsers.add_parser("data-layer", help="Audit Governed Data Layer only")
    subparsers.add_parser("frontend", help="Check frontend build only")

    args = parser.parse_args()

    if args.mcp:
        run_mcp_server()
        return

    agent = TestAgent()

    if args.command == "backend":
        res = agent.run_backend_tests()
        print(json.dumps(res, indent=2))
    elif args.command == "data-layer":
        res = agent.audit_governed_data_layer()
        print(json.dumps(res, indent=2))
    elif args.command == "frontend":
        res = agent.audit_frontend_build()
        print(json.dumps(res, indent=2))
    else:
        report = agent.run_all_tests()
        print("\n" + "="*70)
        print(f" 🧪 FinShield Quality & Test Report: {report['overall_status']}")
        print("="*70)
        for name, suite in report["suites"].items():
            icon = "✅" if suite["passed"] else "❌"
            print(f" {icon} {suite.get('name', name)} ({suite.get('duration_seconds', 0)}s)")
            if "summary" in suite:
                print(f"    └─ {suite['summary']}")
        print("="*70)
        print(f" Detailed report written to: agents/test_agent/TEST_REPORT.md\n")


if __name__ == "__main__":
    main()
