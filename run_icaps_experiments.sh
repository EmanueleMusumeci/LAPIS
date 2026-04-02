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

# Domains to run (Targeting missing evaluation blocks from Table 1)
DOMAINS_FULL=("grippers" "tyreworld" "floortile")
DOMAINS_ADEQUACY=("grippers" "tyreworld" "floortile")
DOMAINS_BASELINE_GEN=("blocksworld" "barman" "grippers" "tyreworld" "floortile")
DOMAINS_GT=("grippers" "tyreworld" "floortile")

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

run_experiment() {
    local domain="$1"
    local method="$2"
    local ablation="$3"

    log "═══════════════════════════════════════════════════════════════════"
    log "Domain: $domain | Method: $method | Ablation: $ablation"
    log "═══════════════════════════════════════════════════════════════════"

    local exp_name="benchmark_${domain}_${ablation}"
    local out_dir="${RESULTS_DIR}/${domain}_${ablation}"

    run_cmd "$PYTHON" run_llmpp_benchmark.py \
        --domain "$domain" \
        --method "$method" \
        --generate_domain \
        --ablation "$ablation" \
        --model "$MODEL" \
        --results_dir "$RESULTS_DIR" \
        --planner_timeout "$PLANNER_TIMEOUT" \
        --data_dir "$DATA_DIR"

    log "Results saved to: $RESULTS_DIR"
}

run_experiment_gt() {
    local domain=$1
    local method=$2
    local ablation=$3

    log "═══════════════════════════════════════════════════════════════════"
    log "Domain: $domain | Ablation: $ablation (GT DOMAIN - NO GEN)"
    log "═══════════════════════════════════════════════════════════════════"

    run_cmd "$PYTHON" run_llmpp_benchmark.py \
        --domain "$domain" \
        --method "$method" \
        --ablation "$ablation" \
        --model "$MODEL" \
        --results_dir "$RESULTS_DIR" \
        --planner_timeout "$PLANNER_TIMEOUT" \
        --data_dir "$DATA_DIR"

    log "Results saved to: $RESULTS_DIR"
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
    run_experiment_gt "$domain" "costl" "full"
done

# ─── LAPIS/full (Condition C) ────────────────────────────────────────────────
log "Phase 1: LAPIS/full (domain generation, no adequacy)"
domains_full=("${DOMAINS_FULL[@]}")
filter_domains domains_full

for domain in "${domains_full[@]}"; do
    run_experiment "$domain" "costl" "full"
done

# ─── LAPIS/full+adequacy (Condition D) ───────────────────────────────────────
log "Phase 2: LAPIS/full+adequacy (domain generation + CoT adequacy)"
domains_adequacy=("${DOMAINS_ADEQUACY[@]}")
filter_domains domains_adequacy

for domain in "${domains_adequacy[@]}"; do
    run_experiment "$domain" "costl" "full_adequacy"
done

# ─── LLMPP-GEN Baseline (Condition B' - Fair Baseline) ───────────────────────
log "Phase 3: LLM+P with generated domain (single-shot, No refinement)"
domains_baseline_gen=("storage" "termes")
filter_domains domains_baseline_gen

for domain in "${domains_baseline_gen[@]}"; do
    # We use method=llmpp (single-shot) but generate_domain=True
    # This demonstrates the need for LAPIS refinement loops.
    run_experiment "$domain" "llmpp" "full" 
done

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
