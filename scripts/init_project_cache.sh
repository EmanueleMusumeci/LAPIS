#!/usr/bin/env bash
# Source this file from your shell (for example, add the following to your ~/.bashrc):
#   source /full/path/to/CoSTL/scripts/init_project_cache.sh
# Then run in any project directory (after activating the .venv):
#   init_project_cache        # uses ./ .cache_venv by default
#   init_project_cache .cache # or provide an explicit cache dir relative to cwd

# init_project_cache: initialize common Python cache env vars to a directory
# under the current working directory (or a provided relative/absolute path).
init_project_cache() {
  # default cache directory under current working directory
  local cache_dir="${1:-$PWD/.cache_venv}"

  # If a relative path was passed (doesn't start with /), interpret relative to cwd
  if [[ "$cache_dir" != /* ]]; then
    cache_dir="$PWD/$cache_dir"
  fi

  # Create subdirectories used by pip, temporary files and python pycache prefix
  mkdir -p "$cache_dir/pip" "$cache_dir/tmp" "$cache_dir/pycache"

  export PIP_CACHE_DIR="$cache_dir/pip"
  export XDG_CACHE_HOME="$cache_dir"
  export TMPDIR="$cache_dir/tmp"
  export PYTHONPYCACHEPREFIX="$cache_dir/pycache"

  # Helpful reminder if the venv is not active
  if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Warning: no active virtualenv detected (VIRTUAL_ENV is empty)."
    echo "It's recommended to activate the project's .venv first, e.g. 'source .venv/bin/activate'"
  else
    echo "Virtualenv: $VIRTUAL_ENV"
  fi

  echo "Initialized project-local caches:"
  echo "  PIP_CACHE_DIR=$PIP_CACHE_DIR"
  echo "  XDG_CACHE_HOME=$XDG_CACHE_HOME"
  echo "  TMPDIR=$TMPDIR"
  echo "  PYTHONPYCACHEPREFIX=$PYTHONPYCACHEPREFIX"
}

# Convenience alias: after sourcing this file you can run `use_local_cache`
use_local_cache() {
  init_project_cache "$1"
}

# If this script is executed (not sourced), run a quick demonstration for cwd
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  echo "This script is meant to be sourced, not executed. Running a demo with default settings..."
  init_project_cache
  echo "Run 'echo \$PIP_CACHE_DIR' to inspect the variable in your shell." 
fi
