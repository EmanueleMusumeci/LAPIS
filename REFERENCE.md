# REFERENCE.md — LAPIS Technical Reference

This document consolidates design decisions, submission plans, and LLP issue tracking.

---

# Part 1: Design Decisions

> Originally from `PAPER.md`

## 1. PDDL Type Hierarchies vs. Union Types

### The Challenge
LLMs often generate PDDL and ADL "union types" using the `(either type1 type2 ...)` syntax. While valid in some PDDL versions, the **Unified Planning (UP)** parser does not support union types.

### Implementation Choice: Forced Parent-Type Hierarchy
Prompt engineering constraint forces the LLM to maintain a strict single-type hierarchy.
- **Requirement**: Define a common parent type (e.g., `entity`) in the `(:types)` block
- **Result**: High compatibility with UP and FastDownward

## 2. LLM-Based Entity Mapping (Name Grounding)

### The Challenge
Natural language subgoals use descriptive names (e.g., "green block number 2") that don't match PDDL instance names (e.g., `green_block_1`).

### Implementation Choice: Explicit Grounding Step
Dedicated LLM-based preprocessing maps NL descriptions to exact PDDL objects *before* generation begins.

## 3. Granular NL Context Segmentation

### The Challenge
Traditional prompts feed the entire environment description to the LLM, leading to "cheating" by including goal-specific predicates in the domain.

### Implementation Choice: Content-Specific Filtering
- **Domain Generation**: Only actions, preconditions, effects. Blind to current goal.
- **Problem Generation**: Only object list and initial state.

## 4. RAG-Enhanced Refinement Loop

### Implementation Choice: Issue-Based Knowledge Retrieval
Vector DB integration in the refinement loop:
1. Error converted to "Issue" description
2. Search DB for similar past issues
3. Inject successful solutions as "REFERENCE SOLUTIONS"
4. Store verified fixes back to DB

## 5. Lexicon Environment Reproduction (BabyAI)

### Implementation Choice: State-Injection via Monkey Patching
1. **Monkey Patching**: Bypass procedural generation by patching `RoomGrid._gen_grid`
2. **State Representation**: `Sample` objects define initial positions from datasets
3. **Observation Wrapping**: Convert MiniGrid observations to PDDL-ready data
4. **UP Mapping**: Translate to `unified_planning.Problem` objects

## 6. Structural Logic Shadowing Detection

### The Challenge
Merging contiguous high-level steps can "shadow" intermediate states required by LTL constraints.

### Implementation Choice: Domain-Agnostic Structural Analysis
1. **Automated Domain Analysis**: Parse domain at runtime, map action→predicate effects
2. **LTL-Sensitive Fluent Extraction**: Identify critical fluents from formula
3. **Heuristic Toggle Check**: Reject merges that toggle sensitive fluents

---

# Part 2: Submission Plan

> Originally from `SUBMISSION_PLAN.md`

## System Name

**LAPIS** — *Language-Adaptive PDDL Iterative Synthesis*

## Submission Checklist

- [ ] Complete experiments — see `EXPERIMENTS_PLAN.md`
- [ ] Fill in results table in `paper/main.tex`
- [ ] Download AAAI author kit from https://aaai.org/authorkit26/
- [ ] Check page limit — 2 pages excluding references
- [ ] Check anonymization policy on ICAPS 2026 call page
- [ ] Create GitHub Pages website
- [ ] Record demo video
- [ ] Submit via EasyChair

## Website Plan

**URL:** https://emanuelemusumeci.github.io/ContextMattersDemo

**Minimum content:**
- Title + 1-paragraph abstract
- Pipeline figure
- Results table
- Links: paper, code, demo video

**Demo video:** 2–3 min screencast of:
- Blocksworld: NL input → PDDL domain → PDDL problem → plan → animation
- Barman: adequacy check comparison
- Side-by-side with LLM+P baseline

## Git Hygiene

Files to add to `.gitignore`:
- `results_llmpp/`, `results_icaps2026/`
- `data/llmpp/`
- `paper/*.aux`, `paper/*.pdf`, `paper/*.out`
- `key.sh`

---

# Part 3: Low-Level Planner Issues

> Originally from `LLP_ISSUES.md` — reference for debugging

## Issue Index

| # | Issue | Impact | Status |
|---|---|---|---|
| L-1 | `pddl_init_state` never parsed/validated | High | **Fixed** |
| L-2 | No object registry (hallucination) | High | Open |
| L-3 | Domain not validated before problem gen | High | **Fixed** |
| L-4 | FD error text truncated in repair prompt | High | **Fixed** |
| L-5 | No structured failure classification | High | Open |
| L-6 | No trajectory history in repair prompts | High | Open |
| L-7 | Silent sync failures | High | **Fixed** |
| L-8 | Empty-plan hallucination not targeted | Medium | **Fixed** |
| L-9 | No regeneration fallback after 9 attempts | Medium | Open |
| L-10 | No predicate vocabulary contract | Medium | Open |
| L-11 | No temperature control | Medium | Open |
| L-12 | No role separation (planner+generator) | Medium | Open |
| L-13 | No episodic memory / RAG | Medium | Stub exists |

## Priority Fixes (if pursuing 100% success rate)

### Immediate (highest ROI)
1. **L-2** — Object registry post-generation scan
2. **L-6** — Trajectory history in repair prompts
3. **L-9** — Full regeneration fallback
4. **L-11** — Temperature ladder

### Medium-term
5. **L-5** — Structured Context Verifier
6. **L-10** — Predicate vocabulary extraction

### Long-term
7. **L-12** — Role separation (Describer + Generator)
8. **L-13** — Full episodic memory with RAG

## Key Technical Details

### L-2: Object Registry

```python
class ObjectRegistry:
    def __init__(self, vocabulary: set[str]):
        self.vocab = {v.lower() for v in vocabulary}

    def scan_pddl(self, pddl_text: str) -> list[str]:
        """Return object identifiers NOT in vocabulary."""
        found = set(re.findall(r'\b([a-z][a-z0-9_-]*(?:_\d+)?)\b', pddl_text.lower()))
        keywords = {'define','domain','problem','objects','init','goal','and','or','not',
                    'when','forall','exists','precondition','effect','action','parameters',
                    'types','predicates','functions'}
        return [f for f in found if f not in self.vocab and f not in keywords]
```

### L-6: Trajectory History

```python
repair_trajectory = []
# After each repair attempt:
repair_trajectory.append({
    "attempt": r,
    "error": planner_error[:300],
    "strategy": repair_context["Repair strategy"]
})

# Inject into prompt:
trajectory_str = "\n".join(
    f"Attempt {t['attempt']}: {t['error']}"
    for t in repair_trajectory[-3:]
)
```

### L-11: Temperature Ladder

| Call Type | Temperature |
|---|---|
| Domain generation | 0.3 |
| Problem generation | 0.2 |
| Repair round 1 | 0.2 |
| Repair round 2 | 0.1 |
| Repair round 3+ | 0.0 |
| Full regeneration | 0.4 |

---

## External Resources

| Technique | Source |
|---|---|
| Object registry / scene graph grounding | DELTA (delta-llm.github.io) |
| Context Verifier structured fields | OctoTools (arxiv.org/abs/2502.11271) |
| Episodic memory (SQLite + RRF) | Ultra Agentic (Marktechpost) |
| Temperature ladder | Hierarchical Planner (Marktechpost) |
| Role separation | OctoTools |
