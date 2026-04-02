# ICAPS 2026 Experiments Status

This document tracks the status of the experiments required for the ICAPS 2026 paper submission, separating the LAPIS framework results from the true LLM+P baseline.

## 1. LAPIS Framework Execution
The standard LAPIS conditions successfully executed utilizing the `run_icaps_experiments.sh` script, which correctly mapped to the `costl` refinement method.

| Condition | Domain | Status | Notes |
| :--- | :--- | :--- | :--- |
| LAPIS/full | blocksworld | ✅ Done | From previous runs |
| LAPIS/full | barman | ✅ Done | From previous runs |
| LAPIS/full | storage | ✅ Done | Run via `run_icaps_experiments.sh` Phase 1 |
| LAPIS/full | termes | ✅ Done | Run via `run_icaps_experiments.sh` Phase 1 |
| LAPIS/full+adequacy | blocksworld | ✅ Done | From previous runs |
| LAPIS/full+adequacy | barman | ✅ Done | From previous runs |
| LAPIS/full+adequacy | storage | ✅ Done | Run via `run_icaps_experiments.sh` Phase 2 |
| LAPIS/full+adequacy | termes | ✅ Done | Run via `run_icaps_experiments.sh` Phase 2 |

*Note: The conversation history mentioned potentially addressing missing benchmark domains like `grippers` and `tyreworld`. If LAPIS needs to be evaluated on these, they are currently marked as **TODO**.*

---

## 2. LAPIS Ablation (Zero-Shot / No Refinement)
Previously labeled "LLM+P with Gen Domain" (Condition B'). This condition failed due to the bash script routing it to `costl` (3 refinements) instead of `llmpp` (0 refinements).

| Condition | Domain | Status | Notes |
| :--- | :--- | :--- | :--- |
| LAPIS Single-Shot | storage | ❌ INVALID | Ran with 3 refinements. Needs rerun. |
| LAPIS Single-Shot | termes | ❌ INVALID | Ran with 3 refinements. Needs rerun. |

---

## 3. Original LLM+P Baseline (True Condition B)
The previous baseline executions used a Zero-Shot prompt structure in `run_llmpp_benchmark.py`. To be 100% fair and accurate, we must execute the original `third-party/llm-pddl/main.py`, which provides the necessary Few-Shot examples to the LLM.

| Condition | Domain | Status | Notes |
| :--- | :--- | :--- | :--- |
| LLM+P (Original) | blocksworld | 🔄 TO BE RERUN | Must use `llm-pddl/main.py` |
| LLM+P (Original) | barman | 🔄 TO BE RERUN | Must use `llm-pddl/main.py` |
| LLM+P (Original) | storage | 🔄 TO BE RERUN | Must use `llm-pddl/main.py` |
| LLM+P (Original) | termes | 🔄 TO BE RERUN | Must use `llm-pddl/main.py` |
| LLM+P (Original) | grippers | 🔄 TO BE RERUN | Mentioned in past logs |
| LLM+P (Original) | tyreworld | 🔄 TO BE RERUN | Mentioned in past logs |

---

## Next Steps
1. Approve the Implementation Plan to fix the scripts.
2. Execute the True LLM+P baseline using the provided third-party code.
3. Rerun the two invalid LAPIS zero-shot ablations.
4. Tabulate final metrics for the paper.
