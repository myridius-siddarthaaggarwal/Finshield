#!/usr/bin/env python3
"""
FinShield Remote GitHub Repository Creator & Pusher
Creates a remote GitHub repository via GitHub REST API and pushes local code.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
import urllib.request
import urllib.error


def create_and_push(token: str, repo_name: str = "Finshield", is_private: bool = False):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "FinShield-Git-Agent"
    }

    data = json.dumps({
        "name": repo_name,
        "description": "Enterprise AI-Powered Financial Crime Risk Assessment Workbench",
        "private": is_private,
        "auto_init": False
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.github.com/user/repos",
        data=data,
        headers=headers,
        method="POST"
    )

    try:
        print(f"[GitAgent] Creating GitHub repository '{repo_name}' on account...")
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode("utf-8"))
            html_url = res.get("html_url")
            print(f"[GitAgent] Repository created successfully: {html_url}")
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        if e.code == 422 and "already exists" in err_body:
            print(f"[GitAgent] Repository '{repo_name}' already exists.")
            html_url = f"https://github.com/myridius-siddarthaaggarwal/{repo_name}"
        else:
            print(f"[GitAgent HTTP Error] Status {e.code}: {err_body}")
            return

    repo_path = Path(__file__).resolve().parents[2]
    auth_url = f"https://oauth2:{token}@github.com/myridius-siddarthaaggarwal/{repo_name}.git"

    subprocess.run(["git", "remote", "remove", "origin"], cwd=repo_path, capture_output=True)
    subprocess.run(["git", "remote", "add", "origin", auth_url], cwd=repo_path, check=True)
    subprocess.run(["git", "branch", "-M", "main"], cwd=repo_path, check=True)

    print("[GitAgent] Pushing branch 'main' to GitHub...")
    p = subprocess.run(["git", "push", "-u", "origin", "main"], cwd=repo_path, capture_output=True, text=True)

    if p.returncode == 0:
        print(f"[GitAgent] PUSH SUCCESSFUL! Repository live at: {html_url}")
    else:
        print(f"[GitAgent Push Failed] {p.stderr}")


def main():
    parser = argparse.ArgumentParser(description="Create GitHub repository and push code via API")
    parser.add_argument("--token", default=os.getenv("GITHUB_TOKEN"), help="GitHub Personal Access Token")
    parser.add_argument("--name", default="Finshield", help="Repository name (default: Finshield)")
    parser.add_argument("--private", action="store_true", help="Create as private repository")

    args = parser.parse_args()
    token = args.token or os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not token:
        token = input("Enter your GitHub Personal Access Token: ").strip()

    if not token:
        print("Error: GitHub token is required.", file=sys.stderr)
        sys.exit(1)

    create_and_push(token, args.name, args.private)


if __name__ == "__main__":
    main()
