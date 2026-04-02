# EXPERIMENTS_PLAN.md — LAPIS ICAPS 2026 Demo Track

This document describes the plan to reproduce missing experiments for the official paper submission.

## Official Paper Tables (from `LAPIS__Language_Adaptive_PDDL_Iterative_Synthesis.zip`)

### Table 1: VAL success rate (%) on 20 problems per domain

| Domain | LLM+P | LAPIS/GT | LAPIS/full | LAPIS/full+adequacy |
|--------|-------|----------|------------|---------------------|
| blocksworld | 75 | 100 | 85 | 100 |
| barman | 0 | 100 | 5 | 5 |
| storage | 85 | 100 | **---** | **---** |
| termes | 20 | 100 | **---** | **---** |

**Missing experiments (marked ---):**
- storage: LAPIS/full, LAPIS/full+adequacy
- termes: LAPIS/full, LAPIS/full+adequacy

### Table 2: Direct LLM baselines vs LAPIS (Lexicon benchmark)

| Model | BlocksWorld | Logistics | Sokoban |
|-------|-------------|-----------|---------|
| o3 | 83 | 40 | 60 |
| Gemini 2.5 | 83 | 43 | 56 |
| DeepSeek R1 | 73 | 37 | 30 |
| Claude 3.7 | 10 | 3 | 10 |
| **LAPIS (GPT-4o)** | 60 | 40 | 57 |

**Status:** Complete (no action needed)

---

## Experiment Conditions

| Condition | Description | `--generate_domain` | `--ablation` | Refinements |
|-----------|-------------|---------------------|--------------|-------------|
| **LLM+P** | GT domain, single-shot, 0 refinements | No | — | 0 |
| **LAPIS/GT** | GT domain, schema injection, 3 refinements | No | — | 3 |
| **LAPIS/full** | Domain generated from NL, clean prompt + schema | Yes | `full` | 3 |
| **LAPIS/full+adequacy** | Domain generated + CoT adequacy checks | Yes | `full_adequacy` | 3 |

---

## Missing Experiments to Run

### Priority 1: Fill Table 1 Gaps

| Domain | LAPIS/full | LAPIS/full+adequacy |
|--------|------------|---------------------|
| storage | **TODO** | **TODO** |
| termes | **TODO** | **TODO** |

### Priority 2: Verify Existing Results (Optional)

Re-run blocksworld and barman with full 20 problems if targeted mini-runs were incomplete.

---

## Configuration Requirements

### Planner Timeout
- **Maximum 180 seconds** per problem for the symbolic planner
- **Up to 3 refinement iterations** per problem

### Results Directory
All experiment results will be consolidated in:
```
results_icaps2026/
├── storage_full/
├── storage_full_adequacy/
├── termes_full/
└── termes_full_adequacy/
```

---

## Automatic Experiment Script

Create `run_icaps_experiments.sh`:

```bash
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

# Domains to run (from official paper Table 1 gaps)
DOMAINS_FULL=("storage" "termes")
DOMAINS_ADEQUACY=("storage" "termes")

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
    local ablation="$2"
    local suffix="$3"

    log "═══════════════════════════════════════════════════════════════════"
    log "Domain: $domain | Ablation: $ablation"
    log "═══════════════════════════════════════════════════════════════════"

    local exp_name="benchmark_${domain}_${suffix}"
    local out_dir="${RESULTS_DIR}/${domain}_${suffix}"

    run_cmd "$PYTHON" run_llmpp_benchmark.py \
        --domain "$domain" \
        --method costl \
        --generate_domain \
        --ablation "$ablation" \
        --model "$MODEL" \
        --results_dir "$RESULTS_DIR" \
        --planner_timeout "$PLANNER_TIMEOUT"

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

# ─── LAPIS/full (Condition C) ────────────────────────────────────────────────
log "Phase 1: LAPIS/full (domain generation, no adequacy)"
domains_full=("${DOMAINS_FULL[@]}")
filter_domains domains_full

for domain in "${domains_full[@]}"; do
    run_experiment "$domain" "full" "full"
done

# ─── LAPIS/full+adequacy (Condition D) ───────────────────────────────────────
log "Phase 2: LAPIS/full+adequacy (domain generation + CoT adequacy)"
domains_adequacy=("${DOMAINS_ADEQUACY[@]}")
filter_domains domains_adequacy

for domain in "${domains_adequacy[@]}"; do
    run_experiment "$domain" "full_adequacy" "full_adequacy"
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
```

---

## Code Changes Required

### 1. Add Planner Timeout Support

**File:** `src/costl/planner/low/planner_utils.py`

The `plan_with_output()` function already has a `timeout` parameter. Ensure it's properly propagated:

```python
def plan_with_output(domain_path, problem_dir, plan_path,
                     planner_name="pyperplan", timeout=180):
    """
    Run planner with timeout (default 180s for ICAPS experiments).
    """
    # ... existing code ...
```

### 2. Add Timeout to Benchmark Runner

**File:** `run_llmpp_benchmark.py`

Add `--planner_timeout` argument:

```python
parser.add_argument("--planner_timeout", type=int, default=180,
                    help="Timeout for symbolic planner in seconds (default: 180)")
```

Pass to pipeline:
```python
pipeline = LexiconLowLevelPipeline(
    # ... existing args ...
    planner_timeout=args.planner_timeout,
)
```

### 3. Update Pipeline to Accept Timeout

**File:** `src/costl/pipelines/lexicon_low_level.py`

Add `planner_timeout` parameter to `__init__` and pass to `plan_with_output()` calls.

---

## Execution Plan

### Step 1: Verify Environment
```bash
source key.sh
echo $ANTHROPIC_API_KEY  # Should be set
python3 -c "import anthropic; print('OK')"
```

### Step 2: Dry Run
```bash
chmod +x run_icaps_experiments.sh
./run_icaps_experiments.sh --dry-run
```

### Step 3: Run Missing Experiments
```bash
# Run all missing experiments
./run_icaps_experiments.sh

# Or run specific domain
./run_icaps_experiments.sh storage
./run_icaps_experiments.sh termes
```

### Step 4: Collect Results

After experiments complete, update the paper's Table 1:

```bash
# Check results
ls -la results_icaps2026/

# Count valid plans
for d in results_icaps2026/*/; do
    domain=$(basename "$d")
    total=$(find "$d" -name "manifold.json" | wc -l)
    valid=$(find "$d" -name "manifold.json" -exec grep -l '"val_valid": true' {} \; | wc -l)
    pct=$((valid * 100 / total))
    echo "$domain: $valid/$total ($pct%)"
done
```

---

## Expected Costs

| Experiment | Problems | Est. Tokens | Est. Cost |
|------------|----------|-------------|-----------|
| storage LAPIS/full | 20 | ~200k | ~$0.60 |
| storage LAPIS/full+adequacy | 20 | ~350k | ~$1.05 |
| termes LAPIS/full | 20 | ~200k | ~$0.60 |
| termes LAPIS/full+adequacy | 20 | ~350k | ~$1.05 |
| **Total** | **80** | **~1.1M** | **~$3.30** |

---

## Verification Checklist

- [ ] Planner timeout set to 180s
- [ ] Max refinements set to 3
- [ ] Results consolidated in `results_icaps2026/`
- [ ] All 4 missing cells in Table 1 filled
- [ ] Summary JSON generated for each run
- [ ] Paper updated with new results
