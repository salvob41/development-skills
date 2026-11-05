---
name: java-dev
description: "Java development. Use for Java, Spring Boot, Maven, Gradle, JPA, Hibernate."
user-invocable: true
allowed-tools: Glob, Read, Grep, Bash, Task, Skill, Edit, Write, EnterPlanMode
---

# Java Development

**Announce:** "I'm using the java-dev skill."

Follow the [development loop](../../shared/development-loop.md). Read [patterns.md](patterns.md) before changing code.

---

## Java-Specific Configuration

### Verification Commands

**Commands:**
- `mvn test` or `gradle test` — run tests
- `mvn compile` or `gradle build` — compilation check
- Check for compiler warnings

**If available, also verify with MCP:**
- PostgreSQL MCP → Query DB state before/after
- Legacy DB MCP → Query legacy databases for data verification

### Implementation Rules

- **Data carrier structure** — Records with CRUD variants per entity (CreateRequest/UpdateRequest/Response), domain-driven packages, composition over deep inheritance
- **Minimize complexity** — efficient streams, HashMap lookups over list scans
- **Preserve compatibility** — Overloaded methods for new params, @JsonProperty for renamed fields, @Deprecated before removal

### Staff Review Configuration

- **Patterns file path:** Path to this skill's `patterns.md`

---

## Java-Specific Rules

- The compiler catches type errors, not logic bugs or concurrency issues — verification is still mandatory
- Understand Spring Boot auto-configuration before relying on it
- No positive claim without running `mvn test` or `gradle test`

---

## Quality Checklist (Java-Specific)

Check these before reporting the work as done:

- [ ] Using Java 21+ features (var, records, switch expressions, pattern matching)
- [ ] Records used for immutable data carriers
- [ ] Constructor injection for all dependencies
- [ ] No raw types — generics used properly
- [ ] Build succeeds without warnings
- [ ] `mvn test` or `gradle test` passes
- [ ] No compiler warnings
