# MCP Toolbox plugin for Codex and Claude

Connect Codex or Claude to PostgreSQL databases using Google's [MCP Toolbox](https://github.com/googleapis/mcp-toolbox). It gives the agent SQL access, schema inspection, query plans, and diagnostics.

Toolbox describes its prebuilt configs as meant for trusted developers working with an agent. Don't use this plugin to connect an application's end users to a database.

## Setup

1. Install Toolbox with `brew install mcp-toolbox`, or download the binary from the [releases page](https://github.com/googleapis/mcp-toolbox/releases).
2. Run `/toolbox-setup`. It asks for a connection name, your connection details, and whether the agent may write.
3. Restart your MCP host if the new server doesn't appear.

Run `/toolbox-setup` again for each additional database.

To configure a connection by hand, add it to `.mcp.json` in your project root. Use the output of `command -v toolbox` as `command`:

```json
{
  "mcpServers": {
    "postgres-shipping-dev": {
      "command": "/opt/homebrew/bin/toolbox",
      "args": ["--prebuilt", "postgres", "--stdio"],
      "env": {
        "POSTGRES_HOST": "db.example.com",
        "POSTGRES_PORT": "5432",
        "POSTGRES_DATABASE": "dbname",
        "POSTGRES_USER": "agent_ro",
        "POSTGRES_PASSWORD": "password",
        "POSTGRES_QUERY_PARAMS": "{\"sslmode\":\"require\"}"
      }
    }
  }
}
```

The config file holds the password in plain text, so add it to `.gitignore`.

Cursor uses the same format in `.cursor/mcp.json`. Codex uses `.codex/config.toml`, and OpenCode uses `opencode.json`. `/toolbox-setup` writes the right format for each.

## Read-only access

Toolbox has no read-only mode. `execute_sql` runs whatever the database role allows, so connect with a read-only role (Postgres 14 or newer):

```sql
CREATE ROLE agent_ro LOGIN PASSWORD '<password>';
GRANT pg_read_all_data, pg_monitor TO agent_ro;
```

This role can read every table in the database. With it, `INSERT`, `DROP`, `CREATE TABLE`, and `pg_read_file` all fail with permission errors. On Postgres 14, roles can also create tables in `public` unless that was revoked.

## Tools

Toolbox provides 29 tools. These are the main ones:

| Tool | Description |
|------|-------------|
| `execute_sql` | Run a SQL statement |
| `list_schemas`, `list_tables`, `list_views`, `list_indexes` | Inspect the schema |
| `get_query_plan` | Get the execution plan for a query |
| `database_overview` | Show the server version, uptime, and connections |
| `list_query_stats` | Report query statistics (needs the `pg_stat_statements` extension) |
| `list_active_queries`, `long_running_transactions`, `list_locks` | Inspect current activity |
| `list_top_bloated_tables`, `list_invalid_indexes` | Find maintenance problems |

## Upgrading from the postgres-mcp plugin

This plugin replaces `postgres-mcp`, which used CrystalDBA's server and no longer installs. Uninstall `postgres-mcp`, install this plugin, and run `/toolbox-setup` for each existing connection, using the same name. There are no index recommendation tools and no `ACCESS_MODE` setting.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Server not connecting | Toolbox exits at startup if it can't connect. Check the error in your MCP host's logs and the `env` values in `.mcp.json` |
| Server not listed | Restart your MCP host and check that it loads the project's `.mcp.json` |
| Error parsing the config at startup | `POSTGRES_QUERY_PARAMS` must be a map such as `{"sslmode":"require"}`, not `sslmode=require` |
| `pg_stat_statements` does not exist | Install that extension to use `list_query_stats`. Other tools still work |
