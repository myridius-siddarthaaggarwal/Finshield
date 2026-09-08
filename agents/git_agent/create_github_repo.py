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
        print(f"[GitAgent] Creating GitHub repository '{repo_name}' via GitHub API...")
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            clone_url = res_data.get("clone_url")
            html_url = res_data.get("html_url")
            print(f"[GitAgent] Repository created successfully: {html_url}")

            # Authenticated URL for seamless pushing
            auth_clone_url = clone_url.replace("https://", f"https://oauth2:{token}@")

            repo_path = Path(__file__).resolve().parents[2]

            # Set remote
            subprocess.run(["git", "remote", "remove", "origin"], cwd=repo_path, capture_output=True)
            subprocess.run(["git", "remote", "add", "origin", auth_clone_url], cwd=repo_path, check=True)
            subprocess.run(["git", "branch", "-M", "main"], cwd=repo_path, check=True)

            print(f"[GitAgent] Pushing 'main' branch to GitHub...")
            push_res = subprocess.run(["git", "push", "-u", "origin", "main"], cwd=repo_path, capture_output=True, text=True)
            
            if push_res.returncode == 0:
                print(f"[GitAgent] PUSH SUCCESSFUL! View your repository at:\n-> {html_url}")
                # Reset remote to clean URL without token in plaintext
                subprocess.run(["git", "remote", "set-url", "origin", clone_url], cwd=repo_path)
            else:
                print(f"[GitAgent Push Error] {push_res.stderr}")

    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        print(f"[GitAgent API Error] Status {e.code}: {err_msg}", file=sys.stderr)
    except Exception as e:
        print(f"[GitAgent Error] {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Create GitHub repository and push code via API")
    parser.add_argument("--token", default=os.getenv("GITHUB_TOKEN"), help="GitHub Personal Access Token (PAT)")
    parser.add_argument("--name", default="Finshield", help="Repository name (default: Finshield)")
    parser.add_argument("--private", action="store_true", help="Create as private repository")

    args = parser.parse_args()

    token = args.token
    if not token:
        token = input("Enter your GitHub Personal Access Token (PAT with 'repo' scope): ").strip()

    if not token:
        print("Error: GitHub token is required.", file=sys.stderr)
        sys.exit(1)

    create_and_push(token, args.name, args.private)


if __name__ == "__main__":
    main()
