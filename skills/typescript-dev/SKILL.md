---
name: "typescript-dev"
description: "TypeScript development. Use for TypeScript, Node.js, Express, Fastify, Zod, vitest, jest. Backend, CLI, libraries only — no frontend frameworks."
metadata:
  user-invocable: "true"
  allowed-tools: "Glob, Read, Grep, Bash, Task, Skill, Edit, Write, EnterPlanMode"
---

Tool names here such as `AskUserQuestion` are Claude Code's. See [tool names](references/tool-names.md) for what to use instead.

# TypeScript Development

**Announce:** "I'm using the typescript-dev skill."

Follow the [development loop](references/shared/development-loop.md). Read [patterns.md](patterns.md) before changing code.

---

## TypeScript-Specific Configuration

### Verification Commands

**Commands:**
- `tsc --noEmit` — type checking
- `eslint` — linting
- `vitest` or `jest` — tests
- Coverage target: 70-80%

**If available, also verify with MCP:**
- PostgreSQL MCP → Query DB state before/after

### Implementation Rules

- **Schema structure** — Zod CRUD variants per entity (CreateInput/UpdateInput/Output), domain-driven `schemas.ts`, types derived via `z.infer`, composition over deep extends chains
- **Minimize complexity** — Map/Set lookups over array scans
- **Preserve compatibility** — `.transform()` for renamed fields, `.default()` for new fields, preserve exported signatures, re-export moved symbols

### Staff Review Configuration

- **Patterns file path:** Path to this skill's `patterns.md`

---

## TypeScript-Specific Rules

- Types are erased at runtime — external data needs Zod validation
- Fix type errors during implementation, not after
- No positive claim without running `tsc --noEmit`

---

## Quality Checklist (TypeScript-Specific)

Check these before reporting the work as done:

- [ ] Using TypeScript 5.x+ features where appropriate
- [ ] `strict: true` enabled in tsconfig.json
- [ ] No `any` types (or explicitly justified)
- [ ] Proper type guards for runtime checks
- [ ] Zod or similar for external data validation
- [ ] ESM imports with proper extensions
- [ ] `tsc --noEmit` passes (no type errors)
- [ ] `eslint` passes
- [ ] Tests pass (`vitest`/`jest`)
