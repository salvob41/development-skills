# PostgreSQL MCP Plugin for Codex and Claude

Connect Codex or Claude to PostgreSQL databases using [CrystalDBA's postgres-mcp](https://github.com/crystaldba/postgres-mcp).

Reference: CrystalDBA `postgres-mcp` is the backend used by this plugin. It was kept because it adds DBA-style capabilities beyond basic SQL access, including schema inspection, `EXPLAIN`, index analysis, workload analysis, and database health tooling.

## What Changed

- Added Codex packaging alongside the existing Claude packaging.
- Kept CrystalDBA as the Postgres MCP backend.
- Updated the setup flow so the plugin guidance is usable from both Codex and Claude.
- Kept project-level `.mcp.json` as the main place where concrete database connections are added.

## Quick Start

1. Run `/postgres-setup`
2. Answer 3 questions: connection name, DATABASE_URI, access mode
3. Restart your MCP host if needed
4. Verify the new server appears in your MCP host

To add more databases, run `/postgres-setup` again.

## Prerequisites

- **uv** (recommended) — `curl -LsSf https://astral.sh/uv/install.sh | sh`
- or **pipx** — `brew install pipx`
- or **Docker**

## Adding Connections

### Via Skill Workflow (recommended)

Run `/postgres-setup`. You'll be asked for:

| Input | Description | Example |
|-------|-------------|---------|
| **Name** | MCP server name (your choice) | `postgres-shipping-dev` |
| **DATABASE_URI** | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| **Access Mode** | `unrestricted` or `restricted` | `unrestricted` |

### Manual configuration

Add to `.mcp.json` in your project root:

```json
{
  "mcpServers": {
    "postgres-shipping-dev": {
      "command": "/path/to/postgres-mcp/scripts/run_postgres_mcp.sh",
      "env": {
        "DATABASE_URI": "postgresql://user:password@host:5432/dbname",
        "ACCESS_MODE": "unrestricted"
      }
    }
  }
}
```

Add multiple connections by adding more entries under `mcpServers`.

## How It Works

1. Your MCP host launches `run_postgres_mcp.sh`
2. The script reads `DATABASE_URI` from the env and starts `postgres-mcp` via uvx
3. The host communicates with the MCP server over stdio

## Available MCP Tools

| Tool | Description |
|------|-------------|
| `list_schemas` | List all schemas in the database |
| `list_objects` | List tables, views, sequences in a schema |
| `get_object_details` | Show detailed info about a table/view |
| `execute_sql` | Execute SQL queries |
| `explain_query` | Get execution plan with cost estimates |
| `analyze_query_indexes` | Recommend indexes for specific queries |
| `analyze_workload_indexes` | Analyze workload and recommend indexes |
| `analyze_db_health` | Check database health |
| `get_top_queries` | Report slowest/most resource-intensive queries |

## Access Modes

| Mode | Description | Use For |
|------|-------------|---------|
| `unrestricted` | Full read/write access | Development, Staging |
| `restricted` | Read-only access | Production |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "No supported runtime found" | Install uv: `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| "DATABASE_URI is not set" | Check the `env` section in `.mcp.json` |
| MCP server not connecting | Restart your MCP host after changing `.mcp.json` |
| Server not listed | Check that your host is loading the project `.mcp.json` configuration |

## File Structure

```
postgres-mcp/
├── .claude-plugin/
│   └── plugin.json
├── .codex-plugin/
│   └── plugin.json
├── skills/
│   └── postgres-setup/
│       └── SKILL.md         # /postgres-setup skill
├── scripts/
│   └── run_postgres_mcp.sh  # Launch MCP server (uvx → pipx → docker)
├── .mcp.json                # Plugin-level Codex MCP stub
├── templates/
│   ├── mcp-config.json      # Template for .mcp.json
│   └── settings-local.json  # Claude-specific local settings template
└── README.md
```
