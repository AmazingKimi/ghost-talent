#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "Ghost Talent launcher"
echo "--------------------"

PYTHON_BIN=""
for candidate in python3.13 python3.12 python3.11 python3.10 python3; do
  if command -v "$candidate" >/dev/null 2>&1; then
    if "$candidate" - <<'PY' >/dev/null 2>&1
import sys
raise SystemExit(0 if sys.version_info >= (3, 10) else 1)
PY
    then
      PYTHON_BIN="$candidate"
      break
    fi
  fi
done

if [ -z "$PYTHON_BIN" ]; then
  echo "Python 3.10 or newer is required."
  echo "Install a supported Python version, then run this launcher again."
  read -r -p "Press Enter to close..."
  exit 1
fi

echo "Using: $($PYTHON_BIN --version 2>&1)"

if [ ! -d ".venv" ]; then
  echo "Creating local environment..."
  "$PYTHON_BIN" -m venv .venv
fi

source .venv/bin/activate

python -m pip install --upgrade "pip<26" "setuptools<76" >/dev/null
python -m pip install -e .

echo "Starting Ghost Talent at http://127.0.0.1:8765"
(sleep 2 && open "http://127.0.0.1:8765") &
python -m ghost_talent.app
