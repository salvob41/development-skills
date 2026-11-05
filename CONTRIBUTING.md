# Contributing to development-skills

Thanks for your interest in improving the plugin. Here's how to contribute effectively.

## The Golden Rule

**No PR is accepted without a regression eval benchmark proving zero regressions.**

This plugin enforces discipline on AI agents — we hold ourselves to the same standard. Every PR must include a `skill-creator` regression report showing that the proposed changes don't degrade any existing behavior. This is non-negotiable.

## Getting Started

1. Fork the repository
2. Install the [`skill-creator`](https://github.com/anthropics/claude-plugins-official) plugin (required):
   ```json
   // ~/.claude/settings.json
   {
     "enabledPlugins": {
       "skill-creator@claude-plugins-official": true
     }
   }
   ```
3. Clone and test locally:
   ```bash
   claude --plugin-dir ./development-skills
   ```
4. Make your changes
5. Run the regression eval suite (see below)
6. Open a PR with the benchmark results

## Regression Testing

Eval cases are in `plugins/development-skills/evals/`. Use `/eval-regression` to select and run them.

## What to Contribute

**High-impact contributions:**
- New language skills (Rust, Go, Kotlin, Ruby, C#) — see the issue template
- Improved patterns for existing languages
- Better anti-rationalization tables
- New evals for uncovered edge cases
- Bug reports with reproduction steps

**Before starting work:** open an issue to discuss the approach. This prevents duplicate effort and ensures alignment with the project's philosophy.

## Skill Structure

Each language skill follows this pattern:
```
skills/
  your-skill/
    SKILL.md          # Frontmatter + instructions
    references/       # Optional reference files
    patterns/         # Optional pattern files
```

The `SKILL.md` must include:
- YAML frontmatter with `name`, `description`, `user-invocable`
- Verification commands (test, lint, build)
- Language-specific implementation rules
- Quality checklist

Look at `skills/python-dev/SKILL.md` as a reference implementation.

## Design Principles

All changes must align with the [Model Behavior Principles](CLAUDE.md):

1. **Maximum honesty, zero accommodation** — skills should make the model challenge wrong approaches
2. **Critical thinking is always on** — never skip evaluation
3. **Planning is 90% of the work** — invest in brainstorming and planning phases
4. **Persist knowledge to disk** — context windows are ephemeral

## Pull Request Checklist

- [ ] Ran `/eval-regression` — all 50 evals pass (zero regressions)
- [ ] `benchmark.md` pasted in PR description
- [ ] New evals added for any new or modified behavior
- [ ] One concern per PR
- [ ] Clear description of what changed and why

## Code of Conduct

Be constructive. We're building tools that enforce quality — let's hold ourselves to the same standard.
