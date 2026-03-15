#!/usr/bin/env bash
set -euo pipefail

EXPECTED_LINE="google.com, pub-5888906096884160, DIRECT, f08c47fec0942fa0"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[1/3] Validando archivos locales ads.txt"
for f in "$ROOT_DIR/ads.txt" "$ROOT_DIR/static/ads.txt"; do
  if [[ ! -f "$f" ]]; then
    echo "ERROR: No existe $f"
    exit 1
  fi
  if ! grep -Fq "$EXPECTED_LINE" "$f"; then
    echo "ERROR: El archivo $f no contiene la linea esperada de AdSense"
    exit 1
  fi
done
echo "OK: Archivos locales ads.txt correctos"

if [[ $# -lt 1 ]]; then
  echo "[2/3] Validacion remota omitida (sin dominio)"
  echo "Uso: $0 <dominio-o-url-base>"
  echo "Ejemplo: $0 https://tudominio.com"
  echo "[3/3] Verificacion final: pendiente de dominio"
  exit 0
fi

BASE="$1"
if [[ "$BASE" != http://* && "$BASE" != https://* ]]; then
  BASE="https://$BASE"
fi
BASE="${BASE%/}"

echo "[2/3] Consultando endpoint publico /ads.txt en $BASE"
HEADERS="$(curl -sSI "$BASE/ads.txt" || true)"
if echo "$HEADERS" | grep -qi 'location: https://share.streamlit.io/-/auth/app'; then
  echo "ERROR: $BASE/ads.txt redirige al login de Streamlit (app privada)."
  echo "Accion: cambia la app a publica en Streamlit Community Cloud y vuelve a verificar."
  exit 1
fi

BODY="$(curl -fsSL "$BASE/ads.txt")"
if [[ "$BODY" != *"$EXPECTED_LINE"* ]]; then
  echo "ERROR: $BASE/ads.txt no devuelve la linea esperada"
  exit 1
fi
echo "OK: $BASE/ads.txt expone la linea esperada"

echo "[3/3] Validacion complementaria /static/ads.txt"
if curl -fsSL "$BASE/static/ads.txt" | grep -Fq "$EXPECTED_LINE"; then
  echo "OK: $BASE/static/ads.txt tambien responde correctamente"
else
  echo "AVISO: $BASE/static/ads.txt no disponible; no es bloqueante si /ads.txt funciona"
fi

echo "Verificacion de AdSense completada correctamente."