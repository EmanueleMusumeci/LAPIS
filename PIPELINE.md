# LAPIS Pipeline Architecture

This document describes the LAPIS system architecture, focusing on how the pipeline achieves practical reliability for end-users who need NL-to-plan synthesis without PDDL expertise.

---

## Overview

LAPIS translates natural language task descriptions into executable plans through a four-stage pipeline. The system is designed to handle the inevitable errors that arise during LLM-based PDDL synthesis by incorporating validation and refinement loops that recover from failures automatically. Users interact with a web dashboard where they input task descriptions and receive executable plans without needing to understand PDDL syntax or debug validation errors manually.

The architecture prioritizes practical deployment over theoretical novelty. A single API key and the web interface are sufficient to run the system; there is no domain-specific configuration required, and the same pipeline handles Blocksworld, Barman, Floortile, and other IPC domains without modification. Problems with plan lengths exceeding 80 steps are handled within the same framework, demonstrating that the approach scales beyond toy examples.

---

## Pipeline Stages

### Stage 1: Domain Synthesis

Given a natural language description of the task environment, the LLM generates a PDDL domain file encoding action schemas, type hierarchies, and predicate definitions. This stage can be bypassed when a ground-truth domain is available (LAPIS/GT condition), but the more interesting case is full synthesis where the LLM must infer the domain structure from the NL description alone.

The key insight from our experiments is that LLM-generated domains often achieve higher success rates than human-authored ground truth domains. This counterintuitive finding arises because the LLM's generated domain and problem files share consistent naming conventions and structural assumptions, while forcing an LLM to adapt to a human-authored domain introduces coupling errors.

### Stage 2: Adequacy Check (Optional)

Before proceeding to problem synthesis, an optional Chain-of-Thought verification step asks the LLM to assess whether the generated domain adequately covers the task requirements. This catches cases where critical predicates are missing (e.g., tracking whether a shaker is clean in Barman) before wasting refinement iterations on an incomplete domain.

The adequacy check is implemented as a single LLM call with structured prompting. While it adds latency, it prevents the refinement loop from attempting to fix problems that stem from fundamental domain modeling gaps rather than syntactic errors.

### Stage 3: Problem Synthesis with Schema Injection

The LLM generates a problem instance (objects, init state, goal) constrained by the domain schema. LAPIS extracts exact type definitions, predicate signatures, and constants from the domain file and injects them into the problem generation prompt. This prevents the common failure mode where the LLM hallucinates predicates or uses incorrect argument types.

Schema injection is the key differentiator from naive single-shot synthesis. Without it, the problem file frequently references predicates that don't exist in the domain, causing immediate validation failures with no clear path to recovery.

### Stage 4: Semantic Verification (Optional)

Before invoking the planner, an optional semantic verification layer analyzes the generated domain and problem for structural issues that guarantee failure. This catches problems that are syntactically valid but semantically unsolvable:

1. **Unfixable Preconditions**: Actions requiring predicates that no action produces (static predicates that must be in init)
2. **Unreachable Actions**: Actions whose preconditions can never be satisfied
3. **Missing Goal Support**: Goal predicates that no action can achieve

The semantic check uses a pluggable extractor architecture (`--extractor_type auto|regex|up`) that parses PDDL and builds a dependency graph of predicates and actions. Warnings are surfaced to the refinement loop, enabling targeted fixes rather than blind iteration.

**Key finding from benchmarks**: Domains with clean semantic checks (blocksworld, grippers) achieve 100% success rates, while domains with structural warnings correlate strongly with planning failures.

### Stage 5: VAL-Guided Iterative Refinement

If FastDownward fails to find a plan or VAL rejects the result, LAPIS enters a refinement loop:

1. Capture validation errors, planner output, and semantic warnings
2. Prompt the LLM with the error messages, semantic issues, and current PDDL
3. Receive corrected domain/problem files
4. Retry semantic verification, planning, and validation
5. Repeat up to 3-6 iterations or until success

A critical constraint prevents the LLM from modifying the initial state (`:init` block) during refinement. This stops the model from "solving" validation errors by hallucinating an easier starting world.

---

## Architecture Diagram

```
NL Task Description
        │
        ▼
┌───────────────────┐
│ Domain Generator  │ ──► generated_domain.pddl
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Adequacy Check   │ (optional CoT verification)
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Schema Extractor │ ──► types, predicates, constants
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Problem Generator │ ──► problem.pddl
└───────────────────┘
        │
        ▼
┌───────────────────┐
│Semantic Verifier  │ (optional structural analysis)
└───────────────────┘
        │
        ▼
┌───────────────────┐
│   FastDownward    │ ──► plan.txt
└───────────────────┘
        │
        ▼
┌───────────────────┐     ┌─────────────┐
│   VAL Validator   │ ◄───│ Refinement  │
└───────────────────┘     │ Loop (x3-6) │
        │                 └─────────────┘
        ▼
┌───────────────────┐
│  Oracle Check     │ (evaluation only)
└───────────────────┘
        │
        ▼
    Success/Failure
```

---

## Evaluation Methodology

During experiments, the ground-truth domain is strictly walled off from the LLM. The refinement loop validates plans against the LLM's own generated domain using VAL. Ground truth is used only as a post-hoc oracle to compute success rates for Table 1. This prevents the LLM from pattern-matching against human-authored PDDL and ensures that reported success rates reflect genuine task completion.

---

## Oracle Pipeline Variant (Simulator-Grounded Refinement)

An alternative configuration uses the ground truth PDDL environment as a **simulation oracle** during refinement, not just for post-hoc evaluation. This variant tests whether semantic feedback from a "real world" simulator improves convergence compared to purely syntactic VAL validation.

### Key Differences from Standard Pipeline

1. **Simulator Setup**: The GT domain and problem are loaded into Unified Planning's `SequentialSimulator`, creating an executable "ground truth world"
2. **Plan Execution**: After VAL validation passes, the plan is executed step-by-step in the simulator
3. **Failure Detection**:
   - If an action is not applicable in the current simulator state → action precondition/effect error
   - If the plan executes but doesn't satisfy the GT goal → problem goal mismatch
4. **LLM-Generated Feedback**: Simulator failures trigger an LLM analysis that converts execution traces and state observations into actionable refinement suggestions
5. **Fair Grounding**: The feedback reveals only what a robot's sensors would observe (state facts, action applicability), never exposes GT structure

### Architecture Flow

```
NL Task → Domain Gen → Problem Gen → Planning → VAL Validation
                                          ↓
                                    [PASS] ✓
                                          ↓
                                 ┌────────────────┐
                                 │   Simulator    │
                                 │   Validation   │
                                 └────────────────┘
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    ▼                     ▼                     ▼
              [Action Failed]       [Plan Succeeded]      [Goal Failed]
                    │                     │                     │
                    ▼                     ▼                     ▼
           ┌──────────────┐              OK            ┌──────────────┐
           │ LLM analyzes │                            │ LLM analyzes │
           │ exec trace & │                            │ final state  │
           │ state before │                            │ vs goal      │
           │ failure      │                            └──────────────┘
           └──────────────┘                                    │
                    │                                          │
                    └──────────────┬───────────────────────────┘
                                   ▼
                          Refinement Iteration
                          (fix domain/problem)
```

### Example Feedback Flow

**Iteration 0**: LLM generates problem with goal:
```pddl
(contains shot1 cocktail1)
(contains shot2 cocktail2)  ; Wrong!
(contains shot3 cocktail3)  ; Wrong!
```

**Simulator Validation**: Plan executes 48 actions successfully but fails goal check against GT:
```
SIMULATOR_ERROR: Plan executed but did NOT achieve the goal.
Goal predicates NOT satisfied:
  - (contains shot2 cocktail3)
  - (contains shot3 cocktail2)
```

**LLM Analysis**: Diagnoses that cocktails are swapped between shot2 and shot3

**Iteration 1**: Problem refined with correct goal:
```pddl
(contains shot1 cocktail1)
(contains shot2 cocktail3)  ; Fixed!
(contains shot3 cocktail2)  ; Fixed!
```

**Result**: Plan validates on simulator → Success

### Implementation Files

| File | Purpose |
|------|---------|
| `src/lapis/pipelines/low_level_planning_oracle.py` | Oracle pipeline with GT simulator |
| `src/lapis/planner/low/planner_oracled.py` | Planner with simulator validation |
| `src/lapis/simulators/pddl_simulator.py` | Generic PDDL simulator wrapper |
| `test_oracle_barman.py` | Test script for oracle pipeline |

### Configuration

```python
pipeline = LowLevelPlanningOraclePipeline(
    agent=agent,
    generate_domain=True,
    gt_source_dir="third-party/llm-pddl/domains",  # GT PDDL location
)
```

The planner automatically receives a `gt_simulator` parameter which enables simulator validation within the refinement loop.

### When to Use

- **Research**: Studying the impact of semantic vs syntactic feedback on LLM refinement
- **Embodied AI**: When a real robot/environment can provide execution feedback
- **Domain Development**: Bootstrap new domains by having the LLM learn from GT simulator responses

---

## Implementation

### Key Files

| File | Purpose |
|------|---------|
| `src/lapis/pipelines/lapis_low_level.py` | Pipeline orchestration |
| `src/lapis/planner/low/pddl_generation.py` | Domain/problem generation |
| `src/lapis/planner/low/pddl_verification.py` | VAL validation |
| `src/lapis/planner/low/planner_utils.py` | FastDownward invocation |
| `lapis-web/` | Web dashboard (React + FastAPI) |

### Configuration

```python
model = "claude-sonnet-4-6"
planner = "up_fd"  # FastDownward via unified-planning
planner_timeout = 180  # seconds
max_refinements = 3
```

### Ablation Flags

| Flag | Effect |
|------|--------|
| `--generate_domain` | Enable domain synthesis |
| `--ablation full` | Standard refinement loop |
| `--ablation full_adequacy` | Add CoT adequacy check |
| `--ablation baseline` | Disable refinement (single-shot) |
| `--semantic_checks` | Enable semantic verification layer |
| `--extractor_type auto` | PDDL extractor backend (auto/regex/up) |
| `--pddl_gen_iterations N` | Override refinement iterations (default: 3) |

---

## Semantic Verification Results

The optional semantic verification layer (`--semantic_checks`) was benchmarked across all 7 IPC domains:

| Domain | Problems | VAL Success | Avg Refinements | Avg Time |
|--------|----------|-------------|-----------------|----------|
| barman | 20/20 | 50% | 3.0 | 116s |
| blocksworld | 20/20 | 100% | 0.0 | 9s |
| floortile | 20/20 | 65% | 3.0 | 188s |
| grippers | 20/20 | 100% | 0.1 | 11s |
| storage | 20/20 | 55% | 3.0 | 133s |
| termes | 20/20 | 100% | 2.2 | 113s |
| tyreworld | 20/20 | 55% | 3.0 | 181s |
| **TOTAL** | **140/140** | **75%** | - | - |

**Key Observations:**
- Domains with clean semantic checks (no warnings): 100% success rate (blocksworld, grippers, termes)
- Domains with semantic warnings: 50-65% success rate
- Most common warning: "unfixable preconditions" (static predicates expected in init)
- Strong correlation between semantic cleanliness and planning success

---

## Limitations

The semantic verification layer catches structural issues (unreachable actions, unfixable preconditions) but cannot verify whether the domain models the intended physics. A domain can pass all verification checks while encoding completely wrong semantics. The plan would be "valid" in the LLM's imagined world but fail against the oracle.

The current semantic checks focus on domain-level analysis. Future work includes:
- Problem-level reachability analysis
- Goal achievability verification
- Plan quality heuristics

---

*Last Updated: 2026-04-05*
