#!/usr/bin/env bash
set -euo pipefail

# setup_lexicon_env.sh
# Create a local virtual environment in the repository root, configure
# local cache directories on /DATA to avoid filling the root partition,
# and install pip requirements for the LexiCon submodule.

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$ROOT_DIR/.venv"
REQUIREMENTS="$ROOT_DIR/requirements-lexicon.txt"
CACHE_DIR="$ROOT_DIR/.cache_lexicon"

echo "Preparing LexiCon environment in: $ROOT_DIR"

if [ ! -f "$REQUIREMENTS" ]; then
  echo "ERROR: requirements file not found at $REQUIREMENTS"
  exit 1
fi

echo "Creating cache directory: $CACHE_DIR"
mkdir -p "$CACHE_DIR/wheels" "$CACHE_DIR/pycache" "$CACHE_DIR/tmp"

echo "Adding cache directory to .gitignore (if missing)"
GITIGNORE="$ROOT_DIR/.gitignore"
if ! grep -q "^\.cache_lexicon" "$GITIGNORE" 2>/dev/null; then
  printf "\n# Local cache and venv for lexicon setup\n.cache_lexicon/\n.venv\n" >> "$GITIGNORE"
  echo "Appended .cache_lexicon and .venv to .gitignore"
else
  echo ".cache_lexicon already in .gitignore"
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment: $VENV_DIR"
  python3 -m venv "$VENV_DIR"
else
  echo "Virtual environment already exists: $VENV_DIR"
fi

echo "Activating virtual environment"
# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

echo "Configuring pip and python caches to use $CACHE_DIR"
export PIP_CACHE_DIR="$CACHE_DIR/wheels"
export XDG_CACHE_HOME="$CACHE_DIR"
export TMPDIR="$CACHE_DIR/tmp"
export PYTHONPYCACHEPREFIX="$CACHE_DIR/pycache"

echo "Upgrading pip, setuptools and wheel"
python -m pip install --upgrade pip setuptools wheel

echo "Installing pip requirements from $REQUIREMENTS"
python -m pip install -r "$REQUIREMENTS"

echo "Ensuring third-party submodules are initialized"
git submodule update --init --recursive || true

echo "Creating intermediate_sas directory for SymK (inside lexicon submodule)"
mkdir -p "$ROOT_DIR/third-party/lexicon_neurips/intermediate_sas"

echo "Setup complete. To activate the environment run:"
echo "  source $VENV_DIR/bin/activate"
echo "Caches are placed at: $CACHE_DIR"

exit 0
