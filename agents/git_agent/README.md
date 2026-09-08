# 🤖 FinShield Git Agent & MCP Tooling

The **FinShield Git Agent** provides dual-mode repository management:
1. **Interactive CLI**: For team members to easily commit, branch, and sync from the terminal.
2. **Standard MCP Server**: Allows Antigravity, Claude, Cursor, and autonomous agents to call Git tools directly over JSON-RPC stdio.

---

## 🚀 1. CLI Usage Reference

### Status
```bash
python agents/git_agent/git_agent.py status
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

### One-Command Full Sync
```bash
python agents/git_agent/git_agent.py sync -m "feat(api): connect committee voting endpoints"
```

---

## 🔌 2. MCP Server Mode

The Git Agent can run directly as an MCP stdio server:

```bash
python agents/git_agent/git_agent.py --mcp
```

### MCP Tools Exposed:
- `git_status`: Returns current branch, staged/unstaged counts, untracked files, and remote status.
- `git_stage_all`: Stages all modified and untracked files.
- `git_commit`: Generates structured conventional commits.
- `git_branch`: Manages feature branch creation and checkouts.
- `git_push` & `git_pull`: Interacts with remote repository.
- `git_sync`: Stages, commits, pulls, and pushes in a single atomic action.
- `git_log`: Retrieves structured commit history.

---

## ⚙️ 3. Registering in `mcp_config.json`

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
