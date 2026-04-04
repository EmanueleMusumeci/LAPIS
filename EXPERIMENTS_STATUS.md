# LAPIS Experiments Status

Current status of experimental evaluation for the ICAPS 2026 Demo Track submission.

---

## Overall Progress

| Category | Status |
|----------|--------|
| LLM+P Baseline (6 domains) | Complete |
| LAPIS/GT (5 domains) | Complete |
| LAPIS/Synthesis (5 domains) | Complete |
| LAPIS/Adequacy (5 domains) | Complete |
| NL2Plan Comparison | In Progress |
| Lexicon Benchmark | Complete |

---

## LLM+P Benchmark Results

### LLM+P Baseline (Few-Shot, GT Domain)

| Domain | Success | Status |
|--------|:-------:|--------|
| Blocksworld | 100% (20/20) | Done |
| Barman | 95% (19/20) | Done |
| Storage | 100% (20/20) | Done |
| Termes | 100% (20/20) | Done |
| Grippers | 100% (20/20) | Done |
| Tyreworld | 95% (19/20) | Done |

### LAPIS/GT (Zero-Shot, GT Domain, Refinement)

| Domain | Success | Status |
|--------|:-------:|--------|
| Blocksworld | 60% (6/10) | Done |
| Grippers | 100% (20/20) | Done |
| Tyreworld | 0% (0/14) | Done |
| Floortile | 45% (9/20) | Done |

### LAPIS/Synthesis (Generated Domain, Refinement)

| Domain | Success | Status |
|--------|:-------:|--------|
| Barman | 50% (1/2) | Partial |
| Storage | 90% (18/20) | Done |
| Termes | 100% (20/20) | Done |
| Tyreworld | 75% (15/20) | Done |
| Floortile | 94% (17/18) | Done |

### LAPIS/Adequacy (Generated Domain, CoT Check, Refinement)

| Domain | Success | Status |
|--------|:-------:|--------|
| Storage | 85% (17/20) | Done |
| Termes | 100% (20/20) | Done |
| Grippers | 100% (20/20) | Done |
| Tyreworld | 65% (13/20) | Done |
| Floortile | 88% (16/18) | Done |

---

## Lexicon Benchmark Results (LAPIS/GT)

| Domain | Success | Problems |
|--------|:-------:|:--------:|
| BabyAI | 100% (10/10) | 10 |
| Blocksworld | 60% (6/10) | 10 |
| Logistics | 40% (12/30) | 30 |
| Sokoban | 56% (17/30) | 30 |

---

## Pending Work

### NL2Plan Comparison

Status: Experiments running. See `tasks/TASK_NL2PLAN_COMPARISON.md` for protocol.

Expected completion: Before deadline if no blockers.

Fallback: If not ready, cite NL2Plan without direct comparison.

### Incomplete Domains

| Domain | Condition | Issues |
|--------|-----------|--------|
| Barman | LAPIS/Synthesis | Only 2/20 problems run |
| Barman | LAPIS/Adequacy | Not started |

These are lower priority given Barman's complexity (cocktail recipes with multiple constraints).

---

## Key Observations

The most notable finding is that LAPIS/Synthesis outperforms LAPIS/GT on structurally complex domains where the ground-truth PDDL uses non-obvious naming conventions or implicit constraints. Floortile shows the clearest example: 94% success with generated domains versus only 45% with ground truth. Tyreworld follows the same pattern: 75% for Synthesis versus 0% for GT.

This suggests that the domain-problem coupling problem is more severe than previously understood. When the LLM generates both files, they share consistent assumptions. When forced to adapt to human-authored domains, the LLM frequently produces problem files that are syntactically valid but semantically incompatible.

Grippers represents a solved domain where all methods achieve perfect or near-perfect scores, establishing a ceiling for comparison.

---

## Data Sources

All numbers sourced from:
- `EXPERIMENTAL_NOTES_FOR_PAPER.md` (primary)
- `TRUE_LLMPP_BASELINE_RESULTS.md` (LLM+P baseline)
- `final_results/` directory (raw manifold.json files)

---

*Last Updated: 2026-04-04*
