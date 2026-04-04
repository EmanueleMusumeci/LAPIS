#!/bin/bash
# run_icaps_experiments.sh — Reproduce missing ICAPS 2026 experiments
#
# Usage:
#   ./run_icaps_experiments.sh           # Run all missing experiments
#   ./run_icaps_experiments.sh storage   # Run only storage domain
#   ./run_icaps_experiments.sh --dry-run # Show commands without executing

set -euo pipefail

# ─── Configuration ───────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-/home/xps/miniconda3/bin/python3}"
MODEL="${MODEL:-claude-sonnet-4-6}"
RESULTS_DIR="${RESULTS_DIR:-results_icaps2026}"
PLANNER_TIMEOUT=180
MAX_REFINEMENTS=3
DATA_DIR="data/llmpp"

# Domains to run (Targeting only the TRUE gaps in the paper table)
DOMAINS_FULL=("tyreworld")
DOMAINS_ADEQUACY=("storage" "grippers" "tyreworld")
DOMAINS_BASELINE_GEN=("storage" "termes" "barman" "tyreworld")
DOMAINS_GT=()

# ─── Parse arguments ─────────────────────────────────────────────────────────
DRY_RUN=false
SPECIFIC_DOMAIN=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            SPECIFIC_DOMAIN="$1"
            shift
            ;;
    esac
done

# ─── Helpers ─────────────────────────────────────────────────────────────────
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

run_cmd() {
    if $DRY_RUN; then
        echo "[DRY-RUN] $*"
    else
        log "Running: $*"
        "$@"
    fi
}

# ─── Setup ───────────────────────────────────────────────────────────────────
cd "$SCRIPT_DIR"

if [[ -f "key.sh" ]]; then
    source key.sh
fi

mkdir -p "$RESULTS_DIR"

# ─── Run Experiments ─────────────────────────────────────────────────────────

get_missing_problems() {
    local domain="$1"
    local method="$2"
    local ablation="$3"
    local generate_domain="${4:-true}"
    
    local gen_suffix=""
    if [ "$generate_domain" = "true" ]; then gen_suffix="_domgen"; fi
    
    # Pre-calculate successful problem IDs for this specific condition
    # Search for all matching result folders and their successful manifold.json files
    local success_pattern="*/benchmark_llmpp_${domain}_${method}${gen_suffix}_*${ablation}_*/p*/manifold.json"
    local successful_paths=$(find results results_llmpp results_icaps2026 -path "$success_pattern" -exec grep -l '"val_valid": true' {} + 2>/dev/null || true)
    
    local missing=()
    for i in {01..20}; do
        local p="p$i"
        # Check if this problem is in the successful_paths
        if [[ ! "$successful_paths" =~ "/${p}/manifold.json" ]]; then
            missing+=("$p")
        fi
    done
    echo "${missing[*]}"
}

run_experiment() {
    local domain="$1"
    local method="$2"
    local ablation="$3"
    
    log "═══════════════════════════════════════════════════════════════════"
    log "Domain: $domain | Method: $method | Ablation: $ablation"
    log "═══════════════════════════════════════════════════════════════════"

    local problems=$(get_missing_problems "$domain" "$method" "$ablation" "true")
    if [[ -z "$problems" ]]; then
        log "All problems for $domain/$ablation already completed. Skipping."
        return
    fi
    
    log "Targeting problems: $problems"

    run_cmd "$PYTHON" run_llmpp_benchmark.py \
        --domain "$domain" \
        --method "$method" \
        --generate_domain \
        --ablation "$ablation" \
        --model "$MODEL" \
        --results_dir "$RESULTS_DIR" \
        --planner_timeout "$PLANNER_TIMEOUT" \
        --data_dir "$DATA_DIR" \
        --problems $problems

    log "Batch complete for $domain"
}

run_experiment_gt() {
    local domain=$1
    local method=$2
    local ablation=$3

    log "═══════════════════════════════════════════════════════════════════"
    log "Domain: $domain | Ablation: $ablation (GT DOMAIN - NO GEN)"
    log "═══════════════════════════════════════════════════════════════════"

    local problems=$(get_missing_problems "$domain" "$method" "$ablation" "false")
    if [[ -z "$problems" ]]; then
        log "All GT problems for $domain/$ablation already completed. Skipping."
        return
    fi

    run_cmd "$PYTHON" run_llmpp_benchmark.py \
        --domain "$domain" \
        --method "$method" \
        --ablation "$ablation" \
        --model "$MODEL" \
        --results_dir "$RESULTS_DIR" \
        --planner_timeout "$PLANNER_TIMEOUT" \
        --data_dir "$DATA_DIR" \
        --problems $problems

    log "Batch complete for $domain (GT)"
}

# Filter domains if specific one requested
filter_domains() {
    local -n arr=$1
    if [[ -n "$SPECIFIC_DOMAIN" ]]; then
        if [[ " ${arr[*]} " =~ " ${SPECIFIC_DOMAIN} " ]]; then
            arr=("$SPECIFIC_DOMAIN")
        else
            arr=()
        fi
    fi
}

# ─── Ground Truth Baselines (Condition A & B) ────────────────────────────────
log "Phase 0: Ground Truth baselines for missing domains"
domains_gt=("${DOMAINS_GT[@]}")
filter_domains domains_gt

for domain in "${domains_gt[@]}"; do
    run_experiment_gt "$domain" "llmpp" "full"
    run_experiment_gt "$domain" "lapis" "full"
done

# ─── LAPIS/full (Condition C) ────────────────────────────────────────────────
log "Phase 1: LAPIS/full (domain generation, no adequacy)"
domains_full=("${DOMAINS_FULL[@]}")
filter_domains domains_full

for domain in "${domains_full[@]}"; do
    run_experiment "$domain" "lapis" "full"
done

# ─── LAPIS/full+adequacy (Condition D) & LLMPP-GEN (Condition B') ─────────────
log "Parallel Phase: LAPIS Adequacy (Cond D) vs LLM+P Synthesis Baseline (Cond B')"
log "Outputs redirected to ph2_adequacy.log and ph3_baseline_gen.log"

# Concurrently run Phase 2 and Phase 3
(
    domains_adequacy=("${DOMAINS_ADEQUACY[@]}")
    filter_domains domains_adequacy
    for domain in "${domains_adequacy[@]}"; do
        run_experiment "$domain" "lapis" "full_adequacy"
    done
) > "${RESULTS_DIR}/ph2_adequacy.log" 2>&1 &

(
    domains_baseline_gen=("${DOMAINS_BASELINE_GEN[@]}")
    filter_domains domains_baseline_gen
    for domain in "${domains_baseline_gen[@]}"; do
        run_experiment "$domain" "llmpp" "full" 
    done
) > "${RESULTS_DIR}/ph3_baseline_gen.log" 2>&1 &

# Wait for parallel tasks
log "Waiting for background threads to complete..."
wait

# ─── Final Deferred Phase: Floortile ────────────────────────────────────────
log "Phase 4: Deferred Floortile Experiments (All Conditions)"
run_experiment_gt "floortile" "llmpp" "full"
run_experiment_gt "floortile" "lapis" "full"
run_experiment "floortile" "lapis" "full"
run_experiment "floortile" "lapis" "full_adequacy"
run_experiment "floortile" "llmpp" "full"

# ─── Summary ─────────────────────────────────────────────────────────────────
log "═══════════════════════════════════════════════════════════════════"
log "Experiments complete!"
log "Results directory: $RESULTS_DIR"
log "═══════════════════════════════════════════════════════════════════"

# Generate summary
if ! $DRY_RUN; then
    log "Generating summary..."

    echo ""
    echo "=== RESULTS SUMMARY ==="
    echo ""

    for dir in "$RESULTS_DIR"/*/; do
        if [[ -d "$dir" ]]; then
            domain=$(basename "$dir")
            manifests=$(find "$dir" -name "manifold.json" 2>/dev/null | wc -l)
            valid=$(find "$dir" -name "manifold.json" -exec grep -l '"val_valid": true' {} \; 2>/dev/null | wc -l)
            echo "$domain: $valid/$manifests valid"
        fi
    done
fi
