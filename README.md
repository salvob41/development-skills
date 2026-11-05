# development-skills

Claude Code plugins for a structured development loop, language-specific guidance, code review, architecture decisions, project documentation, and PostgreSQL access.

Based on [reidemeister94/development-skills](https://github.com/reidemeister94/development-skills).

## How this differs from upstream

| | Upstream | This repo |
|---|---|---|
| Packaging | One plugin | 7 plugins you install separately |
| Language skills | None | `python-dev`, `java-dev`, `typescript-dev`, `frontend-dev`, `swift-dev` |
| Plans and debugging | No `chronicles` or `debugging` skill | Both included |
| Other skills only here | None | `create-skills`, `get-api-docs`, `update-precommit`, `update-reqs` |
| Plugins only here | None | `adr`, `project-documenter`, `toolbox-mcp` |
| `best-practices`, `resolve-merge`, `roast-my-code` | Skills in the main plugin | Separate plugins, with local versions of `best-practices` and `roast-my-code` |
| Machine setup | None | `make setup` links `global/CLAUDE.md` and downloads `ponytail` and `unslop` |

## Installation

```bash
/plugin marketplace add salvob41/development-skills
/plugin install development-skills@development-skills-marketplace
```

Install the other plugins the same way, using the names below.

The repo also ships Codex manifests and a catalog at `.agents/plugins/marketplace.json`. Some skills still contain Claude-specific instructions.

## Plugins

| Plugin | What it adds |
|--------|--------------|
| `development-skills` | The development loop, 32 skills, a read-only staff reviewer agent, and auto-format hooks |
| `best-practices` | Research on current best practices for a technology |
| `resolve-merge` | Systematic merge conflict resolution |
| `roast-my-code` | Code review and an AI-readiness audit scored across 12 dimensions |
| `adr` | Create, list, and update Architecture Decision Records |
| `project-documenter` | Project documentation generated from code, DDLs, and scripts |
| `toolbox-mcp` | PostgreSQL connections through Google's MCP Toolbox, with a read-only role by default |

## The development loop

Each session starts with a short loop. The agent reads the project's standards, settles open decisions, makes the smallest useful change, verifies it, and reports what it didn't check.

A small task goes straight to the edit and the check. Work that needs a lasting record also produces two files:

- `docs/plans/<date>__<task>.md` records the steps and verification results, so the agent can resume after the context clears.
- `docs/chronicles/<date>__<task>.md` records why the work happened: the request, the context, and the rejected alternatives.

See the [in-depth guide](docs/GUIDE.md) for templates and details.

## Syncing from upstream

Sync is one-way, from upstream to this repo. Never push or open PRs upstream, and never run `git merge upstream/main`, because the histories are unrelated.

```bash
make setup          # run once per machine, and rerun to update ponytail and unslop
make sync-upstream  # then review with git diff
```

`make sync-upstream` adds new skills and updates those without local edits. It keeps a skill edited both here and upstream, and reports it. It never touches skills listed in `scripts/upstream-skip`. `scripts/upstream-base` records the last synced commit.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. The original work is by [reidemeister94](https://github.com/reidemeister94), and it draws on [superpowers](https://github.com/obra/superpowers) by Jesse Vincent.
