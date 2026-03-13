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
wiki_src_dir="${workspace_root}/docs/wiki"

if [[ ! -d "$wiki_src_dir" ]]; then
  echo "No se encontró el directorio de wiki fuente: ${wiki_src_dir}"
  exit 1
fi

# Evita publicar documentación desactualizada con rutas ya eliminadas.
if grep -R -n -E 'pages/registro\.py|/pages/registro\.py' "$wiki_src_dir" >/dev/null 2>&1; then
  echo "Se detectaron referencias obsoletas a pages/registro.py en docs/wiki."
  echo "Actualiza la documentación antes de publicar la wiki."
  echo
  grep -R -n -E 'pages/registro\.py|/pages/registro\.py' "$wiki_src_dir" || true
  exit 1
fi

if ! git ls-remote "$wiki_repo" >/dev/null 2>&1; then
  echo "No se pudo acceder a: ${wiki_repo}"
  echo "Posibles causas:"
  echo "  1) La Wiki no está creada aún (abre la pestaña Wiki en GitHub y crea la primera página)."
  echo "  2) Falta autenticación/permisos para el repositorio."
  echo "  3) Owner/repo incorrectos."
  exit 1
fi

tmp_dir=$(mktemp -d)
trap 'rm -rf "$tmp_dir"' EXIT

git clone "$wiki_repo" "$tmp_dir/wiki"
rsync -av --delete --exclude='.git' "${wiki_src_dir}/" "$tmp_dir/wiki/"

if [[ -n $(git -C "$tmp_dir/wiki" status --porcelain) ]]; then
  git -C "$tmp_dir/wiki" add .
  git -C "$tmp_dir/wiki" commit -m "Sync wiki from docs/wiki"
  git -C "$tmp_dir/wiki" push
else
  echo "No changes to publish."
fi
