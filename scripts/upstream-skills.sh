#!/usr/bin/env bash
# One-way sync of skills from upstream into the plugins/ layout. The histories are unrelated and
# the layouts differ, so `git merge upstream/main` is not usable. Review the result with git diff.
#
# scripts/upstream-base records the upstream commit of the last sync, which separates local edits
# from upstream ones: a skill is only replaced if it has no local edits since that commit.
# Skills listed in scripts/upstream-skip are never touched.
set -euo pipefail

cd "$(dirname "$0")/.."
plugin=plugins/development-skills
ref=upstream/main
base_file=scripts/upstream-base
skip_file=scripts/upstream-skip

git fetch -q upstream
base="$(cat "$base_file")"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

find_skill() {
  compgen -G "plugins/*/skills/$1" | head -1 || true
}

is_skipped() {
  grep -qE "^$1([[:space:]]|$)" "$skip_file"
}

# True if $2 in the working tree matches skills/<name> ($3) at commit $1.
same_as_commit() {
  rm -rf "${work:?}/tree"
  mkdir "$work/tree"
  git archive "$1" "skills/$3" 2>/dev/null | tar -x -C "$work/tree" 2>/dev/null || return 1
  diff -r "$work/tree/skills/$3" "$2" >/dev/null 2>&1
}

sync_skill() {
  local skill="$1" local_path
  is_skipped "$skill" && return
  local_path="$(find_skill "$skill")"

  if [ -z "$local_path" ]; then
    git archive "$ref" "skills/$skill" | tar -x -C "$plugin"
    echo "added   $skill"
  elif [ "$(git rev-parse "$ref:skills/$skill")" = "$(git rev-parse -q --verify "$base:skills/$skill" || true)" ]; then
    : # unchanged upstream since the last sync
  elif same_as_commit "$ref" "$local_path" "$skill"; then
    : # already identical
  elif same_as_commit "$base" "$local_path" "$skill"; then
    rm -rf "$local_path"
    git archive "$ref" "skills/$skill" | tar -x -C "${local_path%/skills/*}"
    echo "updated $skill"
  else
    echo "kept    $skill (edited here and upstream: merge by hand or add it to $skip_file)"
  fi
}

# Upstream skills link to ../../shared/, which lands in the same place relative to the plugin.
sync_shared_file() {
  local file="$1" local_path="$plugin/$1"
  if [ ! -e "$local_path" ]; then
    git archive "$ref" "$file" | tar -x -C "$plugin"
    echo "added   $file"
  elif [ "$(git hash-object "$local_path")" = "$(git rev-parse -q --verify "$base:$file" || true)" ] &&
    [ "$(git hash-object "$local_path")" != "$(git rev-parse "$ref:$file")" ]; then
    git archive "$ref" "$file" | tar -x -C "$plugin"
    echo "updated $file"
  fi
}

for path in $(git ls-tree -d --name-only "$ref" skills/); do
  sync_skill "${path#skills/}"
done
for file in $(git ls-tree -r --name-only "$ref" shared/); do
  sync_shared_file "$file"
done

git rev-parse "$ref" >"$base_file"
echo "synced to $(git rev-parse --short "$ref"). Review with git diff, then bump the plugin version."
