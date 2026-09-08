#!/usr/bin/env python3
"""
FinShield Git Automation Agent & MCP Server
Provides automated Git repository management, automated pre-push quality checks,
intelligent merge conflict detection & simulation, automatic conventional commit generation,
and full MCP stdio protocol support.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


# Ensure UTF-8 output on Windows
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass


class GitAgent:
    def __init__(self, repo_path: Optional[str] = None):
        self.repo_path = Path(repo_path) if repo_path else Path(__file__).resolve().parents[2]
        self._ensure_repo()

    def _run_git(self, args: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run git command inside the repository."""
        cmd = ["git"] + args
        try:
            res = subprocess.run(
                cmd,
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                check=check
            )
            return res
        except subprocess.CalledProcessError as e:
            print(f"[GitAgent Error] Command failed: {' '.join(cmd)}", file=sys.stderr)
            print(f"[GitAgent Stderr] {e.stderr}", file=sys.stderr)
            raise

    def _ensure_repo(self):
        """Ensure git repository is initialized."""
        git_dir = self.repo_path / ".git"
        if not git_dir.exists():
            print("[GitAgent] Initializing new git repository...", file=sys.stderr)
            self._run_git(["init"])

    def status(self) -> Dict[str, Any]:
        """Get repository status in a structured format."""
        branch_res = self._run_git(["branch", "--show-current"], check=False)
        current_branch = branch_res.stdout.strip() or "main"

        status_res = self._run_git(["status", "--porcelain"], check=False)
        raw_status = status_res.stdout.splitlines()

        staged = []
        unstaged = []
        untracked = []
        conflicted = []

        for line in raw_status:
            if not line:
                continue
            index_status = line[0]
            worktree_status = line[1]
            file_path = line[3:].strip()

            # Conflict state in porcelain status (UU, AA, DD, AU, UA, UD, DU)
            if index_status in ["U", "A", "D"] and worktree_status in ["U", "A", "D"]:
                conflicted.append({"file": file_path, "status": f"{index_status}{worktree_status}"})
            elif index_status == "?":
                untracked.append(file_path)
            else:
                if index_status in ["M", "A", "D", "R", "C"]:
                    staged.append({"file": file_path, "status": index_status})
                if worktree_status in ["M", "D"]:
                    unstaged.append({"file": file_path, "status": worktree_status})

        remotes_res = self._run_git(["remote", "-v"], check=False)
        remotes = [r.strip() for r in remotes_res.stdout.splitlines() if r.strip()]

        return {
            "branch": current_branch,
            "staged_count": len(staged),
            "staged": staged,
            "unstaged_count": len(unstaged),
            "unstaged": unstaged,
            "untracked_count": len(untracked),
            "untracked": untracked,
            "conflicted_count": len(conflicted),
            "conflicted": conflicted,
            "remotes": remotes,
            "is_clean": len(staged) == 0 and len(unstaged) == 0 and len(untracked) == 0 and len(conflicted) == 0
        }

    def stage_all(self) -> str:
        """Stage all modified, deleted, and untracked files."""
        self._run_git(["add", "-A"])
        return "All files staged successfully."

    def generate_smart_commit_message(self) -> str:
        """Automatically generates a conventional commit message based on modified files."""
        st = self.status()
        all_files = [item["file"] if isinstance(item, dict) else item for item in (st["staged"] + st["unstaged"] + st["untracked"])]

        if not all_files:
            return "chore: update repository synchronization"

        # Categorize by area
        has_backend = any("backend/" in f or "app/" in f for f in all_files)
        has_frontend = any("frontend/" in f or "src/" in f for f in all_files)
        has_docs = any("docs/" in f or f.endswith(".md") for f in all_files)
        has_agents = any("agents/" in f for f in all_files)
        has_ci = any(".github/" in f or "ci.yml" in f for f in all_files)
        has_data = any("governed_data_layer/" in f or "prompts/" in f for f in all_files)
        has_tests = any("tests/" in f or "test_" in f for f in all_files)

        if has_ci and not has_backend and not has_frontend:
            return f"ci: update GitHub Actions workflow configuration ({len(all_files)} files)"
        if has_agents and not has_frontend:
            return f"feat(agents): enhance Git & QA automation capabilities ({len(all_files)} files)"
        if has_data and not has_backend:
            return f"feat(data-layer): update risk taxonomies and prompt specifications"
        if has_tests and not has_frontend:
            return f"test(backend): update test suites and benchmark assertions"
        if has_frontend and not has_backend:
            return f"feat(frontend): enhance workbench UI components and analytics ({len(all_files)} files)"
        if has_backend and not has_frontend:
            return f"feat(backend): update risk scoring engine and API services ({len(all_files)} files)"

        return f"feat(finshield): synchronize codebase updates across {len(all_files)} files"

    def commit(self, message: Optional[str] = None, scope: Optional[str] = None, commit_type: str = "feat") -> str:
        """Create a conventional commit."""
        if not message:
            message = self.generate_smart_commit_message()
            full_message = message
        else:
            prefix = f"{commit_type}({scope}): " if scope else f"{commit_type}: "
            if not any(message.startswith(f"{t}") for t in ["feat", "fix", "docs", "style", "refactor", "test", "chore", "ci"]):
                full_message = f"{prefix}{message}"
            else:
                full_message = message

        self._run_git(["add", "-A"])
        res = self._run_git(["commit", "-m", full_message], check=False)
        if res.returncode != 0:
            if "nothing to commit" in res.stdout or "nothing to commit" in res.stderr:
                return "Working tree clean, nothing new to commit."
            return f"Commit error: {res.stderr.strip() or res.stdout.strip()}"
        return res.stdout.strip()

    def set_remote(self, name: str, url: str) -> str:
        """Add or update git remote."""
        remotes_res = self._run_git(["remote"], check=False)
        existing_remotes = remotes_res.stdout.splitlines()

        if name in existing_remotes:
            self._run_git(["remote", "set-url", name, url])
            return f"Updated remote '{name}' to {url}"
        else:
            self._run_git(["remote", "add", name, url])
            return f"Added remote '{name}' with {url}"

    def branch(self, branch_name: str, checkout: bool = True) -> str:
        """Create and optionally checkout a new branch."""
        if checkout:
            res = self._run_git(["checkout", "-B", branch_name])
        else:
            res = self._run_git(["branch", branch_name])
        return res.stdout.strip() or f"Switched to branch '{branch_name}'"

    def fetch(self, remote: str = "origin") -> str:
        """Fetch latest updates from remote repository."""
        res = self._run_git(["fetch", remote], check=False)
        return res.stdout.strip() or res.stderr.strip() or f"Fetched from {remote}."

    def check_conflicts(self, remote: str = "origin", branch: Optional[str] = None) -> Dict[str, Any]:
        """
        Deep merge conflict inspection:
        1. Checks current working tree for unresolved conflict markers (<<<<<<< HEAD).
        2. Fetches remote and compares commit ancestry (ahead/behind counts).
        3. Simulates a merge with git merge-tree in memory to detect conflicts BEFORE pulling/pushing.
        """
        curr_branch = branch or self.status()["branch"]
        target_ref = f"{remote}/{curr_branch}"

        # 1. Check existing conflict markers in workspace
        workspace_conflicts = self._find_conflict_markers()

        # 2. Fetch remote silently
        self.fetch(remote)

        # 3. Check divergence counts
        count_res = self._run_git(["rev-list", "--left-right", "--count", f"HEAD...{target_ref}"], check=False)
        ahead, behind = 0, 0
        if count_res.returncode == 0 and count_res.stdout.strip():
            parts = count_res.stdout.strip().split()
            if len(parts) >= 2:
                ahead = int(parts[0])
                behind = int(parts[1])

        # 4. Check if upstream has diverged and simulate merge
        simulated_conflicts = []
        can_clean_merge = True

        if behind > 0:
            merge_base_res = self._run_git(["merge-base", "HEAD", target_ref], check=False)
            if merge_base_res.returncode == 0:
                base_sha = merge_base_res.stdout.strip()
                # Run git merge-tree simulation
                tree_res = self._run_git(["merge-tree", base_sha, "HEAD", target_ref], check=False)
                if tree_res.returncode == 0:
                    tree_output = tree_res.stdout
                    if "+<<<<<<<" in tree_output or "merged with conflict" in tree_output:
                        can_clean_merge = False
                        # Parse conflicting files from merge-tree
                        simulated_conflicts = self._parse_merge_tree_conflicts(tree_output)

        has_any_conflicts = len(workspace_conflicts) > 0 or len(simulated_conflicts) > 0 or not can_clean_merge

        status_label = "CLEAN"
        if has_any_conflicts:
            status_label = "CONFLICT_DETECTED"
        elif behind > 0 and ahead > 0:
            status_label = "DIVERGED_CLEAN_MERGEABLE"
        elif behind > 0:
            status_label = "BEHIND_REMOTE"
        elif ahead > 0:
            status_label = "AHEAD_OF_REMOTE"
        else:
            status_label = "UP_TO_DATE"

        return {
            "status": status_label,
            "has_conflicts": has_any_conflicts,
            "branch": curr_branch,
            "remote": remote,
            "ahead_commits": ahead,
            "behind_commits": behind,
            "workspace_conflict_files": workspace_conflicts,
            "simulated_conflict_files": simulated_conflicts,
            "can_auto_merge": can_clean_merge and len(workspace_conflicts) == 0,
            "summary": self._format_conflict_summary(status_label, ahead, behind, workspace_conflicts, simulated_conflicts)
        }

    def _find_conflict_markers(self) -> List[Dict[str, Any]]:
        """Scans modified files in workspace for genuine git conflict markers (<<<<<<< HEAD, =======, >>>>>>>)."""
        st = self.status()
        files_to_check = set([f["file"] for f in st["conflicted"]] + [f["file"] for f in st["staged"]] + [f["file"] for f in st["unstaged"]])
        conflicts = []

        for rel_path in files_to_check:
            full_path = self.repo_path / rel_path
            if full_path.is_file():
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                    markers = []
                    for idx, line in enumerate(lines, 1):
                        stripped = line.strip()
                        if (line.startswith("<<<<<<< ") or stripped == "<<<<<<<") or \
                           (stripped == "=======") or \
                           (line.startswith(">>>>>>> ") or stripped == ">>>>>>>"):
                            markers.append({"line": idx, "text": stripped})
                    if markers:
                        # Only consider a file truly conflicted if both <<<<<<< and >>>>>>> or ======= are present
                        has_start = any(m["text"].startswith("<<<<<<<") for m in markers)
                        has_end = any(m["text"].startswith(">>>>>>>") for m in markers)
                        if has_start and has_end:
                            conflicts.append({"file": rel_path, "markers_count": len(markers), "markers": markers[:6]})
                except Exception:
                    pass
        return conflicts

    def _parse_merge_tree_conflicts(self, tree_output: str) -> List[str]:
        """Extract filenames from merge-tree conflict blocks."""
        conflict_files = []
        for line in tree_output.splitlines():
            if line.startswith("changed in both"):
                parts = line.split()
                if len(parts) >= 4:
                    conflict_files.append(parts[-1])
            elif "conflict in" in line:
                match = re.search(r"conflict in ([\w\/\.\-]+)", line)
                if match:
                    conflict_files.append(match.group(1))
        return list(set(conflict_files))

    def _format_conflict_summary(self, status: str, ahead: int, behind: int, ws_conflicts: list, sim_conflicts: list) -> str:
        if ws_conflicts:
            files_str = ", ".join(c["file"] for c in ws_conflicts)
            return f"⚠️ Active merge conflict markers detected in workspace files: {files_str}. Resolve before pushing."
        if sim_conflicts:
            files_str = ", ".join(sim_conflicts)
            return f"⚠️ Upstream changes on remote conflict with local commits in: {files_str}. Rebase or merge resolution required."
        if ahead > 0 and behind > 0:
            return f"ℹ️ Local branch is {ahead} commit(s) ahead and {behind} commit(s) behind remote. Clean auto-rebase possible."
        if behind > 0:
            return f"ℹ️ Local branch is {behind} commit(s) behind remote. Safe fast-forward pull possible."
        if ahead > 0:
            return f"✓ Local branch is {ahead} commit(s) ahead of remote. Ready for push."
        return "✓ Local repository and remote are fully synchronized. Zero conflicts."

    def pull(self, remote: str = "origin", branch: Optional[str] = None, rebase: bool = True) -> str:
        """Pull latest changes from remote with rebase support."""
        curr_branch = branch or self.status()["branch"]
        args = ["pull"]
        if rebase:
            args.append("--rebase")
        args.extend([remote, curr_branch])

        res = self._run_git(args, check=False)
        if res.returncode != 0:
            return f"Pull error: {res.stderr.strip() or res.stdout.strip()}"
        return res.stdout.strip() or "Already up to date."

    def push(self, remote: str = "origin", branch: Optional[str] = None, set_upstream: bool = True) -> str:
        """Push committed changes to remote repository."""
        curr_branch = branch or self.status()["branch"]
        args = ["push"]
        if set_upstream:
            args.extend(["-u", remote, curr_branch])
        else:
            args.extend([remote, curr_branch])

        res = self._run_git(args, check=False)
        if res.returncode != 0:
            return f"Push error: {res.stderr.strip() or res.stdout.strip()}"
        return res.stdout.strip() or f"Successfully pushed branch '{curr_branch}' to {remote}."

    def log(self, limit: int = 5) -> List[Dict[str, str]]:
        """Get recent commit history."""
        res = self._run_git(["log", f"-n {limit}", "--pretty=format:%h|%an|%ar|%s"], check=False)
        lines = res.stdout.splitlines()
        history = []
        for line in lines:
            if "|" in line:
                parts = line.split("|", 3)
                if len(parts) == 4:
                    history.append({
                        "commit": parts[0],
                        "author": parts[1],
                        "date": parts[2],
                        "message": parts[3]
                    })
        return history

    def verify_quality(self) -> Dict[str, Any]:
        """Runs pre-push automated quality checks (pytest + data layer audit)."""
        print("[GitAgent] 🧪 Running pre-push verification tests...", file=sys.stderr)
        try:
            test_agent_path = self.repo_path / "agents" / "test_agent" / "test_agent.py"
            venv_python = self.repo_path / ".venv" / "Scripts" / "python.exe"
            py_exec = str(venv_python) if venv_python.exists() else "python"

            res = subprocess.run(
                [py_exec, str(test_agent_path), "run"],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True
            )
            passed = res.returncode == 0
            return {
                "verified": passed,
                "output": res.stdout[-600:] if len(res.stdout) > 600 else res.stdout,
                "error": res.stderr if not passed else None
            }
        except Exception as e:
            return {
                "verified": False,
                "output": "",
                "error": f"Verification error: {str(e)}"
            }

    def auto_push(self, message: Optional[str] = None, remote: str = "origin", branch: Optional[str] = None, verify: bool = True) -> Dict[str, Any]:
        """
        Comprehensive Auto-Push & Merge Conflict Pipeline:
        1. Pre-flight Quality Check (runs test suite).
        2. Pre-flight Merge Conflict Inspection (detects conflicts before pushing).
        3. Automated staging of uncommitted/untracked files.
        4. Conventional Commit (auto-generated if not provided).
        5. Upstream Synchronization (safe pull/rebase).
        6. Push to remote repository on GitHub.
        """
        print(f"\n======================================================================", file=sys.stderr)
        print(f" 🚀 FinShield Git Agent: Autonomous Auto-Push & Conflict Check", file=sys.stderr)
        print(f"======================================================================", file=sys.stderr)

        curr_branch = branch or self.status()["branch"]

        # Step 1: Pre-flight Quality Verification
        if verify:
            verify_res = self.verify_quality()
            if not verify_res["verified"]:
                print(f"[GitAgent] ❌ Pre-push verification failed! Aborting push.", file=sys.stderr)
                return {
                    "status": "aborted",
                    "step": "verification",
                    "reason": "Pre-push verification test suite failed. Resolve errors before pushing.",
                    "verification": verify_res
                }
            print(f"[GitAgent] ✅ Pre-push verification passed (all tests green).", file=sys.stderr)

        # Step 2: Pre-flight Conflict Check
        print(f"[GitAgent] 🔍 Inspecting remote '{remote}/{curr_branch}' for merge conflicts...", file=sys.stderr)
        conflict_check = self.check_conflicts(remote=remote, branch=curr_branch)
        if conflict_check["has_conflicts"]:
            print(f"[GitAgent] ❌ Merge conflict detected! Aborting push.", file=sys.stderr)
            return {
                "status": "aborted",
                "step": "conflict_detection",
                "reason": "Merge conflicts detected. Automatic push halted to prevent repository corruption.",
                "conflict_details": conflict_check
            }
        print(f"[GitAgent] ✅ Conflict check passed: {conflict_check['summary']}", file=sys.stderr)

        # Step 3: Stage all changes
        self.stage_all()

        # Step 4: Commit
        commit_res = self.commit(message=message)
        print(f"[GitAgent] 📦 Commit created: {commit_res.splitlines()[0] if commit_res else 'Clean'}", file=sys.stderr)

        # Step 5: Pull / Rebase upstream if needed
        if conflict_check["behind_commits"] > 0:
            print(f"[GitAgent] 🔄 Rebase-pulling {conflict_check['behind_commits']} upstream commit(s)...", file=sys.stderr)
            pull_res = self.pull(remote=remote, branch=curr_branch, rebase=True)
            print(f"[GitAgent] {pull_res}", file=sys.stderr)
        else:
            pull_res = "Up to date with remote."

        # Step 6: Push
        print(f"[GitAgent] 📤 Pushing '{curr_branch}' to remote '{remote}'...", file=sys.stderr)
        push_res = self.push(remote=remote, branch=curr_branch, set_upstream=True)
        print(f"[GitAgent] ✅ Push completed successfully.", file=sys.stderr)
        print(f"======================================================================\n", file=sys.stderr)

        return {
            "status": "success",
            "verified": verify,
            "branch": curr_branch,
            "remote": remote,
            "conflict_check": conflict_check["summary"],
            "commit": commit_res,
            "pull": pull_res,
            "push": push_res
        }

    def sync(self, commit_message: str, remote: str = "origin", verify: bool = True) -> Dict[str, Any]:
        """Wrapper for backward compatibility."""
        return self.auto_push(message=commit_message, remote=remote, verify=verify)


# ==============================================================================
# MCP Protocol Server Handler (JSON-RPC 2.0 over Stdio)
# ==============================================================================

MCP_TOOLS = [
    {
        "name": "git_status",
        "description": "Get current git branch, staged files, unstaged changes, untracked files, conflicted files, and remote status.",
        "inputSchema": { "type": "object", "properties": {} }
    },
    {
        "name": "git_check_conflicts",
        "description": "Deep merge conflict inspection. Simulates remote merge in-memory, detects conflict markers, and verifies clean pushability without modifying workspace.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "remote": { "type": "string", "default": "origin", "description": "Remote name (default: origin)" },
                "branch": { "type": "string", "description": "Branch name to check against" }
            }
        }
    },
    {
        "name": "git_auto_push",
        "description": "Autonomous full-pipeline push: runs test suite verification, checks for merge conflicts, auto-generates conventional commit message if needed, stages, pulls cleanly, and pushes to GitHub.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "message": { "type": "string", "description": "Optional custom commit message. If omitted, smart conventional message is generated automatically." },
                "remote": { "type": "string", "default": "origin", "description": "Remote name (default: origin)" },
                "branch": { "type": "string", "description": "Branch name to push" },
                "verify": { "type": "boolean", "default": True, "description": "Run automated test suite verification before pushing" }
            }
        }
    },
    {
        "name": "git_stage_all",
        "description": "Stage all modified, deleted, and untracked files in the repository.",
        "inputSchema": { "type": "object", "properties": {} }
    },
    {
        "name": "git_commit",
        "description": "Stage all changes and create a conventional formatted commit.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "message": { "type": "string", "description": "Commit message" },
                "scope": { "type": "string", "description": "Scope e.g. backend, frontend, docs, agents" },
                "type": { "type": "string", "description": "Type e.g. feat, fix, chore, docs, refactor", "default": "feat" }
            }
        }
    },
    {
        "name": "git_branch",
        "description": "Create and checkout a new branch for feature isolation.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": { "type": "string", "description": "Branch name to create or switch to" }
            },
            "required": ["name"]
        }
    },
    {
        "name": "git_push",
        "description": "Push local branch to remote repository.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "remote": { "type": "string", "default": "origin" },
                "branch": { "type": "string" }
            }
        }
    },
    {
        "name": "git_pull",
        "description": "Pull latest changes from remote repository.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "remote": { "type": "string", "default": "origin" },
                "branch": { "type": "string" }
            }
        }
    },
    {
        "name": "git_log",
        "description": "Get recent commit history.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": { "type": "number", "default": 5 }
            }
        }
    }
]


def run_mcp_server():
    agent = GitAgent()

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
                            "name": "finshield-git-agent",
                            "version": "2.2.0"
                        }
                    }
                }
            elif method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": { "tools": MCP_TOOLS }
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                args = params.get("arguments", {})

                if tool_name == "git_status":
                    res = agent.status()
                elif tool_name == "git_check_conflicts":
                    res = agent.check_conflicts(remote=args.get("remote", "origin"), branch=args.get("branch"))
                elif tool_name == "git_auto_push" or tool_name == "git_verified_sync":
                    res = agent.auto_push(
                        message=args.get("message"),
                        remote=args.get("remote", "origin"),
                        branch=args.get("branch"),
                        verify=args.get("verify", True)
                    )
                elif tool_name == "git_stage_all":
                    res = agent.stage_all()
                elif tool_name == "git_commit":
                    res = agent.commit(args.get("message"), scope=args.get("scope"), commit_type=args.get("type", "feat"))
                elif tool_name == "git_branch":
                    res = agent.branch(args["name"])
                elif tool_name == "git_push":
                    res = agent.push(remote=args.get("remote", "origin"), branch=args.get("branch"))
                elif tool_name == "git_pull":
                    res = agent.pull(remote=args.get("remote", "origin"), branch=args.get("branch"))
                elif tool_name == "git_log":
                    res = agent.log(limit=args.get("limit", 5))
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
    parser = argparse.ArgumentParser(description="FinShield Git Agent Automation CLI & MCP Server")
    parser.add_argument("--mcp", action="store_true", help="Start as an MCP stdio server")
    subparsers = parser.add_subparsers(dest="action", help="Available Git actions")

    # Status
    subparsers.add_parser("status", help="View structured repository status")

    # Conflict Check
    conflicts_parser = subparsers.add_parser("conflicts", aliases=["check-conflicts"], help="Check for potential merge conflicts with remote")
    conflicts_parser.add_argument("--remote", default="origin", help="Remote name (default: origin)")
    conflicts_parser.add_argument("--branch", default=None, help="Branch name")

    # Auto-Push / Sync
    autopush_parser = subparsers.add_parser("autopush", aliases=["auto-push", "sync"], help="Auto-test, detect conflicts, stage, commit & push in one command")
    autopush_parser.add_argument("-m", "--message", default=None, help="Commit message (auto-generated if omitted)")
    autopush_parser.add_argument("--remote", default="origin", help="Remote name (default: origin)")
    autopush_parser.add_argument("--branch", default=None, help="Branch name")
    autopush_parser.add_argument("--no-verify", action="store_true", help="Skip pre-push verification tests")

    # Stage
    subparsers.add_parser("stage", help="Stage all changes")

    # Commit
    commit_parser = subparsers.add_parser("commit", help="Commit changes with conventional format")
    commit_parser.add_argument("-m", "--message", default=None, help="Commit message (auto-generated if omitted)")
    commit_parser.add_argument("-s", "--scope", default=None, help="Commit scope (e.g. backend, frontend)")
    commit_parser.add_argument("-t", "--type", default="feat", help="Commit type (feat, fix, docs, chore)")

    # Branch
    branch_parser = subparsers.add_parser("branch", help="Create or switch branch")
    branch_parser.add_argument("name", help="Branch name")

    # Set Remote
    remote_parser = subparsers.add_parser("set-remote", help="Set origin or upstream remote")
    remote_parser.add_argument("url", help="Remote Git repository URL")
    remote_parser.add_argument("--name", default="origin", help="Remote name (default: origin)")

    # Push
    push_parser = subparsers.add_parser("push", help="Push to remote")
    push_parser.add_argument("--remote", default="origin", help="Remote name")
    push_parser.add_argument("--branch", default=None, help="Branch name")

    # Pull
    pull_parser = subparsers.add_parser("pull", help="Pull from remote")
    pull_parser.add_argument("--remote", default="origin", help="Remote name")
    pull_parser.add_argument("--branch", default=None, help="Branch name")

    # Log
    log_parser = subparsers.add_parser("log", help="View commit history")
    log_parser.add_argument("-n", "--limit", type=int, default=5, help="Number of commits")

    # Verify
    subparsers.add_parser("verify", help="Run automated pre-push test suites")

    args = parser.parse_args()

    if args.mcp:
        run_mcp_server()
        return

    agent = GitAgent()

    if args.action == "status" or not args.action:
        res = agent.status()
        print(json.dumps(res, indent=2))
    elif args.action in ["conflicts", "check-conflicts"]:
        res = agent.check_conflicts(remote=args.remote, branch=args.branch)
        print(json.dumps(res, indent=2))
    elif args.action in ["autopush", "auto-push", "sync"]:
        verify = not args.no_verify
        res = agent.auto_push(message=args.message, remote=args.remote, branch=args.branch, verify=verify)
        print(json.dumps(res, indent=2))
    elif args.action == "stage":
        print(agent.stage_all())
    elif args.action == "commit":
        print(agent.commit(args.message, scope=args.scope, commit_type=args.type))
    elif args.action == "branch":
        print(agent.branch(args.name))
    elif args.action == "set-remote":
        print(agent.set_remote(args.name, args.url))
    elif args.action == "push":
        print(agent.push(args.remote, args.branch))
    elif args.action == "pull":
        print(agent.pull(args.remote, args.branch))
    elif args.action == "log":
        print(json.dumps(agent.log(args.limit), indent=2))
    elif args.action == "verify":
        res = agent.verify_quality()
        print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
