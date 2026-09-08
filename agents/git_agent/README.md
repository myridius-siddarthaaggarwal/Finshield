# 🤖 FinShield Git Agent & MCP Tooling

The **FinShield Git Agent** provides dual-mode repository management:
1. **Interactive CLI & One-Line Scripts**: For developers to instantly check conflicts, run test suites, commit, and push with zero hassle.
2. **Standard MCP Server**: Allows Antigravity, Claude, Cursor, and autonomous agents to call Git automation tools directly over JSON-RPC stdio.

---

## ⚡ 1. One-Line Auto-Push & Merge Conflict Detection

Whenever you write a single command, the Git Agent will:
1. 🧪 Run full automated test suite (Pytest + Data Layer + Prompts + Frontend).
2. 🔍 Fetch and simulate merge against remote `origin/main` to detect any conflicts in advance.
3. 📦 Auto-stage all modified & untracked files.
4. 📝 Generate a conventional commit message (or use your custom message).
5. 🔄 Pull/rebase upstream changes cleanly.
6. 📤 Push to GitHub remote repository.

### Quick Commands:

**PowerShell Shortcut:**
```powershell
.\autopush
# Or with a custom message:
.\autopush "feat(scoring): enhance override audit trail"
```

**CMD / Batch Shortcut:**
```cmd
autopush.bat "feat(scoring): enhance override audit trail"
```

**Python CLI:**
```bash
python agents/git_agent/git_agent.py autopush -m "feat(ui): update RiskDimensionCards"
```

---

## 🔍 2. Deep Merge Conflict Inspection

To check for conflicts without committing or pushing:

```bash
python agents/git_agent/git_agent.py conflicts
```

Output:
- In-memory merge simulation via `git merge-tree`
- Divergence counts (ahead/behind commits)
- Conflicting files and line hunks breakdown
- Actionable recommendations (clean rebase vs conflict resolution required)

---

## 🚀 3. Standard CLI Commands

### Status
```bash
python agents/git_agent/git_agent.py status
```

### Pre-push Quality Verification
```bash
python agents/git_agent/git_agent.py verify
```

### Conventional Commit
```bash
python agents/git_agent/git_agent.py commit -m "add hybrid scoring engine" -s backend -t feat
```

### Branch Creation & Checkout
```bash
python agents/git_agent/git_agent.py branch feature/analyst-override-ui
```

### Remote Push & Pull
```bash
python agents/git_agent/git_agent.py pull
python agents/git_agent/git_agent.py push
```

---

## 🔌 4. MCP Server Mode

The Git Agent can run directly as an MCP stdio server:

```bash
python agents/git_agent/git_agent.py --mcp
```

### MCP Tools Exposed:
- `git_auto_push`: Runs test suite, checks for conflicts, auto-commits, pulls, and pushes.
- `git_check_conflicts`: Simulates merge in-memory, detects conflicts before pulling/pushing.
- `git_status`: Returns current branch, staged/unstaged counts, untracked/conflicted files.
- `git_stage_all`: Stages all modified and untracked files.
- `git_commit`: Generates structured conventional commits.
- `git_branch`: Manages feature branch creation and checkouts.
- `git_push` & `git_pull`: Interacts with remote repository.
- `git_log`: Retrieves structured commit history.

---

## ⚙️ 5. Registering in `mcp_config.json`

To register this local Git Agent alongside GitHub, Postman, and Atlassian servers:

```json
"finshield-git-agent": {
  "$typeName": "exa.cascade_plugins_pb.CascadePluginCommandTemplate",
  "command": "python",
  "args": [
    "agents/git_agent/git_agent.py",
    "--mcp"
  ],
  "env": {}
}
```
