#!/usr/bin/env python3
"""
FinShield Git Automation Agent & MCP Server
Provides automated Git repository management, conventional commits, branching,
remote synchronization, and a full Model Context Protocol (MCP) stdio server.
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, List, Optional


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
        current_branch = branch_res.stdout.strip() or "HEAD (detached)"

        status_res = self._run_git(["status", "--porcelain"], check=False)
        raw_status = status_res.stdout.splitlines()

        staged = []
        unstaged = []
        untracked = []

        for line in raw_status:
            if not line:
                continue
            index_status = line[0]
            worktree_status = line[1]
            file_path = line[3:].strip()

            if index_status == "?":
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
            "remotes": remotes,
            "is_clean": len(staged) == 0 and len(unstaged) == 0 and len(untracked) == 0
        }

    def stage_all(self) -> str:
        """Stage all modified, deleted, and untracked files."""
        self._run_git(["add", "-A"])
        return "All files staged successfully."

    def commit(self, message: str, scope: Optional[str] = None, commit_type: str = "feat") -> str:
        """Create a conventional commit."""
        if not message:
            raise ValueError("Commit message cannot be empty.")

        prefix = f"{commit_type}({scope}): " if scope else f"{commit_type}: "
        if not any(message.startswith(f"{t}") for t in ["feat", "fix", "docs", "style", "refactor", "test", "chore", "ci"]):
            full_message = f"{prefix}{message}"
        else:
            full_message = message

        self._run_git(["add", "-A"])
        res = self._run_git(["commit", "-m", full_message])
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

    def pull(self, remote: str = "origin", branch: Optional[str] = None) -> str:
        """Pull latest changes from remote."""
        curr_branch = branch or self.status()["branch"]
        res = self._run_git(["pull", remote, curr_branch], check=False)
        if res.returncode != 0:
            return f"Pull result: {res.stderr.strip() or res.stdout.strip()}"
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
            return f"Push result: {res.stderr.strip() or res.stdout.strip()}"
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

    def sync(self, commit_message: str, remote: str = "origin") -> Dict[str, Any]:
        """Perform full sync: stage all, commit, pull, and push."""
        stage_msg = self.stage_all()
        commit_msg = self.commit(commit_message)
        curr_branch = self.status()["branch"]
        pull_msg = self.pull(remote, curr_branch)
        push_msg = self.push(remote, curr_branch)

        return {
            "status": "success",
            "branch": curr_branch,
            "commit": commit_msg,
            "pull": pull_msg,
            "push": push_msg
        }


# ==============================================================================
# MCP Protocol Server Handler (JSON-RPC 2.0 over Stdio)
# ==============================================================================

MCP_TOOLS = [
    {
        "name": "git_status",
        "description": "Get current git branch, staged files, unstaged changes, untracked files, and remote status.",
        "inputSchema": { "type": "object", "properties": {} }
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
            },
            "required": ["message"]
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
        "name": "git_sync",
        "description": "Stage all changes, commit, pull latest changes, and push upstream in one command.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "message": { "type": "string", "description": "Commit message" },
                "remote": { "type": "string", "default": "origin" }
            },
            "required": ["message"]
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
    """Runs a standard MCP JSON-RPC stdio server loop."""
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
                            "version": "2.0.0"
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
                elif tool_name == "git_stage_all":
                    res = agent.stage_all()
                elif tool_name == "git_commit":
                    res = agent.commit(args["message"], scope=args.get("scope"), commit_type=args.get("type", "feat"))
                elif tool_name == "git_branch":
                    res = agent.branch(args["name"])
                elif tool_name == "git_push":
                    res = agent.push(remote=args.get("remote", "origin"), branch=args.get("branch"))
                elif tool_name == "git_pull":
                    res = agent.pull(remote=args.get("remote", "origin"), branch=args.get("branch"))
                elif tool_name == "git_sync":
                    res = agent.sync(args["message"], remote=args.get("remote", "origin"))
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

    # Stage
    subparsers.add_parser("stage", help="Stage all changes")

    # Commit
    commit_parser = subparsers.add_parser("commit", help="Commit changes with conventional format")
    commit_parser.add_argument("-m", "--message", required=True, help="Commit message")
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

    # Sync
    sync_parser = subparsers.add_parser("sync", help="One-command Stage, Commit, Pull & Push")
    sync_parser.add_argument("-m", "--message", required=True, help="Commit message")
    sync_parser.add_argument("--remote", default="origin", help="Remote name")

    args = parser.parse_args()

    if args.mcp:
        run_mcp_server()
        return

    agent = GitAgent()

    if args.action == "status" or not args.action:
        res = agent.status()
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
    elif args.action == "sync":
        res = agent.sync(args.message, args.remote)
        print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
