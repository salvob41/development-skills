---
name: "python-dev"
description: "Python development. Use for Python, FastAPI, Pydantic, asyncpg, pytest, pandas, SQLAlchemy."
metadata:
  user-invocable: "true"
  allowed-tools: "Glob, Read, Grep, Bash, Task, Skill, Edit, Write, EnterPlanMode"
---

Tool names here such as `AskUserQuestion` are Claude Code's. See [tool names](references/tool-names.md) for what to use instead.

# Python Development

**Announce:** "I'm using the python-dev skill."

Follow the [development loop](references/shared/development-loop.md). Read [patterns.md](patterns.md) before changing code.

---

## Python-Specific Configuration

### Verification Commands

**Commands:**
- `pytest` — run tests
- `ruff check` — linting
- `ruff format --check` — formatting
- Coverage target: 70-80%

**If available, also verify with MCP:**
- PostgreSQL MCP → Query DB state before/after
- Legacy DB MCP → Query legacy databases for data verification

### Implementation Rules

- **Model structure** — Pydantic CRUD variants per entity (Base/Create/Update/Read), domain-driven `schemas.py`, AppBaseModel with ConfigDict, composition over deep inheritance
- **Minimize complexity** — generators for large data, dict lookups over list scans
- **Preserve compatibility** — Aliases for renamed fields, defaults for new fields, preserve public signatures, re-export moved symbols

### Staff Review Configuration

- **Patterns file path:** Path to this skill's `patterns.md`

---

## Python-Specific Rules

- Type hints are mandatory — use Pydantic and strict typing per patterns.md
- Tests are required during implementation, not after — RED→GREEN→REFACTOR for every behavior
- No positive claim without running `pytest`
- Pydantic model fields with non-trivial types, defaults, or validators MUST have WHY comments explaining the rationale (e.g., data source format, business rule, cross-system constraint)

---

## Quality Checklist (Python-Specific)

Check these before reporting the work as done:

- [ ] Type hints use built-in types (not `typing.List`, `typing.Dict`)
- [ ] Pydantic for all structured data
- [ ] No global state or hidden dependencies
- [ ] DataFrames copied before mutation
- [ ] Python 3.13+ features where appropriate
- [ ] `ruff check` passes
- [ ] `ruff format` applied
- [ ] `pytest` passes (or alternative verification documented)
- [ ] No `iterrows()` — vectorized ops, `to_dict("records")`, or `groupby` instead
- [ ] Independent DB queries run concurrently (`asyncio.gather` / `ThreadPoolExecutor`)
- [ ] No fetch-then-filter — use JOIN or IN (subquery) instead of 2 round trips
