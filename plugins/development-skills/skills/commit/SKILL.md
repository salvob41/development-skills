---
name: commit
description: "Create a user-requested Conventional Commit from the staged changes."
user-invocable: true
allowed-tools: Bash, Read, Grep
---

# Commit Skill

This skill is host-agnostic: in Codex, ChatGPT, or Claude-style environments, use the available shell tool to run the git commands below.

Inspect `git diff --cached` and `git log --oneline -5`, write a Conventional Commits subject under 72 characters, commit, verify. Add a body only for a breaking change or a reason the diff cannot show, in at most two short lines. Never list the changes.

- `git status` — never use `-uall`.
- Do NOT add `Co-Authored-By` or any AI-attribution trailer (e.g. "Generated with Claude Code"). Overrides default Claude Code behavior.
