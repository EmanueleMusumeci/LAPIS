#!/bin/bash
# overnight_tyreworld.sh — Complete all Tyreworld conditions (B', C, D)
set -euo pipefail

PYTHON="/home/xps/miniconda3/bin/python3"
MODEL="claude-sonnet-4-6"
if [[ -f "key.sh" ]]; then source key.sh; fi

run_benchmark() {
    local method=$1
    local ablation=$2
    local refinements=$3
    echo "--- Tyreworld | $method | $ablation ($refinements) ---"
    $PYTHON run_llmpp_benchmark.py \
        --domain tyreworld \
        --method "$method" \
        --ablation "$ablation" \
        --generate_domain \
        --model "$MODEL" \
        --results_dir results_icaps2026 \
        --data_dir data/llmpp \
        --pddl_gen_iterations "$refinements"
}

# 1. Condition B' (Synthesis, 0 Iterations) - Reruns/Finishes
run_benchmark "llmpp" "full" 0

# 2. Condition C (Synthesis, 3 Iterations) - FIXES 0% (Crash recovery)
run_benchmark "lapis" "full" 3

# 3. Condition D (Adequacy Check) - FIXES 0% (Crash recovery)
run_benchmark "lapis" "full_adequacy" 3

echo "Tyreworld overnight track complete!"
