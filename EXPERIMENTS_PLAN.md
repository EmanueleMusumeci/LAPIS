# LAPIS Experimental Evaluation Plan

> **Note**: This document describes the original experimental plan from early April 2026. For **current results and completion status**, see:
> - **EXPERIMENTAL_NOTES_FOR_PAPER.md** - Final results (Table 1 with all tracks including LAPIS/Semantic)
> - **EXPERIMENTS_STATUS.md** - Current experiment completion status
> - **MISSING_EXPERIMENTS.md** - Missing experiments breakdown and execution guide
> - **TASK_SEMANTIC_VERIFICATION_BENCHMARK.md** - Semantic verification track (140/140 complete)

This document describes the evaluation strategy for the LAPIS demo system, designed to demonstrate practical capabilities for the ICAPS 2026 Demo Track.

---

## Evaluation Goals

The experiments aim to demonstrate that LAPIS provides a robust end-to-end NL-to-plan pipeline that generalizes across IPC domains without domain-specific tuning. Rather than claiming research novelty, we show that the system handles real planning problems reliably, recovers from synthesis errors through iterative refinement, and scales to non-trivial plan lengths while requiring minimal deployment effort from users who need not write PDDL manually.

---

## Experimental Conditions

We compare four conditions that isolate the contribution of each pipeline component:

| Condition | Domain Source | Refinement | Adequacy Check |
|-----------|---------------|:----------:|:--------------:|
| LLM+P | Ground Truth | No | No |
| LAPIS/GT | Ground Truth | Yes (3 iter) | No |
| LAPIS/Synthesis | LLM-generated | Yes (3 iter) | No |
| LAPIS/Adequacy | LLM-generated | Yes (3 iter) | Yes |

The ablation structure allows readers to isolate each component's contribution by examining the delta between adjacent rows.

---

## Benchmark Domains

### Primary: LLM+P Benchmark (7 domains, 20 problems each)

| Domain | Description | Complexity |
|--------|-------------|------------|
| Blocksworld | Stack/unstack blocks | Low |
| Barman | Cocktail mixing with shakers | High |
| Storage | Warehouse logistics with hoists | Medium |
| Termes | Construction with height constraints | Medium |
| Grippers | Multi-gripper ball transport | Low |
| Tyreworld | Vehicle maintenance operations | High |
| Floortile | Robot painting with directional moves | Medium |

### Secondary: Lexicon Benchmark (supporting evidence)

| Domain | Problems | Purpose |
|--------|:--------:|---------|
| Blocksworld | 10 | Cross-benchmark validation |
| Logistics | 30 | Multi-vehicle routing |
| Sokoban | 30 | Spatial constraint reasoning |
| BabyAI | 10 | Grid navigation |

### Pending: NL2Plan Comparison

If NL2Plan experiments complete before deadline, we will add a direct comparison on the LLM+P benchmark. This evaluates architecture rather than model capability, since both systems use frontier-class LLMs. See `tasks/TASK_NL2PLAN_COMPARISON.md` for protocol.

---

## Configuration

```yaml
model: claude-sonnet-4-6
planner: up_fd (FastDownward via unified-planning)
planner_timeout: 180s
max_refinements: 3
problems_per_domain: 20
```

The 180-second timeout and 3-iteration cap were chosen to balance thoroughness with practical API costs. Future work may include sensitivity analysis on iteration count.

---

## Execution Commands

```bash
# LAPIS/Synthesis condition
python run_llmpp_benchmark.py \
    --domain storage \
    --method lapis \
    --generate_domain \
    --ablation full \
    --model claude-sonnet-4-6

# LAPIS/Adequacy condition
python run_llmpp_benchmark.py \
    --domain storage \
    --method lapis \
    --generate_domain \
    --ablation full_adequacy \
    --model claude-sonnet-4-6

# Batch execution
./run_icaps_experiments.sh           # All domains
./run_icaps_experiments.sh storage   # Single domain
```

---

## Results Collection

Results are stored in two directories:

```
results_icaps2026/           # Raw experiment outputs
final_results/               # Consolidated by condition
```

Count success rates:
```bash
for d in final_results/*/; do
    domain=$(basename "$d")
    total=$(find "$d" -name "manifold.json" | wc -l)
    valid=$(find "$d" -name "manifold.json" -exec grep -l '"val_valid": true' {} \; | wc -l)
    [ "$total" -gt 0 ] && echo "$domain: $valid/$total ($((valid*100/total))%)"
done
```

---

## Key Metrics

For demo track evaluation, we focus on:

1. **Success Rate**: % of problems yielding VAL-valid plans against oracle
2. **Recovery Rate**: % of initially-failed problems recovered via refinement
3. **Plan Length**: Demonstrates handling of non-trivial horizons
4. **API Calls**: Total LLM invocations per successful plan

---

## Data Sources

- All numerical results: `EXPERIMENTAL_NOTES_FOR_PAPER.md` (ground truth)
- LLM+P baseline: `TRUE_LLMPP_BASELINE_RESULTS.md`
- Experiment configurations: `run_icaps_experiments.sh`

---

*Last Updated: 2026-04-04*
