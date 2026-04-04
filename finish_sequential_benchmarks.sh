#!/bin/bash
# finish_benchmarks.sh — Sequentially fill Table 1 gaps for Tyreworld and Floortile
set -euo pipefail

PYTHON="/home/xps/miniconda3/bin/python3"
MODEL="claude-sonnet-4-6"

if [[ -f "key.sh" ]]; then source key.sh; fi

# Helper to find missing problems
get_missing() {
    local domain="$1"
    local method="$2"
    local ablation="$3"
    local state_pattern="*/benchmark_llmpp_${domain}_${method}_domgen_*${ablation}_*/p*/manifold.json"
    
    local successful=$(find results_icaps2026 results_llmpp -path "$state_pattern" -exec grep -l '"val_valid": true' {} + 2>/dev/null || true)
    local missing=()
    for i in {01..20}; do
        local p="p$i"
        if [[ ! "$successful" =~ "/${p}/manifold.json" ]]; then
            missing+=("$p")
        fi
    done
    echo "${missing[*]}"
}

run_sequential() {
    local domain=$1
    local method=$2
    local ablation=$3
    
    local problems=$(get_missing "$domain" "$method" "$ablation")
    if [[ -z "$problems" ]]; then
        echo "--- All problems for $domain/$method/$ablation already completed. Skipping. ---"
        return
    fi

    echo "--- Resuming $domain | $method | $ablation (Problems: $problems) ---"
    
    $PYTHON run_llmpp_benchmark.py \
        --domain "$domain" \
        --method "$method" \
        --ablation "$ablation" \
        --generate_domain \
        --model "$MODEL" \
        --results_dir results_icaps2026 \
        --data_dir data/llmpp \
        --problems $problems
}

# 1. Floortile Adequacy (Condition D)
run_sequential "floortile" "lapis" "full_adequacy"

# 2. Tyreworld Adequacy (Condition D)
run_sequential "tyreworld" "lapis" "full_adequacy"

# 3. Tyreworld Synthesis (Condition C)
run_sequential "tyreworld" "lapis" "full"

# 4. Tyreworld Ablation (Condition B')
run_sequential "tyreworld" "llmpp" "full"

echo "Sequential completion complete!"
