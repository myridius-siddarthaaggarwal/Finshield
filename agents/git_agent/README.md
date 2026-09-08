# 🤖 FinShield Git Agent & MCP Tooling

The **FinShield Git Agent** automates repository operations for hackathon team collaboration, enabling agents (and humans) to stage, commit, branch, push, and sync changes seamlessly.

---

## 🚀 Quick CLI Usage

### 1. Check Status
```bash
python agents/git_agent/git_agent.py status
```
Returns structured JSON with branch, staged, unstaged, untracked files, and remote status.

### 2. Conventional Commit
```bash
python agents/git_agent/git_agent.py commit -m "add hybrid scoring engine" -s backend -t feat
```
Output commit: `feat(backend): add hybrid scoring engine`

### 3. Create Feature Branch
```bash
python agents/git_agent/git_agent.py branch feature/analyst-override-ui
```

### 4. Set GitHub Remote
```bash
python agents/git_agent/git_agent.py set-remote https://github.com/your-org/finshield.git
```

### 5. One-Command Sync (Stage + Commit + Pull + Push)
```bash
python agents/git_agent/git_agent.py sync -m "feat(api): connect committee voting endpoints"
```

---

## 🔌 MCP Server Configuration
To use this with Antigravity / Claude / Cursor MCP clients:
1. Register `agents/git_agent/mcp_git_server.json` in your client's MCP configuration.
2. The agent will have access to: `git_status`, `git_commit`, `git_branch`, `git_sync`, `git_push`, `git_pull`, `git_set_remote`.
