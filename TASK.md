# Task: Fix LTL Verification Naming Consistency

## Goal

Fix the LTL verifier always returning VIOLATED for correct plans due to fluent name mismatches across the high-level planning pipeline.

Read `HLP_PROBLEM.md` first — it contains the full root cause analysis.

---

## Current Status

### Done ✅

1. **`src/costl/planner/high/Planner/formula_generator.py`**
   Added a "NAMING CONTRACT" section to the system prompt with abstract `PREDICATE_N(OBJECT_N)` syntax examples. Forces the LLM to copy object names verbatim from the input and populate `fluent_syntax` as a canonical naming contract for the trace generator.

2. **`src/costl/planner/high/Planner/trace_generator.py`**
   Added the same "NAMING CONTRACT" section to both `init_trace` and `trace_generation` system prompts. Forces the LLM to mirror the `fluent_syntax` field character-for-character.

   **Result:** Formula↔trace naming is now consistent. But the formula still uses wrong identifiers (`orange_1` instead of `orange_block_1`) because the problem is upstream.

### Pending ❌

3. **`src/costl/planner/high/Planner/nl_description_generator.py`** — **THIS IS THE NEXT STEP**

   The system prompt at line 36 currently says:
   > *"Instead of technical names like 'black_block_1', say 'the black block number 1'"*

   This must be changed to preserve PDDL identifiers verbatim in `problem`, `goal`, and `constraints` outputs (natural language is fine for `domain` and `actions`).

   **Exact edit needed** — replace line 36:
   ```
   Important: Write naturally as a human would. Instead of technical names like "black_block_1", say "the black block number 1" or "the first black block". Make the physical constraints and limitations very clear and explicit in everyday language.
   ```
   With:
   ```
   Important: Write naturally as a human would for the Domain and Actions fields. Make the physical constraints and limitations very clear and explicit in everyday language.

   CRITICAL — Object Identifier Rule: In the **Problem**, **Goal**, and **Constraints** fields you MUST preserve object identifiers EXACTLY as they appear in the input (e.g. "black_block_1", "orange_block_1"). Do NOT paraphrase them into natural language (NOT "the black block number 1", NOT "black block 1"). These exact strings are required downstream for formal verification. You may add clarifying words around them (e.g. "block black_block_1") but the identifier itself must appear verbatim.
   ```

---

## Verification

After applying the fix to `nl_description_generator.py`, run the end-to-end test:

```bash
cd /DATA/CoSTL
conda run --prefix /DATA/CoSTL/.conda_env python /tmp/test_ltl_fix.py
```

The test script `/tmp/test_ltl_fix.py` is already written. It:
1. Runs the full pipeline on sample 112 (`data/blocksworld/data/data_1/112/nl`)
2. Checks all 5 PDDL objects appear verbatim in the formula (`black_block_1`, `brown_block_1`, `brown_block_2`, `orange_block_1`, `black_block_2`)
3. Checks no abbreviations appear in the trace
4. Calls `trace_check()` with `constraint_evaluation_mode="up"`

**Expected output after fix:**
- `=== FORMULA NAMING ===` → all 5 lines show `OK`
- `=== NAMING CONSISTENCY ===` → `OK - no abbreviation mismatches`
- `VERIFICATION: SATISFIED`

**Note on verifier:** `spot` is not installed in any env. Use `constraint_evaluation_mode="up"` (Unified Planning). However, `unified-planning` may also be missing from the conda env — if `VERIFICATION: VIOLATED` with error "Unified Planning not installed", the naming fix is still valid and the verifier backend is a separate issue.

---

## Key Files

| File | Role |
|------|------|
| `src/costl/planner/high/Planner/nl_description_generator.py` | **NEEDS EDIT** — preserves PDDL identifiers |
| `src/costl/planner/high/Planner/formula_generator.py` | Already fixed — naming contract in prompt |
| `src/costl/planner/high/Planner/trace_generator.py` | Already fixed — naming contract in both prompts |
| `src/costl/planner/high/Planner/trace_check.py` | Unchanged — routes to ltl_verifier submodule |
| `/DATA/LTL_Verifier/ltl_verifier/evaluator.py` | Verifier — spot unavailable, up backend present |
| `HLP_PROBLEM.md` | Full root cause analysis |
| `data/blocksworld/data/data_1/112/nl` | Canonical test case (has 5 blocks with `_block_` in names) |

---

## Environment

- Conda env: `/DATA/CoSTL/.conda_env`
- Always `cd /DATA/CoSTL` before running `conda run` (path resolution depends on cwd)
- API key: loaded from `/DATA/CoSTL/key.sh` (`export API_KEY=...`)
- Verifier submodule: `/DATA/LTL_Verifier` (also at `third-party/LTL_Verifier`)
