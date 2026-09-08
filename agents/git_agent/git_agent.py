#!/usr/bin/env python3
"""
FinShield Git Automation Agent
Provides automated Git repository management, conventional commits, branching,
remote synchronization, and MCP-compatible interface for team collaboration.
"""

import argparse
import json
import subprocess
import sys
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
            print("[GitAgent] Initializing new git repository...")
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

        # Remotes
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

        # If conventional commit prefix is not present, add it
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
            return f"Pull failed or no upstream configured: {res.stderr.strip()}"
        return res.stdout.strip()

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
            return f"Push failed: {res.stderr.strip()}"
        return res.stdout.strip() or f"Successfully pushed branch '{curr_branch}' to {remote}."

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


def main():
    parser = argparse.ArgumentParser(description="FinShield Git Agent Automation CLI")
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

    # Sync
    sync_parser = subparsers.add_parser("sync", help="One-command Stage, Commit, Pull & Push")
    sync_parser.add_argument("-m", "--message", required=True, help="Commit message")
    sync_parser.add_argument("--remote", default="origin", help="Remote name")

    args = parser.parse_args()

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
    elif args.action == "sync":
        res = agent.sync(args.message, args.remote)
        print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
