#!/usr/bin/env python3
"""Generate skills/ from plugins/*/skills/ as self-contained Agent Skills.

The plugin sources stay untouched so `make sync-upstream` keeps updating them. Each generated skill
carries the shared files it links to, and its frontmatter uses only the fields in the Agent Skills
spec. Usage: build_portable_skills.py [--check]
"""

import argparse
import filecmp
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC_FIELDS = {"name", "description", "license", "compatibility"}
IGNORED = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store", ".pytest_cache")
# Markdown link targets, plus bare ../paths outside links.
LINK = re.compile(r"(?<=\]\()[^)\s#]+|(?<![\w/.-])(?:\.\./)+[\w./-]+")
SKILL_PATH = re.compile(r"plugins/[^/]+/skills/([^/]+)/(.+)")
TOOL_NAME = re.compile(
    r"\b(AskUserQuestion|EnterPlanMode|ExitPlanMode|TodoWrite|SendMessage|TaskCreate|TaskUpdate|TaskList)\b"
)

USER_ONLY_NOTE = (
    "Run this skill only when the user explicitly asks for it by name. Don't start it on your own."
)
TOOL_NOTE = "Tool names here such as `AskUserQuestion` are Claude Code's. See [tool names](references/tool-names.md) for what to use instead."
README = """# Generated skills

`scripts/build_portable_skills.py` generates this folder from `plugins/*/skills/`. Don't edit it by hand. Change the plugin source and run `make portable-skills`.
"""
TOOL_NAMES = """# Tool names

These skills were written for Claude Code. If your agent has no matching tool, use the equivalent below.

| Claude Code | What to do instead |
|---|---|
| `AskUserQuestion` | Use your question tool, or ask one short question in chat |
| `EnterPlanMode`, `ExitPlanMode` | Use your plan mode, or present the plan and wait for approval before editing |
| `TaskCreate`, `TaskUpdate`, `TaskList`, `TodoWrite` | Use your task list tool, or keep a checklist in chat |
| `Task`, `Agent`, `SendMessage` | Use your subagent tool if you have one. Otherwise do the work yourself, one step at a time |
| `Skill` | Load the named skill however your agent loads skills |

A tool name in a skill doesn't make that tool available or change your permission rules.
"""


def split_frontmatter(text):
    match = re.match(r"---\n(.*?)\n---\n?(.*)\Z", text, re.S)
    if not match:
        raise ValueError("SKILL.md has no frontmatter")
    return match.group(1), match.group(2)


def parse_fields(frontmatter):
    """Return (key, value lines) pairs. Indented lines belong to the key above them."""
    fields = []
    for line in frontmatter.split("\n"):
        match = re.match(r"([A-Za-z_-]+):\s*(.*)$", line)
        if match:
            fields.append((match.group(1), [match.group(2)]))
        elif fields:
            fields[-1][1].append(line)
    return fields


def unquote(value):
    value = value.strip()
    return value[1:-1] if len(value) > 1 and value[0] == value[-1] and value[0] in "\"'" else value


def as_scalar(lines):
    items = [re.sub(r"^\s*-\s*", "", line) for line in lines if line.strip()]
    return " ".join(unquote(item) for item in items)


def convert_frontmatter(frontmatter):
    """Keep spec fields, and move every other field into metadata as a string."""
    kept, metadata = [], {}
    for key, lines in parse_fields(frontmatter):
        if key in SPEC_FIELDS:
            is_block = len(lines) > 1 or lines[0][:1] in ('"', "'", ">", "|")
            value = lines[0] if is_block else json.dumps(lines[0], ensure_ascii=False)
            kept.append(f"{key}: {value}")
            kept.extend(lines[1:])
        elif key == "metadata":
            for line in filter(str.strip, lines[1:]):
                name, _, value = line.strip().partition(":")
                metadata[name] = unquote(value)
        else:
            metadata[key] = as_scalar(lines)
    if metadata:
        kept.append("metadata:")
        kept.extend(
            f"  {name}: {json.dumps(value, ensure_ascii=False)}" for name, value in metadata.items()
        )
    return "\n".join(kept)


def plugin_fields(frontmatter):
    return dict((key, as_scalar(lines)) for key, lines in parse_fields(frontmatter))


def rewrite_links(text, source, output, skill_output, skills, shared_dir, needed_shared):
    """Point links at their generated location. Links that resolve to nothing stay as they are."""

    def replace(match):
        target = match.group(0)
        if "://" in target or target.startswith(("/", "@", "mailto:")):
            return target
        resolved = Path(os.path.normpath(source.parent / target))
        try:
            shared_file = resolved.relative_to(shared_dir)
        except ValueError:
            shared_file = None
        if resolved.name == "codex-tools.md":
            destination = skill_output / "references" / "tool-names.md"
        elif shared_file is not None and resolved.is_file():
            needed_shared.add(shared_file)
            destination = skill_output / "references" / "shared" / shared_file
        else:
            in_skill = SKILL_PATH.search(resolved.as_posix())
            if not in_skill or in_skill.group(1) not in skills:
                return target
            destination = skill_output.parent / in_skill.group(1) / in_skill.group(2)
        return os.path.relpath(destination, output.parent).replace(os.sep, "/")

    return re.sub(r"\[(Codex tools|codex-tools\.md)\]", "[tool names]", LINK.sub(replace, text))


def build_skill(source_dir, output_dir, skills):
    plugin_dir = source_dir.parent.parent
    shared_dir = plugin_dir / "shared"
    if not shared_dir.is_dir():
        # Standalone plugins share the development-skills copy of shared/.
        shared_dir = plugin_dir.parent / "development-skills" / "shared"
    shutil.copytree(source_dir, output_dir, ignore=IGNORED)

    needed_shared = set()
    for path in sorted(output_dir.rglob("*.md")):
        source = source_dir / path.relative_to(output_dir)
        text = rewrite_links(
            path.read_text(), source, path, output_dir, skills, shared_dir, needed_shared
        )
        path.write_text(text)

    copied = set()
    while needed_shared - copied:
        name = sorted(needed_shared - copied)[0]
        copied.add(name)
        path = output_dir / "references" / "shared" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        text = (shared_dir / name).read_text()
        path.write_text(
            rewrite_links(
                text, shared_dir / name, path, output_dir, skills, shared_dir, needed_shared
            )
        )

    documents = [path.read_text() for path in output_dir.rglob("*.md")]
    tools_mentioned = any(TOOL_NAME.search(text) for text in documents)
    tool_map_linked = any(
        "references/tool-names.md" in text or "tool-names.md)" in text for text in documents
    )
    if tools_mentioned or tool_map_linked:
        (output_dir / "references").mkdir(exist_ok=True)
        (output_dir / "references" / "tool-names.md").write_text(TOOL_NAMES)

    skill_file = output_dir / "SKILL.md"
    frontmatter, body = split_frontmatter(skill_file.read_text())
    notes = []
    if plugin_fields(frontmatter).get("disable-model-invocation") == "true":
        notes.append(USER_ONLY_NOTE)
    if tools_mentioned:
        notes.append(TOOL_NOTE)
    prefix = "".join(f"{note}\n\n" for note in notes)
    skill_file.write_text(
        f"---\n{convert_frontmatter(frontmatter)}\n---\n\n{prefix}{body.lstrip()}"
    )


def build(output):
    sources = sorted(path.parent for path in ROOT.glob("plugins/*/skills/*/SKILL.md"))
    skills = {path.name for path in sources}
    if len(skills) != len(sources):
        raise ValueError("two plugins define a skill with the same name")
    output.mkdir(parents=True)
    (output / "README.md").write_text(README)
    for source in sources:
        build_skill(source, output / source.name, skills)
    return len(sources)


def differences(left, right):
    def files(base):
        return {path.relative_to(base) for path in base.rglob("*") if path.is_file()}

    left_files, right_files = files(left), files(right)
    changed = {
        name
        for name in left_files & right_files
        if not filecmp.cmp(left / name, right / name, shallow=False)
    }
    return sorted(left_files ^ right_files | changed)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if skills/ is out of date")
    args = parser.parse_args()
    output = ROOT / "skills"
    with tempfile.TemporaryDirectory() as temp:
        fresh = Path(temp) / "skills"
        count = build(fresh)
        if args.check:
            stale = differences(fresh, output) if output.exists() else ["skills/"]
            for name in stale:
                print(f"out of date: {name}")
            if stale:
                sys.exit("skills/ is out of date. Run make portable-skills.")
            print(f"skills/ is up to date ({count} skills)")
            return
        if output.exists():
            shutil.rmtree(output)
        shutil.copytree(fresh, output)
    print(f"generated {count} skills in skills/")


if __name__ == "__main__":
    main()
