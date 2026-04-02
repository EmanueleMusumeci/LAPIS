#!/bin/bash
# run_original_llmpp_experiments.sh — Run true Condition B (LLM+P Original)
#
# Usage:
#   ./run_original_llmpp_experiments.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-python3}"
DOMAINS=("blocksworld" "barman" "storage" "termes" "grippers" "tyreworld")

cd "$SCRIPT_DIR"

if [[ -f "key.sh" ]]; then
    source key.sh
fi

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

log "Running Original LLM+P on domains: ${DOMAINS[*]}"

for domain in "${DOMAINS[@]}"; do
    log "═══════════════════════════════════════════════════════════════════"
    log "Domain: $domain | Method: llm_ic_pddl_planner (True LLM+P + Context)"
    log "═══════════════════════════════════════════════════════════════════"

    # For original LLM+P, it expects 20 tasks, indexed 0-19. 
    # (Assuming glob expansion in third-party/llm-pddl reads them as 0 to 19 matching `pxx.nl`)

    cd "third-party/llm-pddl"

    for task_id in {0..19}; do
        log "Running task $task_id for $domain"
        
        # We catch failures gracefully so the script continues
        $PYTHON main.py --domain "$domain" --method "llm_ic_pddl_planner" --task "$task_id" || true

    done
    
    cd "$SCRIPT_DIR"
done

log "═══════════════════════════════════════════════════════════════════"
log "All original LLM+P tasks complete!"
log "Metrics have been saved in 'third-party/llm-pddl/experiments' containing _manifold.json"
log "═══════════════════════════════════════════════════════════════════"
