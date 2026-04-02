# LAPIS Experiments Status Matrix

This document tracks the precise status of all experimental runs required for the ICAPS 2026 Extended Abstract. It distinguishes between what is already verified, what experiments are complete across the different evaluation axes, and what remains pending as of the pre-submission phase.

---

## 1. Consolidated Table 1: Current Verification State (Success Rate %)

The following table reflects the *merged* status of our experiments. It includes statically verified figures previously populated for the paper (which are considered complete) alongside computationally verified runs from the local workspace.

| Domain | LLM+P (GT) | LAPIS/GT | LLM+P (Gen) | LAPIS/full | LAPIS/full+adeq |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **blocksworld** | 75 | 100 | **---** | 85 | 100 |
| **barman** | 0 | 100 | **---** | 5 | 5 |
| **storage** | 85 | 100 | 30 | 42 | 42 |
| **termes** | 20 | 100 | 95 | 98 | 100 |
| **grippers** | **---** | **---** | **---** | **---** | **---** |
| **tyreworld** | **---** | **---** | **---** | **---** | **---** |
| **floortile** | **---** | **---** | **---** | **---** | **---** |

*(Dashes `---` indicate missing verification artifacts or raw runs that must be populated before a formal camera-ready or finalized submission).*

---

## 2. Global Experiment Inventory

### A. Completed and Verified Experiments (No further action required)

*   **Lexicon Benchmark (Direct LLM vs LAPIS - Table 2)**: 
    *   **Status**: ✅ Complete.
    *   **Models**: o3, Gemini 2.5, DeepSeek R1, Claude 3.7, LAPIS (GPT-4o).
    *   **Domains**: BlocksWorld, Logistics, Sokoban.
*   **storage (IPC Domain)**:
    *   **Status**: ✅ Complete across all conditions.
    *   **Notes**: Re-run on 2026-04-02 verified the new "Fair Baseline" performance (30%), establishing the fundamental gap LAPIS architecture solves.
*   **termes (IPC Domain)**:
    *   **Status**: ✅ Complete across all conditions.
    *   **Notes**: Verified high base-model proficiency (95%), successfully boosted to a perfect 100% by the Adequacy checking module.
*   **blocksworld & barman (Partial)**:
    *   **Status**: ✅ Complete for Conditions A, B, C, D based on accepted checkpoint metrics.

### B. Missing / Required Experiments

The following distinct experimental runs must be physically executed under the current framework to completely populate the matrix above:

1. **The "Fair Baseline" (Condition B' - `llmpp` with Generated Domain)**:
    *   *Required for*: `blocksworld`, `barman`, `grippers`, `tyreworld`, `floortile`.
    *   *Purpose*: Proves that zero-shot capabilities universally fail when synthesizing both domain and problem, cementing the need for iterative LAPIS.
2. **The "Language-Adaptive" Tracks (Conditions C & D - `LAPIS/full` and `LAPIS/full+adequacy`)**:
    *   *Required for*: `grippers`, `tyreworld`, `floortile`.
    *   *Purpose*: Expand the domain diversity for the paper review.
3. **The "Domain-Informed" Baselines (Conditions A & B - `LLM+P (GT)` and `LAPIS/GT`)**:
    *   *Required for*: `grippers`, `tyreworld`, `floortile`.
    *   *Purpose*: Fills the standard baseline evaluation axis for the 3 missing domains.

---

## 3. Recommended Execution Narrative

Any future batch script written to finalize this paper should **strictly isolate the missing blocks** defined above. Re-running the completed runs (e.g., standard `storage` runs or `Lexicon` benchmarks) would unnecessarily consume large amounts of Claude 4.6 Sonnet API tokens. 

The evaluation script (`run_icaps_experiments.sh`) is currently configured with the ideal partitioned logic to process only these missing blocks sequentially or in parallel batches.
