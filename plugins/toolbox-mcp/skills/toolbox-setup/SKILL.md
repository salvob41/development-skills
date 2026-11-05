---
name: toolbox-setup
description: "Add a PostgreSQL database connection to this project using Google's MCP Toolbox. Use when asked to 'connect to PostgreSQL', 'add a database connection', 'set up the Postgres MCP', 'set up MCP Toolbox', 'configure database access for your agent', or 'I want the agent to query my database'."
metadata:
  author: salvob41
  version: 1.1.0
  mcp-server: postgres
  category: infrastructure
---

# MCP Toolbox: add a PostgreSQL connection

Add a PostgreSQL database connection using Google's [MCP Toolbox](https://github.com/googleapis/mcp-toolbox). Each invocation adds ONE connection.
Run `/toolbox-setup` again to add more databases.

## When this triggers

- User runs `/toolbox-setup`
- User asks to "set up postgres", "add a database", "configure database connection", etc.
- A postgres MCP tool fails with a connection or setup error

## Config file for each agent

Use the file for the agent you're running in. If you can't tell, ask. The steps below call it the config file.

| Agent | Project config file |
|---|---|
| Claude Code | `.mcp.json` |
| Cursor | `.cursor/mcp.json` |
| Codex | `.codex/config.toml` (Codex only loads it for trusted projects) |
| OpenCode | `opencode.json` |
| Any other agent | Check that agent's MCP docs. The command, args, and env are the same |

## Setup flow

### Step 1: Check existing configuration

On Claude Code, run the check below. On other agents, read the config file and look for server names starting with `postgres-`.

```bash
cat .mcp.json 2>/dev/null | python3 -c "
import sys, json
try:
    servers = {k: v for k, v in json.load(sys.stdin).get('mcpServers', {}).items() if k.startswith('postgres-')}
except Exception:
    servers = {}
print('CONFIGURED: ' + ', '.join(servers) if servers else 'NOT_CONFIGURED')
old = [k for k, v in servers.items() if 'DATABASE_URI' in v.get('env', {})]
if old:
    print('OLD_BACKEND: ' + ', '.join(old))
"
```

- If **NOT_CONFIGURED**: "Let's set up your first PostgreSQL connection."
- If **OLD_BACKEND**: these entries use the removed `postgres-mcp` plugin's launcher and no longer start. Tell the user, then reconfigure each one under the same name by following Steps 2 to 6.
- If **CONFIGURED**: show the existing server names and ask:
  "You already have these PostgreSQL connections: [list]. Do you want to **add another**, or are you having **issues with an existing one**?"
  - If adding another, go to Step 2.
  - If troubleshooting, go to the Troubleshooting section.

### Step 2: Check prerequisites

```bash
command -v toolbox || echo "MISSING_TOOLBOX"
git check-ignore -q <CONFIG_FILE> && echo "CONFIG_IGNORED" || echo "CONFIG_NOT_IGNORED"
```

- If MISSING_TOOLBOX, tell the user to run `brew install mcp-toolbox`, or to download the binary from the [releases page](https://github.com/googleapis/mcp-toolbox/releases) and put it on their PATH. Wait until `command -v toolbox` prints a path. Store that absolute path as TOOLBOX_PATH.
- If CONFIG_NOT_IGNORED, warn the user that the config file will hold the database password in plain text and could be committed. Recommend adding it to `.gitignore`. Don't change `.gitignore` yourself.

### Step 3: Choose access

Ask: "Should the agent be able to write to this database?" Default to **no**.

Toolbox has no read-only mode. `execute_sql` runs whatever the database role allows, so the role is the only control.

- **Read-only (default):** give the user this SQL to run as an admin, using a password they choose. It needs Postgres 14 or newer. On Postgres 14, roles can also create tables in `public` unless that was revoked.

  ```sql
  CREATE ROLE agent_ro LOGIN PASSWORD '<password>';
  GRANT pg_read_all_data, pg_monitor TO agent_ro;
  ```

  This role can read every table in the database. Use its credentials in Step 4.
- **Read-write:** only for development or staging databases. Use an existing non-superuser role if possible.

### Step 4: Ask for connection details

Ask the user for these, using the host's normal question or input mechanism:

1. **Connection name**: this becomes the MCP server name.
   - Examples: `postgres-shipping-dev`, `postgres-billing-prod`, `postgres-analytics-staging`
   - Start the name with `postgres-`. Use only letters, numbers, hyphens, and underscores.
2. **Host and port**: the port defaults to `5432`.
3. **Database name**
4. **Username and password**: the password doesn't need URL encoding.
5. **TLS**: for any database not on `localhost`, recommend `require`.

### Step 5: Generate configuration

Add this ONE server to the config file. **Always merge. Never overwrite existing entries.**

Read the existing file, or start from an empty one. On Claude Code and Cursor, add the new server under `mcpServers`:

```json
{
  "mcpServers": {
    "<NAME>": {
      "command": "<TOOLBOX_PATH>",
      "args": ["--prebuilt", "postgres", "--stdio"],
      "env": {
        "POSTGRES_HOST": "<HOST>",
        "POSTGRES_PORT": "<PORT>",
        "POSTGRES_DATABASE": "<DATABASE>",
        "POSTGRES_USER": "<USER>",
        "POSTGRES_PASSWORD": "<PASSWORD>",
        "POSTGRES_QUERY_PARAMS": "{\"sslmode\":\"require\"}"
      }
    }
  }
}
```

On Codex, add a table to `.codex/config.toml`:

```toml
[mcp_servers.<NAME>]
command = "<TOOLBOX_PATH>"
args = ["--prebuilt", "postgres", "--stdio"]

[mcp_servers.<NAME>.env]
POSTGRES_HOST = "<HOST>"
POSTGRES_PORT = "<PORT>"
POSTGRES_DATABASE = "<DATABASE>"
POSTGRES_USER = "<USER>"
POSTGRES_PASSWORD = "<PASSWORD>"
POSTGRES_QUERY_PARAMS = '{"sslmode":"require"}'
```

On OpenCode, add the server under `mcp` in `opencode.json`:

```json
{
  "mcp": {
    "<NAME>": {
      "type": "local",
      "command": ["<TOOLBOX_PATH>", "--prebuilt", "postgres", "--stdio"],
      "enabled": true,
      "environment": {
        "POSTGRES_HOST": "<HOST>",
        "POSTGRES_PORT": "<PORT>",
        "POSTGRES_DATABASE": "<DATABASE>",
        "POSTGRES_USER": "<USER>",
        "POSTGRES_PASSWORD": "<PASSWORD>",
        "POSTGRES_QUERY_PARAMS": "{\"sslmode\":\"require\"}"
      }
    }
  }
}
```

Omit `POSTGRES_QUERY_PARAMS` when TLS isn't needed. It must be a YAML map as shown. The form `sslmode=require` stops the server from starting.

If the name already exists, overwrite that entry (this allows reconfiguration).

**Host-specific note:** if the MCP host needs an extra opt-in step to load project MCP servers, tell the user what remains. For Claude-style hosts that use `.claude/settings.local.json`, update that file only when that host needs it.

### Step 6: Finish and verify

Tell the user:

1. "Added **<NAME>** to <CONFIG_FILE>."
2. "Restart your agent if required, then check that the server appears and is connected."
3. "To add another database connection, run `/toolbox-setup` again."

After the restart, run this with the new server's `execute_sql` tool:

```sql
SELECT current_user AS role,
       rolsuper OR rolcreaterole OR rolcreatedb
       OR pg_has_role(current_user, 'pg_write_all_data', 'MEMBER')
       OR pg_has_role(current_user, 'pg_read_server_files', 'MEMBER')
       OR pg_has_role(current_user, 'pg_write_server_files', 'MEMBER')
       OR pg_has_role(current_user, 'pg_execute_server_program', 'MEMBER') AS unsafe
FROM pg_roles WHERE rolname = current_user;
```

If the user chose read-only and `unsafe` is true, tell them the connection isn't read-only and that the agent can write or reach server files. Don't run other queries on it until they fix the role. `unsafe` being false doesn't rule out table-level grants or owned tables, which is why Step 3 creates a new role.

## Troubleshooting

If setup completed but tools still don't work:

1. **Check the binary**: run `toolbox --version` and confirm the command in the config file points to it.
2. **Check the startup error**: Toolbox exits at startup if it can't connect, and the error is on stderr. Use the agent's MCP status view or logs.
3. **Check the config file**: verify the environment values, and that `POSTGRES_QUERY_PARAMS` is a map.
4. **`list_query_stats` fails with `pg_stat_statements does not exist`**: the database doesn't have that extension installed. Other tools still work.

## Examples

### Example 1: Add a primary database

User says: "Connect the agent to our production database"
Actions: Create a read-only role, ask for connection details, write the `.mcp.json` entry, run the role check.
Result: The agent can query the database and can't change it.

### Example 2: Add a second database

User says: "Also connect to our analytics database"
Actions: Read the existing `.mcp.json`, ask for the new details, add the entry.
Result: Both databases are available under distinct names.
