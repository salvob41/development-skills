#!/usr/bin/env bash
# Run once per machine after cloning: links the global CLAUDE.md and skills, and makes upstream fetch-only.
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
upstream_url="https://github.com/reidemeister94/development-skills.git"

# Replaces $2 with a link to $1, moving anything different to $3 so nothing is lost.
link_path() {
  local source_path="$1" target="$2" backup_dir="$3"
  if [ "$target" -ef "$source_path" ]; then
    echo "ok      $target"
    return
  fi
  mkdir -p "$(dirname "$target")"
  if [ -L "$target" ]; then
    rm "$target"
  elif [ -e "$target" ]; then
    if diff -r "$target" "$source_path" >/dev/null 2>&1; then
      rm -rf "$target"
    else
      mkdir -p "$backup_dir"
      mv "$target" "$backup_dir/$(basename "$target").$(date +%Y%m%d%H%M%S)"
      echo "backup  $target -> $backup_dir"
    fi
  fi
  ln -s "$source_path" "$target"
  echo "linked  $target"
}

link_config_dir() {
  # Backups live outside skills/, where a copy would load as a duplicate skill.
  local dir="$1" backup_dir="$1/global-backups" skill
  link_path "$repo/global/CLAUDE.md" "$dir/CLAUDE.md" "$backup_dir"
  for skill in "$repo"/global/skills/*; do
    link_path "$skill" "$dir/skills/$(basename "$skill")" "$backup_dir"
  done
}

cd "$repo"

link_config_dir "$HOME/.claude"
[ -d "$HOME/.claude-personal" ] && link_config_dir "$HOME/.claude-personal"
[ -n "${CLAUDE_CONFIG_DIR:-}" ] && link_config_dir "$CLAUDE_CONFIG_DIR"

git remote get-url upstream >/dev/null 2>&1 || git remote add upstream "$upstream_url"
# Sync is one-way: pushes to upstream fail, and gh targets this fork instead of the parent repo.
git remote set-url --push upstream DISABLED
git config remote.origin.gh-resolved base
echo "ok      upstream is fetch-only, gh defaults to origin"
