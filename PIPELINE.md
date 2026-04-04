# LAPIS Pipeline Architecture

This document describes the LAPIS system architecture, focusing on how the pipeline achieves practical reliability for end-users who need NL-to-plan synthesis without PDDL expertise.

---

## Overview

LAPIS translates natural language task descriptions into executable plans through a four-stage pipeline. The system is designed to handle the inevitable errors that arise during LLM-based PDDL synthesis by incorporating validation and refinement loops that recover from failures automatically. Users interact with a Streamlit dashboard where they input task descriptions and receive executable plans without needing to understand PDDL syntax or debug validation errors manually.

The architecture prioritizes practical deployment over theoretical novelty. A single API key and the Streamlit interface are sufficient to run the system; there is no domain-specific configuration required, and the same pipeline handles Blocksworld, Barman, Floortile, and other IPC domains without modification. Problems with plan lengths exceeding 80 steps are handled within the same framework, demonstrating that the approach scales beyond toy examples.

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

### Stage 4: VAL-Guided Iterative Refinement

If FastDownward fails to find a plan or VAL rejects the result, LAPIS enters a refinement loop:

1. Capture validation errors and planner output
2. Prompt the LLM with the error messages and current PDDL
3. Receive corrected domain/problem files
4. Retry planning and validation
5. Repeat up to 3 iterations or until success

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
│   FastDownward    │ ──► plan.txt
└───────────────────┘
        │
        ▼
┌───────────────────┐     ┌─────────────┐
│   VAL Validator   │ ◄───│ Refinement  │
└───────────────────┘     │  Loop (x3)  │
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

## Implementation

### Key Files

| File | Purpose |
|------|---------|
| `src/lapis/pipelines/lapis_low_level.py` | Pipeline orchestration |
| `src/lapis/planner/low/pddl_generation.py` | Domain/problem generation |
| `src/lapis/planner/low/pddl_verification.py` | VAL validation |
| `src/lapis/planner/low/planner_utils.py` | FastDownward invocation |
| `demo/app_premium.py` | Streamlit dashboard |

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

---

## Limitations

The current pipeline validates only syntactic correctness. VAL checks whether PDDL is well-formed, but cannot verify whether the domain models the intended physics. A domain can pass all validation checks while encoding completely wrong semantics. The plan would be "valid" in the LLM's imagined world but fail against the oracle.

Future work includes a semantic verification layer that catches guaranteed-unsolvable problems (unreachable goals, dead-end actions) before wasting planner time.

---

*Last Updated: 2026-04-04*
