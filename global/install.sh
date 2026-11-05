#!/usr/bin/env bash
# Run on each machine after cloning: links the global CLAUDE.md, downloads the skills in
# global/skills.txt from their authors, and makes upstream fetch-only. Rerun to update the skills.
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
upstream_url="https://github.com/reidemeister94/development-skills.git"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

# Moves $1 to $2 so nothing is lost; a symlink holds nothing worth keeping.
move_aside() {
  if [ -L "$1" ]; then
    rm "$1"
  elif [ -e "$1" ]; then
    mkdir -p "$2"
    mv "$1" "$2/$(basename "$1").$(date +%Y%m%d%H%M%S)"
    echo "backup  $1 -> $2"
  fi
}

install_config_dir() {
  # Backups live outside skills/, where a copy would load as a duplicate skill.
  local dir="$1" backup_dir="$1/global-backups" skill target
  mkdir -p "$dir/skills"

  if [ "$dir/CLAUDE.md" -ef "$repo/global/CLAUDE.md" ]; then
    echo "ok      $dir/CLAUDE.md"
  else
    if ! cmp -s "$dir/CLAUDE.md" "$repo/global/CLAUDE.md"; then
      move_aside "$dir/CLAUDE.md" "$backup_dir"
    fi
    ln -sf "$repo/global/CLAUDE.md" "$dir/CLAUDE.md"
    echo "linked  $dir/CLAUDE.md"
  fi

  for skill in "$work"/*; do
    target="$dir/skills/$(basename "$skill")"
    if [ ! -L "$target" ] && diff -r "$target" "$skill" >/dev/null 2>&1; then
      echo "ok      $target"
    else
      move_aside "$target" "$backup_dir"
      cp -R "$skill" "$target"
      echo "fetched $target"
    fi
  done
}

cd "$repo"

# Download everything first, so a failed download changes nothing.
while read -r name url; do
  mkdir -p "$work/$name"
  # Claude can't invoke a skill with this flag, and the global rules need it to.
  curl -fsSL "$url" | sed '/^disable-model-invocation: true$/d' >"$work/$name/SKILL.md"
done <global/skills.txt

install_config_dir "$HOME/.claude"
[ -d "$HOME/.claude-personal" ] && install_config_dir "$HOME/.claude-personal"
[ -n "${CLAUDE_CONFIG_DIR:-}" ] && install_config_dir "$CLAUDE_CONFIG_DIR"

git remote get-url upstream >/dev/null 2>&1 || git remote add upstream "$upstream_url"
# Sync is one-way: pushes to upstream fail, and gh targets this fork instead of the parent repo.
git remote set-url --push upstream DISABLED
git config remote.origin.gh-resolved base
echo "ok      upstream is fetch-only, gh defaults to origin"
