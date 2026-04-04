#!/bin/bash
# run_urgent_parallels.sh — Parallelize Tyreworld and Storage ICAPS benchmarks

set -euo pipefail

# ─── Configuration ───────────────────────────────────────────────────────────
PYTHON="/home/xps/miniconda3/bin/python3"
MODEL="claude-sonnet-4-6"
RESULTS_DIR="results_icaps2026"
PLANNER_TIMEOUT=180
DATA_DIR="data/llmpp"

if [[ -f "key.sh" ]]; then
    source key.sh
fi

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

get_missing_problems() {
    local domain="$1"
    local method="$2"
    local ablation="$3"
    local generate_domain="${4:-true}"
    
    local gen_suffix=""
    if [ "$generate_domain" = "true" ]; then gen_suffix="_domgen"; fi
    
    # Pre-calculate successful problem IDs for this specific condition
    local success_pattern="*/benchmark_llmpp_${domain}_${method}${gen_suffix}_*${ablation}_*/p*/manifold.json"
    local successful_paths=$(find results results_llmpp results_icaps2026 -path "$success_pattern" -exec grep -l '"val_valid": true' {} + 2>/dev/null || true)
    
    local missing=()
    for i in {01..20}; do
        local p="p$i"
        if [[ ! "$successful_paths" =~ "/${p}/manifold.json" ]]; then
            missing+=("$p")
        fi
    done
    echo "${missing[*]}"
}

run_experiment_bg() {
    local domain="$1"
    local method="$2"
    local ablation="$3"
    local log_file="${RESULTS_DIR}/parallel_${domain}_${method}_${ablation}.log"
    
    local problems=$(get_missing_problems "$domain" "$method" "$ablation" "true")
    if [[ -z "$problems" ]]; then
        log "All problems for $domain/$method/$ablation already completed. Skipping."
        return
    fi
    
    log "Launching $domain $method $ablation in background... (Log: $log_file)"
    "$PYTHON" run_llmpp_benchmark.py \
        --domain "$domain" \
        --method "$method" \
        --generate_domain \
        --ablation "$ablation" \
        --model "$MODEL" \
        --results_dir "$RESULTS_DIR" \
        --planner_timeout "$PLANNER_TIMEOUT" \
        --data_dir "$DATA_DIR" \
        --problems $problems > "$log_file" 2>&1 &
}

# ─── Parallel Execution ───

log "Starting Parallel Resumption for Tyreworld and Storage..."

# Tyreworld Parallel Tracks
run_experiment_bg "tyreworld" "lapis" "full"           # Synthesis (Condition C)
run_experiment_bg "tyreworld" "lapis" "full_adequacy"  # Adequacy (Condition D)
run_experiment_bg "tyreworld" "llmpp" "full"           # Baseline (Condition B')

# Storage Parallel Tracks
run_experiment_bg "storage" "lapis" "full_adequacy"    # Adequacy (Condition D)
run_experiment_bg "storage" "llmpp" "full"             # Baseline (Condition B')

log "All sub-tasks launched. Monitoring progress..."
log "Waiting for all parallel jobs to finish..."
wait
log "Urgent benchmarks complete!"
