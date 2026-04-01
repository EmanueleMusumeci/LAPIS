---
title: "Syntax-Aware PDDL State Synchronization"
subtitle: "Design and Implementation in CoSTL"
author: "CoSTL Engineering"
date: "2026-03-13"
titlepage: true
titlepage-color: "374151"
titlepage-text-color: "ffffff"
book: true
---

# Overview

The **Syntax-Aware Sync** is a set of mechanisms in the CoSTL multi-level planning pipeline that ensures consistent object and predicate naming across all LLM calls — from the high-level planner (HLP) to the low-level planner (LLP) and the symbolic PDDL verifier (VAL / FastDownward).

Without these mechanisms, each LLM call may independently coin different names for the same object or predicate (e.g. `ontable` vs `on-table` vs `on_table`), causing the symbolic planner to fail silently or reject files with misleading parser errors.

---

# Problem Statement

## Root Causes

The CoSTL pipeline chains multiple LLM calls across two planning levels:

1. **HLP** — `nl_description_generator` → `formula_generator` → `trace_generator`
2. **LLP** — `generate_domain` → `generate_problem` → `refine_domain_and_problem_unified`

Each call receives a natural-language description of the problem, not a structured PDDL schema. This leads to two classes of naming inconsistency:

### Object Identifier Drift

The HLP's `nl_description_generator` paraphrases PDDL identifiers into natural language (e.g. `black_block_1` → "the black block number 1"). Downstream LLM calls then re-invent identifiers from this paraphrased text, producing `black_block_1`, `black_block`, `blackBlock1`, etc.

### Predicate Name Drift

PDDL predicates have multiple conventional spellings: `on-table`, `ontable`, `on_table`. Each LLM call independently chooses one. The GT simulator state uses its own canonical form. When the ground-truth init state (from the simulator) is injected into an LLM-generated domain that uses a different spelling, FastDownward's translator exits with code 31 ("critical translator error") — an opaque failure.

## Failure Chain

```
Simulator state:    (ontable green_block_1)
LLM domain:         predicate on-table defined
Raw injection:      (:init (ontable green_block_1))   ← mismatch
FD translator:      exit code 31                       ← failure
```

Without the sync, this cycle repeats across all 3×3 = 9 refinement attempts until the pipeline gives up.

---

# Solution: Syntax-Aware Sync

The solution has four complementary layers, each targeting a different stage of the pipeline.

## Layer 1 — Object Vocabulary from `fluent_syntax`

**Files:** `planner.py`, `pddl_generation.py`, `multi_level_planning.py`

The HLP's `ltl_formula_generation` function produces a `fluent_syntax` string — the first crystallisation of canonical object identifiers. Example:

```
clear(orange_block_1), on(brown_block_1, brown_block_2)
```

This string is parsed with a regex to extract all object identifiers:

```python
def _extract_object_vocabulary(fluent_syntax):
    objects = set()
    for arg_list in re.findall(r'\w+\(([^()]+)\)', fluent_syntax):
        for obj in arg_list.split(','):
            obj = obj.strip()
            if obj:
                objects.add(obj)
    return objects
```

**Key design note:** The regex uses `[^()]+` (excludes both parentheses) rather than `[^)]+`. This handles nested LTL operators such as `F(on(grey_block_1, white_block_1))` — matching only the innermost `on(...)` and correctly extracting `grey_block_1, white_block_1`.

The extracted vocabulary is injected into the PDDL generation prompt:

```
<object_vocabulary>
CRITICAL — Object Identifier Rule: The following object identifiers MUST be used
VERBATIM in the (:objects) block. Do NOT rename, abbreviate, or paraphrase them:
brown_block_1, brown_block_2, orange_block_1
</object_vocabulary>
```

**Graceful degradation:** If `fluent_syntax` is None (pre-existing plan, no HLP run), the vocabulary is empty and the constraint is silently skipped.

## Layer 2 — Resilient Environmental State Synchronization

**File:** `planner_utils.py` — `synchronize_environmental_state()`

Before every planning attempt, the ground-truth init state from the simulator is written into the problem PDDL. This function parses the domain to discover all valid predicates, then maps each simulator predicate to the nearest domain predicate via a six-priority fuzzy matcher.

### Priority Chain

| Priority | Transformation | Example |
|----------|---------------|---------|
| 1 | Exact match | `on` → `on` |
| 2 | Add `is-` prefix | `locked` → `is-locked` |
| 3 | Underscore → hyphen | `on_table` → `on-table` |
| 4 | Hyphen → underscore | `on-table` → `on_table` |
| 5 | Special cases | `holding` → `is-holding` |
| **6** | **Strip all separators** | `ontable` → `on-table` |

Priority 6 was the critical addition: by stripping all hyphens and underscores from both the simulator predicate name and each domain predicate name before comparing, `ontable` correctly resolves to `on-table` even though no single character-substitution rule covers the gap.

```python
sim_stripped = re.sub(r'[-_]', '', sim_name).lower()
for pred_name in available_predicates:
    if re.sub(r'[-_]', '', pred_name).lower() == sim_stripped:
        resolved_name = pred_name
        break
```

### Auto-Adding Missing Objects

A subgoal-scoped `:objects` block may omit objects that appear in the simulator state (e.g. `green_block_2` is in the arm, but the LLM only listed the 3 blocks directly relevant to the subgoal). The sync now auto-adds any object referenced in `filtered_init_lines` that is absent from `:objects`:

```python
declared_objects = set(re.findall(r'(\w+)\s+-\s+\w+', objects_part))
missing_objects = {}
for line in filtered_init_lines:
    for arg in parts[1:]:   # skip predicate name
        if arg not in declared_objects:
            missing_objects[arg] = inferred_type
```

## Layer 3 — Post-Refinement Sync

**File:** `planner.py`

The raw GT init injection inside `refine_domain_and_problem_unified` (at the PDDL string level) can re-introduce a predicate name mismatch if the new domain just generated by the LLM uses a different spelling. Previously, `synchronize_environmental_state` was only called *before* planning, never after writing refined files — so VAL would immediately fail on the refreshed mismatch, triggering another refinement cycle.

The fix: call `synchronize_environmental_state` immediately after writing both the unified refinement and the separate domain/problem refinement outputs:

```python
# After writing refined files:
if pddl_init_state:
    try:
        synchronize_environmental_state(
            domain_path=str(current_domain_path),
            problem_path=str(current_problem_path),
            ground_truth_init_str=pddl_init_state
        )
    except Exception as e:
        logger.warning(f"Post-refinement sync failed: {e}")
```

This breaks the loop: each refinement iteration starts from a semantically consistent (domain, problem) pair.

## Layer 4 — LTL Trace Normalization

**File:** `multi_level_planning.py`

The LTL verifier compares formula atoms against trace predicates using direct string membership (`atom in state`). The trace predicates go through `normalize_predicate`, which converts spaces to underscores: `on(grey_block_1, white_block_1)` → `on(grey_block_1,_white_block_1)`. The formula retains the original spacing. They never match.

The fix normalises comma spacing in **both** the trace and the formula before the check:

```python
import re as _re

string_trace = [
    {_re.sub(r',\s+', ',', p) for p in state}
    for state in target_trace
]
grounded_ltl_formula = _re.sub(r',\s+', ',', grounded_ltl_formula)

is_sat, violations = check_trace(string_trace, grounded_ltl_formula)
```

After this: `on(grey_block_1,white_block_1)` appears identically in both the trace set and the formula atom — the verifier returns the correct result.

---

# Supporting Fixes

## `translate_plan` — PDDL Format Support

FastDownward writes plans in PDDL format: `(action arg1 arg2)`. The legacy `translate_plan` function used the regex `r'(\w+)\((.*?)\)'` which expects function-call syntax `action(arg1, arg2)` — producing an empty translated plan from every FD output. VAL then saw a 0-step plan and reported "Goal not satisfied" even when FD had found a valid plan.

The rewritten function detects both formats:

```python
pddl_pattern = re.compile(r'^\s*\((\w+)((?:\s+\S+)*)\s*\)\s*$')
for line in plan_content.splitlines():
    m = pddl_pattern.match(line)
    if m:
        # PDDL format: (action arg1 arg2)
        ...
    else:
        # Function-call format: action(arg1, arg2)
        ...
```

## VAL Verbosity

The VAL invocation was extended with `-e` (full error report for the entire plan) and `-c` (continue past failed preconditions) to surface all failures in a single pass:

```python
command = [validate_path, "-v", "-e", "-c", domain_file_path]
```

## Prompt Guard — Actions in Problem File

During unified refinement, the LLM occasionally appended `:action` blocks to the problem PDDL, causing a VAL parser error. An explicit constraint was added to both the two-step and single-step refinement prompts:

```
CRITICAL: The PROBLEM file must NEVER contain (:action ...) blocks.
Actions belong ONLY in the domain file.
```

---

# Data Flow Summary

```
HLP run
  +-- ltl_formula_generation()
       +-- fluent_syntax  ------------------------------------+
                                                              |
                                            _extract_object_vocabulary()
                                                              |
                                            object_vocabulary injected
                                            into generate_problem() prompt
                                                              |
For each subgoal:                                             v
  Simulator state --> synchronize_environmental_state()  <---+
        |              (6-priority fuzzy predicate match
        |               + auto-add missing objects)
        |
        v
  plan_with_output() --> FastDownward
        |
        v
  translate_plan()   --> translated_plan.txt --> VAL (-v -e -c)
        |
        v
  After refinement:
  synchronize_environmental_state()  (post-refinement sync)
        |
        v
After all subgoals:
  LTL trace normalization (strip comma spaces)
        |
        v
  check_trace(string_trace, grounded_ltl_formula)
```

---

# Regression Observed (problem 102, data_1)

| Run | Subgoals completed | LTL result | Notes |
|-----|-------------------|-----------|-------|
| Baseline | 0/5 | VIOLATED | `translate_plan` empty; FD args wrong |
| After FD fix | 1/5 | VIOLATED | `translate_plan` fixed; predicate mismatch loops |
| After Priority 6 + post-refinement sync | 2/5 | VIOLATED | `ontable`/`on-table` resolved |
| After auto-add objects | 5/5 | VIOLATED | All plans found; LTL comma mismatch |
| After LTL normalisation | 5/5 | **SATISFIED** _(expected)_ | Full pipeline end-to-end |
