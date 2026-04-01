# High-Level Planner: Naming Consistency Problem

## Summary

The LTL verifier always returns **VIOLATED** for correct plans because fluent names in the formula and trace never match. The root cause is a naming drift introduced by `nl_description_generator.py` that cascades through the entire pipeline.

---

## Pipeline Overview

```
nl file
  └─► nl_description_generation()   → domain, problem, goal, constraints
        └─► ltl_formula_generation() → formula, fluent_syntax
              └─► trace_generation() → trace
                    └─► trace_check() → SATISFIED / VIOLATED
```

---

## Where the Problem Originates

### Step 1 — `nl_description_generator.py`

The input `nl` file contains exact PDDL object identifiers:

```
"Block black_block_1"
"Block black_block_2"
"Block orange_block_1"
...
```

The system prompt **explicitly instructs** the LLM to paraphrase them:

> *"Instead of technical names like 'black_block_1', say 'the black block number 1' or 'the first black block'."*

So the `problem` string passed downstream contains **"black block number 1"**, not **"black_block_1"**.

### Step 2 — `formula_generator.py`

Receives the paraphrased problem. Must invent predicate-safe identifiers for fluents. With no canonical form available, the LLM abbreviates:

| Received | Invented |
|----------|----------|
| "black block number 1" | `black_1` |
| "orange block number 1" | `orange_1` |
| "brown block number 2" | `brown_2` |

Formula produced: `F(clear(orange_1)) & F(!clear(black_2)) & ...`
Fluent syntax: `clear(orange_1), clear(black_2), on(brown_1, brown_2)`

### Step 3 — `trace_generator.py`

Receives the formula + fluent_syntax and correctly mirrors those names — but now both formula and trace use the **wrong identifiers** (`orange_1`, `black_2`) instead of the PDDL ground truth (`orange_block_1`, `black_block_2`).

### Step 4 — `trace_check.py` → `ltl_verifier`

The verifier does **exact string matching** of propositions. Since the formula uses `clear(orange_1)` but the PDDL world uses `orange_block_1`, any downstream check against PDDL state is broken. All plans are flagged as VIOLATED regardless of correctness.

---

## Concrete Example (Sample 112)

**PDDL objects:** `black_block_1`, `brown_block_1`, `brown_block_2`, `orange_block_1`, `black_block_2`

**After `nl_description_generation`:**
> "five blocks: black block number 1, brown block number 1, brown block number 2, orange block number 1, and black block number 2"

**Formula generated:**
```
F(clear(orange_1)) & F(!clear(black_2)) & G(on(BLOCK, black_2) -> ...)
```

**Expected formula (using PDDL identifiers):**
```
F(clear(orange_block_1)) & F(!clear(black_block_2)) & G(... | clear(black_block_1))
```

---

## Why Previous Fix Was Insufficient

We added a **NAMING CONTRACT** section to both `formula_generator.py` and `trace_generator.py` with abstract syntax examples using `PREDICATE_N(OBJECT_N)` placeholders. This enforces consistency *between* formula and trace — but cannot fix the upstream problem: the formula generator never sees `black_block_1`, it only sees "black block number 1" and must invent an identifier anyway.

The fix achieves **formula↔trace consistency** but not **formula↔PDDL consistency**.

---

## Fix Required

**In `nl_description_generator.py`:** Preserve PDDL object identifiers verbatim in the `problem`, `goal`, and `constraints` outputs. Natural language is fine for `domain` and `actions` (which don't flow into predicate generation), but the fields used by `formula_generator` must carry the exact identifier strings.

**Rule to add to the system prompt:**
> In **Problem**, **Goal**, and **Constraints**: use object identifiers exactly as they appear in the input (e.g. `black_block_1`). Do NOT paraphrase. Domain and Actions may use natural language freely.

This ensures `formula_generator` receives `"block black_block_1"` → generates `clear(black_block_1)` → `trace_generator` mirrors it → verifier matches.
