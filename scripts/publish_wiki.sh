#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/publish_wiki.sh <owner> <repo>
# Example: ./scripts/publish_wiki.sh Idromerom714 Tutor-Icfes-AI

owner=${1:-}
repo=${2:-}

if [[ -z "$owner" || -z "$repo" ]]; then
  echo "Usage: $0 <owner> <repo>"
  exit 1
fi

wiki_repo="https://github.com/${owner}/${repo}.wiki.git"
workspace_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

if [[ ! -d "${workspace_root}/.wiki" ]]; then
  git clone "$wiki_repo" "${workspace_root}/.wiki"
fi

rsync -av --delete "${workspace_root}/docs/wiki/" "${workspace_root}/.wiki/"

pushd "${workspace_root}/.wiki" >/dev/null
if [[ -n $(git status --porcelain) ]]; then
  git add .
  git commit -m "Sync wiki from docs/wiki"
  git push
else
  echo "No changes to publish."
fi
popd >/dev/null
