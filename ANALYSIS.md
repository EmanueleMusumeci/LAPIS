# CoSTL Agentic Components — Improvement Analysis

> Generated: 2026-03-17
> Sources: Telegram channels **LLM LTL** (research group), **University** (personal knowledge base), codebase exploration.

---

## Table of Contents

1. [Current Architecture at a Glance](#1-current-architecture-at-a-glance)
2. [Component-by-Component Analysis](#2-component-by-component-analysis)
3. [Key Improvement Signals from Telegram](#3-key-improvement-signals-from-telegram)
4. [Improvement Opportunities — Ranked](#4-improvement-opportunities--ranked)
5. [Papers & Resources to Study](#5-papers--resources-to-study)
6. [Synthesis: What Should Change and Why](#6-synthesis-what-should-change-and-why)

---

## 1. Current Architecture at a Glance

CoSTL is a **two-level neurosymbolic planner**:

```
Natural Language Problem
         │
         ▼
┌─────────────────────────────────────┐
│   HIGH-LEVEL PLANNER (HLP)          │  ← 5 sequential LLM calls
│                                     │
│  NL Description → LTL Formula       │
│  LTL Formula → Plan                 │
│  Plan → Trace (init + states)       │
│  Trace → LTL Verification           │
└────────────────┬────────────────────┘
                 │  fluent_syntax, subgoals
                 ▼
┌─────────────────────────────────────┐
│   LOW-LEVEL PLANNER (LLP)           │  ← iterative LLM calls per subgoal
│   [per subgoal, up to 9 attempts]   │
│                                     │
│  Generate PDDL domain               │
│  Generate PDDL problem              │
│  Inject simulator state (Layer 2)   │
│  Symbolic planner (FastDownward…)   │
│  Execute in simulator               │
│  Refine on failure                  │
└─────────────────────────────────────┘
```

**Core weakness identified by the team**: Each LLM call independently interprets names → naming drift → LTL verifier always reports VIOLATED even for correct plans. Three layers of "Syntax-Aware Sync" are fixing this, but Layer 3 (in `nl_description_generator.py`) is still pending.

---

## 2. Component-by-Component Analysis

### 2.1 `nl_description_generator.py` — LLM Call #1
| | |
|---|---|
| **Role** | Converts raw NL problem into structured domain/problem/goal/constraints |
| **Current Issue** | Actively paraphrases PDDL identifiers (`black_block_1` → "the black block number 1"), causing downstream naming drift |
| **Impact** | **Critical** — root cause of the entire naming drift bug chain |
| **Fix status** | Layer 3 of Syntax-Aware Sync pending (line 36 of the file) |
| **Improvement signal** | Team notes from meeting (ID 293 in LLM LTL): the output of this stage should be the "naming contract" anchor; all subsequent prompts must receive verbatim PDDL identifiers |

### 2.2 `formula_generator.py` — LLM Call #2
| | |
|---|---|
| **Role** | Generates LTL formula + `fluent_syntax` (canonical naming contract) |
| **Current Issue** | Fixed with NAMING CONTRACT section; depends on correct output from stage 1 |
| **Improvement opportunity** | **DFA-based alternative**: instead of generating an LTL formula and then verifying against a trace, Elena Umili (LLM LTL chat, ID 393) proposes converting LTL to a DFA first and using DFA state transitions to derive subgoals directly. This removes the LTL→trace roundtrip and the naming-sensitive trace check. |
| **Relevant paper** | DeepLTL (arxiv.org/abs/2410.04631) — deep learning for LTL formula generation/satisfaction |

### 2.3 `plan_generator.py` — LLM Call #3
| | |
|---|---|
| **Role** | Generates a high-level plan (list of abstract actions) satisfying the constraints |
| **Current approach** | Single-shot with up to 5 retries; constraint-focused prompting |
| **Improvement opportunities** | (1) **Tree of Thoughts**: instead of retrying with the same prompt on failure, explore multiple plan branches concurrently — suggested by both Iocchi and Alessio (LLM LTL chat, IDs 293–294). (2) **Autoregressive plan generation**: build the plan state-by-state, checking at each step whether the emerging state violates any constraint (Alessio's refactor, ID 330: "il piano lo genera in maniera autoregressiva e si costruisce lo stato ad ogni step"). (3) **Constraint complexity ordering**: resolve simpler constraints (immediate, fewer fluents) before complex ones (ID 330). |

### 2.4 `trace_generator.py` — LLM Calls #4–N
| | |
|---|---|
| **Role** | Generates initial state + full trace from plan |
| **Current issue** | Depends on naming contract working end-to-end; still prone to hallucinated fluents |
| **Improvement opportunities** | (1) **DFA-guided trace extension**: instead of asking an LLM to generate a trace, use the DFA derived from the LTL formula to determine which transition must be taken at each plan step, reducing the LLM's degrees of freedom and hallucination surface. (2) **Constraint-level trace check** (not name-dependent): instead of matching formula predicates to trace atoms by name, check each constraint independently against the set of satisfied/violated conditions (Alessio, ID 330). |

### 2.5 `trace_check.py` — LTL Verification
| | |
|---|---|
| **Role** | Routes trace + formula to LTL_Verifier submodule (Spot/UP backends) |
| **Current issue** | Only works if formula and trace use identical names — solved once Layers 1–3 are complete |
| **Improvement opportunity** | Move to **DFA-based verification** (Vincenzo's suggestion, ID 293): compile the LTL formula to a DFA once and use the DFA to (a) derive subgoals and (b) check plan execution step-by-step, skipping the full trace generation. Tool available: Fuggitti's LTL-to-PDDL tool mentioned in ID 393. |

### 2.6 `pddl_generation.py` — PDDL Generation & Refinement
| | |
|---|---|
| **Role** | Generates PDDL domain/problem; refines on VAL errors |
| **Current approach** | Up to 9 attempts; uses Layer 1 (fluent_syntax vocabulary injection) + Layer 2 (fuzzy state sync) |
| **Improvement opportunities** | (1) **RAG-based few-shot prompting**: inject examples of past successful PDDL generation + refinement into the prompt (Vincenzo & Alessio, IDs 293, 295). (2) **DELTA-like scene pruning**: before generating PDDL, prune unreachable/irrelevant parts of the problem state to reduce the LLM's context load (mentioned in University msg 1103, referencing delta-llm.github.io). (3) **N-level abstraction**: extend beyond 2 levels to support HTN-like decomposition for complex domains (Nardi, ID 293). |

### 2.7 `planner_utils.py` — Execution & State Synchronization
| | |
|---|---|
| **Role** | Layer 2 state sync; runs symbolic planner; handles execution |
| **Current approach** | 6-priority fuzzy match; graceful degradation |
| **Improvement opportunity** | **Logical dependency graph**: track which subplan actions depend on the post-conditions of previous ones. If execution fails at subplan N, the dependency graph identifies which earlier subplans are affected without restarting from scratch (from Emanuele's vision note, University msg 1103). |

### 2.8 Multi-Level Pipeline (`multi_level_planning.py`)
| | |
|---|---|
| **Role** | Orchestrates HLP → LLP → Simulation → Verification loop |
| **Current gap** | HLP→LLP feedback is limited: if LLP fails, there is no structured way to feed that failure back to HLP to revise the high-level plan |
| **Improvement opportunities** | (1) **RL-based feedback controller**: use a reinforcement learning signal (execution success/failure) to guide high-level plan regeneration (Iocchi, ID 293). (2) **Orchestrator pattern**: replace the fixed loop with a learned routing controller — e.g., Orchestrator-8B style (RL-trained, cost-aware, routes between specialist modules). (3) **N levels of abstraction**: generalize the current 2-level architecture to N levels with arbitrary decomposition depth (Nardi, ID 293). |

---

## 3. Key Improvement Signals from Telegram

### From LLM LTL chat (the CoSTL research group)

| Signal | Author | Key idea |
|---|---|---|
| **DFA instead of LTL trace** | Vincenzo Suriani (ID 293) | Compile formula to DFA once; derive subgoals directly from DFA transitions. Removes name-sensitive trace check entirely. |
| **Tree of Thoughts for plan exploration** | Alessio + Iocchi (IDs 293–294) | On LLP failure, instead of returning to HLP with a single feedback message, explore multiple alternative HLP branches as a tree. |
| **RAG for refinement few-shots** | Vincenzo + Alessio (IDs 293, 295) | Retrieve past successful refinement examples and inject them as few-shot context into the refinement prompt. |
| **RL for feedback signal** | Iocchi (ID 293) | Treat plan success/failure as a reward signal and use RL to improve the HLP policy over multiple planning episodes. |
| **Autoregressive plan + state building** | Alessio (ID 330) | Generate plan step-by-step, materializing the state at each step instead of generating all steps then checking. |
| **Constraint complexity ordering** | Alessio (ID 330) | Solve immediate/simple constraints first; build plan incrementally. |
| **Constraint-level trace check** | Alessio (ID 330) | Check each constraint independently over all states rather than doing full formula matching. More robust to naming issues. |
| **N-level planning depth** | Nardi (ID 293) | Generalize from 2 levels to N levels depending on task complexity (HTN-like). |
| **Until operator testing** | Emanuele (ID 395) | Test how reliably LLMs model the `Until` temporal operator; current pipeline may silently fail on non-trivial LTL operators. |
| **Abstract text-based simulator** | Iocchi (ID 293) | Evaluate with a lightweight LLM-text simulator before committing to physical simulators, to test scaling. |
| **LTLf-constrained subgoals** | Elena Umili (ID 393) | Each subgoal from the DFA is itself a constrained planning problem: goal = DFA transition label, constraint = `G(¬b)` for all blocking transitions. Can use Fuggitti's tool. |

### From University personal knowledge base

| Signal | Article / Note | Key idea for CoSTL |
|---|---|---|
| **OctoTools** | arxiv.org/abs/2502.11271 (Stanford, 2025) | Standardized "tool cards" + planner-executor architecture with test-time verification and re-evaluation. CoSTL's pipeline could adopt tool cards for each agentic stage (formula gen, trace gen, PDDL gen). |
| **A-RAG** | University msg 1469 | Hierarchical retrieval with decision-making over what to retrieve. Applicable to CoSTL's PDDL refinement: retrieve the right level of context (domain-level vs. object-level vs. error-level). |
| **ALCHEMY** | University msg 425 | Relaxation-graph-of-thought: iteratively remove constraints to find feasible plans. Directly applicable to CoSTL when the LTL-constrained problem is infeasible. |
| **DELTA** | delta-llm.github.io | Scene decomposition + substep local loops. The DELTA substep decomposition pattern (Emanuele, University msg 1103) maps well onto CoSTL's LLP refinement loop. |
| **Orchestrator-8B** | arxiv.org/pdf/2511.21689 (NVIDIA) | RL-trained router: routes between tools/models with cost-aware multi-objective reward. Applicable to CoSTL's pipeline orchestration: route between symbolic planner, LLM refiner, and simulator based on cost/success. |
| **DeepLTL** | arxiv.org/abs/2410.04631 | Neural approach to LTL formula generation and satisfaction. Could replace or augment CoSTL's LTL formula generation step. |
| **LCM/LPM** | arxiv.org/pdf/2412.08821 | Large Concept Model: operates in concept space rather than token space. Could replace the HLP's NL description generator, providing more stable concept-level representations resistant to naming drift. |
| **RoboData / GRASP** | University msgs 1103, 1229 | Agentic SPARQL query generation for knowledge extraction. Could ground CoSTL's domain descriptions in verifiable knowledge sources (Wikidata), reducing hallucinated predicate names. |
| **Emanuele's architecture vision** | University msg 1103 | Full integration blueprint: LPM for high-level plan → LCM for goal outline → DELTA-like local solver → safety check via LTL → epistemic constraints → dependency graph for efficient failure recovery. |

---

## 4. Improvement Opportunities — Ranked

### Tier 1 — High Impact, Feasible Now

#### A. Complete Layer 3 of Syntax-Aware Sync
- **File**: `src/costl/planner/high/Planner/nl_description_generator.py`, line 36
- **Action**: Add rule to preserve PDDL identifiers in `Problem`, `Goal`, and `Constraints` fields
- **Why critical**: Root cause of all naming drift; without this, Layers 1+2 can't fully protect

#### B. DFA-Based Subgoal Decomposition (replace LTL trace generation)
- **Idea**: Compile the LTL formula to a DFA (using Spot). Use DFA state transitions as subgoal sequence. Each subgoal = DFA transition label. Check plan execution by stepping the DFA.
- **Impact**: Eliminates the entire `trace_generator.py` naming problem; makes verification exact and fast
- **Effort**: Medium — requires integrating Spot's DFA output into the pipeline
- **Source**: Vincenzo (LLM LTL ID 293), Elena (ID 393)

#### C. Autoregressive Plan Generation with Intermediate State Check
- **Idea**: Generate plan step-by-step; after each step, materialize the state and check whether any constraint is violated before proceeding
- **Impact**: Dramatically reduces invalid plan generation; early stopping on infeasible branches
- **Effort**: Medium — Alessio has a prototype (ID 330)
- **Source**: Alessio (ID 330)

### Tier 2 — High Impact, Requires More Work

#### D. RAG-Based Refinement Memory
- **Idea**: Store past PDDL generation + refinement attempts (keyed by domain type and error class). At each new attempt, retrieve the top-k most similar past successes and inject as few-shot examples.
- **Impact**: Reduces refinement iterations; LLM learns from its own past corrections
- **Effort**: Medium-high — needs a vector store and retrieval pipeline
- **Source**: Vincenzo + Alessio (IDs 293, 295); A-RAG paper (University msg 1469)

#### E. Tree of Thoughts for High-Level Plan Recovery
- **Idea**: When LLP fails, instead of re-prompting HLP with a single error message, maintain a beam of K alternative high-level plans and select the best branch via symbolic evaluation
- **Impact**: Better recovery from LLP failures; reduces dependency on single HLP generation
- **Effort**: High — requires beam search infrastructure
- **Source**: Iocchi + Alessio (IDs 293–294)

#### F. Constraint Complexity Ordering in Plan Generation
- **Idea**: Sort LTL constraints by complexity (immediate > bounded > unbounded; fewer fluents first). Resolve them in order.
- **Impact**: Avoids the common failure where simple constraints are violated because complex ones dominate the prompt
- **Effort**: Low-medium — constraint parsing + ordering logic
- **Source**: Alessio (ID 330)

### Tier 3 — Long-Term Research Directions

#### G. N-Level Hierarchical Planning (HTN-style)
- **Idea**: Replace the fixed 2-level HLP/LLP architecture with N-level decomposition. High-level goals recursively decompose into subgoals until they are directly executable.
- **Impact**: Scalability to complex, long-horizon tasks
- **Effort**: Very high — architectural change
- **Source**: Nardi (ID 293), referencing HTN/Aiello paper

#### H. RL-Based Feedback Signal
- **Idea**: Treat each planning episode as an RL step. Use simulator execution success as reward. Train a policy that improves HLP generation over episodes.
- **Impact**: System improves over time without manual prompt tuning
- **Effort**: Very high — requires RL infrastructure and many episode samples
- **Source**: Iocchi (ID 293)

#### I. Logical Subplan Dependency Graph
- **Idea**: Build a dependency graph linking each subplan action to the pre/post-conditions of other subplans. Use this graph to identify which earlier subplans to revise when a later one fails.
- **Impact**: Targeted failure recovery instead of global replanning
- **Effort**: Very high — requires formal dependency tracking
- **Source**: Emanuele (University msg 1103)

#### J. Knowledge Grounding via RoboData/SPARQL
- **Idea**: Before generating PDDL, query a structured knowledge base (Wikidata) for the domain objects and their properties. Use this as ground truth for predicate names.
- **Impact**: Eliminates hallucinated predicates; names are anchored to a KG
- **Effort**: High — requires KG integration pipeline
- **Source**: Emanuele's RoboData work (University msg 1103, 1229)

---

## 5. Papers & Resources to Study

| Paper / Resource | URL | Relevance to CoSTL |
|---|---|---|
| **DeepLTL** | arxiv.org/abs/2410.04631 | LTL formula generation/satisfaction with deep learning — could improve `formula_generator.py` |
| **DELTA (Bosch)** | delta-llm.github.io | Scene decomposition + local refinement loops — maps to LLP refinement strategy |
| **OctoTools** | arxiv.org/abs/2502.11271 | Tool-card + planner-executor with test-time verification — architectural pattern for CoSTL stages |
| **ALCHEMY** | (paper outline, University msg 425) | Relaxation-graph-of-thought for infeasible planning problems — applicable when LTL constraints make problem infeasible |
| **Orchestrator-8B** | arxiv.org/pdf/2511.21689 | RL-trained pipeline router — for cost-aware orchestration of HLP/LLP/simulator |
| **A-RAG** | (University msg 1469) | Hierarchical agentic retrieval — for PDDL refinement few-shot memory |
| **LCM (Large Concept Model)** | arxiv.org/pdf/2412.08821 | Concept-space generation, more stable than token generation — potential replacement for `nl_description_generator.py` |
| **Skilled LLMs Workshop @ FLOC 2026** | skilled-llms.github.io/2026/ | Directly relevant venue; Elena shared (LLM LTL ID 369) |
| **FLOC 2026 OVERLAY Workshop** | overlay.uniud.it/workshop/2026/ | Formal methods + AI venue; shared today (LLM LTL ID 398) |
| **PSG4D** | github.com/Jingkang50/PSG4D | 4D scene graphs — relevant if CoSTL expands to 3D/4D simulators |
| **Fuggitti LTLf→PDDL tool** | (mentioned by Elena, ID 393) | Translates LTLf constraints to PDDL goals — enables constrained low-level planning natively |

---

## 6. Synthesis: What Should Change and Why

### The Single Most Important Thing
**Complete Layer 3** (`nl_description_generator.py`). Every other improvement is blocked or degraded by naming drift. This is a small, targeted prompt edit with outsized impact.

### The Highest-Leverage Architectural Change
**Replace the LTL trace pipeline with DFA-based subgoal derivation.** The current `trace_generator.py` → `trace_check.py` loop is fragile because it depends on two LLM calls producing identical names. If the LTL formula is compiled to a DFA (Spot does this in one call), the DFA's transitions become deterministic subgoals. No trace generation needed. Verification becomes exact. This collapses two agentic components into a deterministic one.

### The Best Near-Term Addition
**RAG memory for PDDL refinement.** The LLP already has a refinement loop with up to 9 attempts. Injecting few-shot examples from past successes into those prompts is additive, non-breaking, and addresses the observed issue of LLMs repeating the same mistakes across refinement rounds.

### The Best Long-Term Direction
**N-level hierarchical planning with a subplan dependency graph.** The current 2-level architecture is a special case of HTN planning. Generalizing it — with a dependency graph to enable targeted recovery — would dramatically improve robustness on complex, long-horizon problems while preserving the neurosymbolic architecture.

---

*Analysis based on: codebase exploration (March 2026), Telegram/LLM LTL research group discussions (Nov 2025 – Mar 2026), Telegram/University personal knowledge base (Nov 2024 – Mar 2026).*
