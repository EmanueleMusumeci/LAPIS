# CoSTL — Known Issues & Resource Mapping

> Compiled: 2026-03-17
> Last updated: 2026-03-18
> Sources: Antigravity session (2026-03-12), TASK.md, HLP_PROBLEM.md, LLM LTL research group discussions.

---

## Issue Index

| # | Issue | Severity | Status | Proposed Change | Expected Effect |
|---|---|---|---|---|---|
| I-1 | [LTL Naming Drift — Layer 3 pending](#i-1-ltl-naming-drift--layer-3-pending) | 🔴 Critical | 🔄 Layers 1&2 done; Layer 3 pending | Edit `nl_description_generator.py:36` — add CRITICAL Object Identifier Rule: preserve object IDs verbatim in Problem/Goal/Constraints fields | Closes the drift source; formula and trace will use `black_block_1` not `"the black block"` → verifier returns SATISFIED for correct plans |
| I-2 | [PDDL State Hallucination](#i-2-pddl-state-hallucination) | 🔴 Critical | ✅ L-1,3,4,7,8 done — L-2,6,9,11 pending | L-2: object registry post-gen scan; L-6: trajectory history in repair prompts; L-9: full regeneration fallback; L-11: temperature ladder | Eliminates hallucinated objects before FD call; stops LLM repeating same failed fix; adds escape hatch when 9 attempts exhausted; reduces variance in PDDL syntax |
| I-3 | [Broken HLP→LLP Feedback Loop](#i-3-broken-hlpllp-feedback-loop) | 🟠 High | ❌ Not addressed | Structured LLP failure context propagated to HLP; Reflexion-style re-prompting of HLP when LLP exhausts budget | HLP can revise abstract subgoals instead of silently failing; expected improvement in `GT_success_rate` on complex multi-step tasks |
| I-4 | [No Plan Branch Exploration on Failure](#i-4-no-plan-branch-exploration-on-failure) | 🟠 High | ❌ Not addressed | Tree of Thoughts with beam search at HLP level; LLM commonsense as branch heuristic; depth-limited pruning | HLP generates and scores multiple candidate plans; failed LLP attempts prune low-quality branches; reduces single-point-of-failure on the first generated plan |
| I-5 | [No Refinement Memory / RAG](#i-5-no-refinement-memory--rag) | 🟡 Medium | ❌ Not addressed (`use_vector_db` stub exists) | Episodic memory (SQLite + TF-IDF/dense RRF fusion); inject top-2 past successful PDDL pairs as few-shot examples into generation prompt | Repair prompts see relevant prior fixes; predicate naming errors stop recurring across runs; effectively zero-shot → few-shot for repeated domain types |
| I-6 | [Linear Plan Generation (no autoregressive state)](#i-6-linear-plan-generation-no-autoregressive-state) | 🟡 Medium | 🔄 Prototype in Alessio branch | Integrate step-by-step plan generation with intermediate state materialisation; order constraints by complexity (immediate first) | Each action step is conditioned on the state after previous actions; violated precondition errors (e.g. unstacking uncleared blocks) are caught before full plan is emitted |
| I-7 | [DFA-Based Verification Not Implemented](#i-7-dfa-based-verification-not-implemented) | 🟡 Medium | ❌ Not addressed (requires Spot) | Compile LTL formula to DFA once via Spot; step DFA through plan execution predicates directly | Eliminates fragile trace generation step and name-matching entirely; verification is exact and O(plan\_length); enables Elena's constrained subgoal decomposition per DFA transition |
| I-8 | [Fixed 2-Level Planning Depth](#i-8-fixed-2-level-planning-depth) | 🟢 Low / Long-term | ❌ Not addressed | N-level hierarchical decomposition; recursive agent delegation (HTN-inspired, per Nardi); caution: Iocchi flags HTN as impractical | Handles long-horizon tasks requiring more than one abstraction level; risk of complexity blowup — only pursue after I-3/I-4 feedback loop is stable |

---

## I-1: LTL Naming Drift — Layer 3 Pending

### Description
The LTL verifier always returns **VIOLATED** for correct plans because fluent names in the formula and trace don't match the PDDL ground truth. Root cause: `nl_description_generator.py` explicitly instructs the LLM to *paraphrase* object identifiers (e.g. `black_block_1` → "the black block number 1"), which propagates through the entire pipeline.

### Failure chain
```
nl file: "black_block_1"
  → nl_description_generator: "the black block number 1"   ← DRIFT SOURCE
    → formula_generator: invents "black_1"
      → trace_generator: mirrors "black_1" (correct internally)
        → trace_check: compares "black_1" vs PDDL "black_block_1" → VIOLATED ✗
```

### What's done (Layers 1 & 2)
- `formula_generator.py`: NAMING CONTRACT added — forces verbatim object names from input
- `trace_generator.py`: NAMING CONTRACT added to both `init_trace` and `trace_generation` prompts
- `planner_utils.py`: Layer 2 fuzzy predicate matching for env state sync

### What's pending (Layer 3)
**File:** `src/costl/planner/high/Planner/nl_description_generator.py`, line 36

Replace:
```
Important: Write naturally as a human would. Instead of technical names like "black_block_1", say "the black block number 1" or "the first black block". Make the physical constraints and limitations very clear and explicit in everyday language.
```
With:
```
Important: Write naturally as a human would for the Domain and Actions fields. Make the physical constraints and limitations very clear and explicit in everyday language.

CRITICAL — Object Identifier Rule: In the Problem, Goal, and Constraints fields you MUST preserve object identifiers EXACTLY as they appear in the input (e.g. "black_block_1", "orange_block_1"). Do NOT paraphrase them into natural language. These exact strings are required downstream for formal verification.
```

### Verification
```bash
cd /DATA/CoSTL
conda run --prefix /DATA/CoSTL/.conda_env python /tmp/test_ltl_fix.py
```
Expected: all 5 block identifiers appear verbatim in formula, `VERIFICATION: SATISFIED`.

### Scraped resource mapping
| Resource | Relevance |
|---|---|
| **Hands-On-LLM Ch6 — Prompt Engineering** ([Colab](https://colab.research.google.com/github/HandsOnLLM/Hands-On-Large-Language-Models/blob/main/chapter06/Chapter%206%20-%20Prompt%20Engineering.ipynb)) | Structured prompt design patterns — directly applicable to the CRITICAL rule injection in the system prompt |
| **OctoTools — Tool Cards** ([arxiv 2502.11271](https://arxiv.org/abs/2502.11271)) | Tool cards enforce input/output contracts per stage — analogous to a "naming contract" at each pipeline stage |
| **DeepLearning.AI Agentic KG** ([course](https://www.deeplearning.ai/short-courses/agentic-knowledge-graph-construction/)) | "Understanding User Intent" lesson shows how to extract and preserve structured entity names through agent stages |

---

## I-2: PDDL State Hallucination

### Description
During the low-level PDDL refinement loop, the LLM sometimes invents a simpler initial state to make an unsolvable problem appear solvable (e.g. asserting `(empty-hands)` when the robot is actually `(holding block_1)`). This causes the symbolic planner to find a plan that cannot be executed in the real simulator.

### Root cause
The PDDL problem's `:init` block is generated by the LLM without grounding to the simulator's actual state. Under repeated refinement pressure (VAL errors), the LLM "cheats" by simplifying the init state.

### What's done
`synchronize_environmental_state()` in `planner_utils.py` was implemented (Antigravity session, 2026-03-12):
- Extracts `:objects` and `:goal` from the LLM's PDDL
- Overwrites `:init` with the ground-truth simulator state
- Called before every planning attempt within the refinement loop
- Fuzzy-matches simulator predicates to domain predicates (6-priority chain)

Unit test `tests/test_state_sync.py` created and passing:
```
PRE-SYNC:  (:init (holding agent block_hallucination))
POST-SYNC: (:init (empty-hands agent))
```

### What's pending
- `src/costl/planner/low/planner.py` (Antigravity in-progress task): parse `pddl_init_state` string into a list of predicates at the start of `plan()`, before passing to `synchronize_environmental_state`
- Re-run Problem 102 (`BabyAI-MiniBossLevel-v0`) to confirm `:init` blocks in iteration/refinement PDDL files strictly match simulator output
- Verify benchmark results with `GT_success_rate` metric

### Scraped resource mapping
| Resource | Relevance |
|---|---|
| **Marktechpost — Self-Verifying DataOps Agent** ([code](https://github.com/Marktechpost/AI-Tutorial-Codes-Included/blob/main/AI%20Agents%20Codes/self_verifying_dataops_agent_local_hf_marktechpost.py)) | Automated planning → execution → verification cycle; pattern for injecting a verification gate after each state change |
| **Marktechpost — Critic-Augmented Risk-Aware Agent** ([notebook](https://github.com/Marktechpost/AI-Tutorial-Codes-Included/blob/main/Agentic%20AI%20Codes/critic_augmented_risk_aware_agent_Marktechpost.ipynb)) | Internal critic that flags inconsistent/risky intermediate states — applies to detecting init hallucinations before planning |
| **Marktechpost — Symbolic Guardrails + Reflexive Orchestration** ([notebook](https://github.com/Marktechpost/AI-Tutorial-Codes-Included/blob/main/AI%20Agents%20Codes/gemini_semantic_agent_orchestrator_Marktechpost.ipynb)) | Symbolic guardrails that block invalid transitions — can be adapted to enforce "no `:init` modification" constraints |
| **DeepLearning.AI Agentic KG — Schema Proposal Refinement** | Iterative schema loop with grounding checks mirrors the init-state synchronization loop: propose → validate against ground truth → accept/reject |

---

## I-3: Broken HLP→LLP Feedback Loop

### Description
When the Low-Level Planner fails to find a valid PDDL plan (after all 9 refinement attempts), there is no structured mechanism to feed that failure back to the High-Level Planner to revise the abstract plan. The pipeline either silently fails or reports the subgoal as failed with no recovery.

### Impact
- No adaptive recovery from LLP failures
- High-level plan cannot be revised based on what the low-level planner found infeasible
- Observed in benchmark results (low `GT_success_rate` on complex problems)

### Team signals
- Iocchi (LLM LTL, ID 293): "Inserire RL per generazione feedback"
- Alessio (LLM LTL, ID 330): "il trace check adesso possiamo tenerlo come opzionale ad alto livello. Nel senso che ci teniamo il primo piano generato e se fallisce a low level allora lo modifichiamo"
- Elena (LLM LTL, ID 393): constrained subgoal reformulation using DFA transitions

### Scraped resource mapping
| Resource | Relevance |
|---|---|
| **Marktechpost — Streaming Decision Agent with Online Replanning** ([code](https://github.com/Marktechpost/AI-Tutorial-Codes-Included/blob/main/Agentic%20AI%20Codes/streaming_decision_agent_online_replanning_marktechpost.py)) | Mid-execution replanning pattern — directly models what CoSTL needs: detect LLP failure mid-pipeline and trigger HLP re-generation |
| **Marktechpost — Reflexion Loops with LangGraph** ([notebook](https://github.com/Marktechpost/AI-Tutorial-Codes-Included/blob/main/Agentic%20AI%20Memory/agentic_ai_with_langgraph_adaptive_memory_reflexion_Marktechpost.ipynb)) | Reflexion architecture (Shinn et al.): agent reflects on failure, writes verbal feedback, re-plans — applicable as HLP re-prompting strategy |
| **Marktechpost — Peer-to-Peer Critic Loops** ([notebook](https://github.com/Marktechpost/AI-Tutorial-Codes-Included/blob/main/Agentic%20AI%20Codes/anemoi_semi_centralized_peer_critic_loop_langgraph_Marktechpost.ipynb)) | LLP acts as critic to HLP: LLP failure message becomes a structured critique that drives HLP revision |
| **OctoTools — Planner-Executor loop** ([tutorials](https://github.com/octotools/octotools/tree/main/tutorials)) | OctoTools's planner retries high-level steps when executor fails, with structured error context propagation |
| **AWS Agent Squad — SupervisorAgent** ([docs](https://awslabs.github.io/agent-squad/)) | Supervisor pattern: HLP acts as supervisor that receives structured failure reports from LLP (subordinate) and delegates replanning |

---

## I-4: No Plan Branch Exploration on Failure

### Description
The High-Level Planner generates a single plan (with up to 5 retry attempts using the same prompt). When the LLP fails, CoSTL has no mechanism to explore alternative high-level plan branches. Recovery is currently limited to retrying the same generation.

### Team signals
- Iocchi + Alessio (LLM LTL, IDs 293–294): "Tree of Thought potrebbe essere usato per esplorare diversi piani ad alto livello come alternative, qualora il basso livello dovesse fallire"
- Nardi (ID 293): "LLM commonsense come euristica per l'esplorazione dello spazio di soluzioni del problema di planning"

### Scraped resource mapping
| Resource | Relevance |
|---|---|
| **Marktechpost — Tree-of-Thoughts Multi-Branch Agent with Beam Search** ([code](https://github.com/Marktechpost/AI-Tutorial-Codes-Included/blob/main/Agentic%20AI%20Codes/tree_of_thoughts_multi_branch_reasoning_agent_marktechpost.py)) | ⭐ Direct implementation of Tree of Thoughts with beam search + heuristic scoring + depth-limited pruning — all of which apply to multi-branch HLP generation |
| **Marktechpost — CoT Pruning** ([notebook](https://github.com/Marktechpost/AI-Tutorial-Codes-Included/blob/main/Agentic%20AI%20Codes/agentic_chain_of_thought_pruning_dynamic_reasoning_Marktechpost.ipynb)) | Prune low-quality plan branches before sending to LLP — reduces wasted LLP calls |
| **Marktechpost — Cost-Aware Planning Agent** ([notebook](https://github.com/Marktechpost/AI-Tutorial-Codes-Included/blob/main/AI%20Agents%20Codes/cost_aware_planning_agent_budget_constrained_Marktechpost.ipynb)) | Budget-constrained branch selection — useful to cap the number of HLP branches explored per LLM call budget |
| **OctoTools — High-Level + Low-Level Planner** ([arxiv 2502.11271](https://arxiv.org/abs/2502.11271)) | OctoTools maintains a plan trajectory and can backtrack to a previous high-level step when the low-level executor fails — reference architecture |

---

## I-5: No Refinement Memory / RAG

### Description
Each PDDL refinement attempt starts from scratch with no memory of past corrections. When the LLM makes the same predicate naming error repeatedly across refinement rounds (a known pattern), there is no mechanism to inject examples of past successful fixes.

### Team signals
- Vincenzo (LLM LTL, ID 293): "RAG per migliorare il prompt con esempi di refinement del piano pregressi"
- Alessio (LLM LTL, ID 295): "RAG per fornire alcuni esempi few shot all'interno del prompt basandosi su tentativi che hanno avuto successo in passato"

### Scraped resource mapping
| Resource | Relevance |
|---|---|
| **Marktechpost — Production-Grade Agentic AI with Hybrid Retrieval + Repair Loops** ([notebook](https://github.com/Marktechpost/AI-Tutorial-Codes-Included/blob/main/Agentic%20AI%20Codes/Ultra_Agentic_AI_Hybrid_Retrieval_Guardrails_Episodic_Memory_Marktechpost.ipynb)) | ⭐ Episodic memory + repair loops: stores past successful executions, retrieves relevant ones at repair time — exact pattern for PDDL refinement RAG |
| **Marktechpost — Atomic-Agents RAG Pipeline with Dynamic Context Injection** ([notebook](https://github.com/Marktechpost/AI-Tutorial-Codes-Included/blob/main/Agentic%20AI%20Codes/atomic_agents_advanced_rag_pipeline_Marktechpost.ipynb)) | Dynamic context injection and agent chaining — applicable to injecting past PDDL fix examples at refinement time |
| **agents-towards-production — agent-RAG-with-Contextual** ([tutorial](https://github.com/NirDiamant/agents-towards-production)) | Production-ready RAG with Contextual AI: chunking, retrieval, re-ranking — infrastructure for building the refinement memory store |
| **agents-towards-production — Self-improving hybrid vector+graph memory (Mem0)** | Hybrid memory that improves from experience — applicable to storing PDDL corrections as a self-improving refinement KB |
| **DeepLearning.AI Agentic KG — Iterative Schema Refinement** | The "propose → refine" loop in knowledge graph construction mirrors the PDDL error → retrieve similar fix → refine loop |

---

## I-6: Linear Plan Generation (no autoregressive state)

### Description
The plan generator (`plan_generator.py`) generates all plan steps in a single LLM call. There is no intermediate state materialization between steps — the LLM has no explicit representation of what the world looks like after each action. This leads to plans with violated preconditions (e.g. unstacking a block that hasn't been cleared yet).

### Team signals
- Alessio (LLM LTL, ID 330): "il piano lo genera in maniera autoregressiva e si costruisce lo stato ad ogni step (è molto più lento ma dovrebbe essere più preciso)"
- Alessio (ID 330): "i constraint da risolvere vengono ordinati e risolti in ordine di complessità (prima quelli immediati, poi quelli con meno fluent ecc.)"
- Prototype exists in Alessio's branch (partially integrated)

### Scraped resource mapping
| Resource | Relevance |
|---|---|
| **Marktechpost — Hierarchical Planner AI Agent** ([code](https://github.com/Marktechpost/AI-Tutorial-Codes-Included/blob/main/AI%20Agents%20Codes/hierarchical_planner_ai_agent_open_source_llm_marktechpost.py)) | ⭐ Step-by-step plan construction with intermediate state tracking in a hierarchical agent — direct reference for autoregressive plan building |
| **Marktechpost — Multi-Agent Reasoning with Planning + Reflection** ([notebook](https://github.com/Marktechpost/AI-Tutorial-Codes-Included/blob/main/Agentic%20AI%20Memory/spacy_agentic_ai_system_Marktechpost.ipynb)) | Planning with memory and reflection between steps — models the intermediate state representation needed for autoregressive generation |
| **OctoTools — Executor structured context** ([tutorials](https://github.com/octotools/octotools/tree/main/tutorials)) | OctoTools executor saves each step's result to a structured context that the planner reads at the next step — reference for state accumulation between plan steps |
| **Hands-On-LLM Ch7 — Advanced Text Generation** ([Colab](https://colab.research.google.com/github/HandsOnLLM/Hands-On-Large-Language-Models/blob/main/chapter07/Chapter%207%20-%20Advanced%20Text%20Generation%20Techniques%20and%20Tools.ipynb)) | Tool-augmented generation and structured outputs — applicable to enforcing structured intermediate state at each generation step |

---

## I-7: DFA-Based Verification Not Implemented

### Description
The current LTL verification pipeline (trace_generator → trace_check → LTL_Verifier) requires: (1) generating a full trace via LLM, (2) exact name matching between formula and trace. Both steps are fragile. An alternative: compile the LTL formula to a DFA once (using Spot), then step the DFA through the plan execution to verify satisfaction — no trace generation needed, no name-matching required.

### Team signals
- Vincenzo (LLM LTL, ID 293): "Invece che passare per LTL, passare direttamente per l'automa"
- Elena (LLM LTL, ID 393): "il problema di constrained planning originale si trasforma in una sequenza di tanti constrained planning piccoli" — each DFA transition becomes a subgoal, itself a constrained planning problem
- Elena (ID 393): Fuggitti's LTL-to-PDDL tool exists for this

### Scraped resource mapping
| Resource | Relevance |
|---|---|
| **Marktechpost — Self-Verifying DataOps Agent** ([code](https://github.com/Marktechpost/AI-Tutorial-Codes-Included/blob/main/AI%20Agents%20Codes/self_verifying_dataops_agent_local_hf_marktechpost.py)) | Automated test generation + verification at each plan step — models the step-by-step DFA checking pattern |
| **Marktechpost — Neuro-Symbolic Hybrid Agent** ([notebook](https://github.com/Marktechpost/AI-Tutorial-Codes-Included/blob/main/AI%20Agents%20Codes/neuro_symbolic_hybrid_agent_Marktechpost.ipynb)) | ⭐ Combines logical (symbolic) planning with neural perception — closest available reference for integrating a DFA/automaton verifier into an LLM-based planning pipeline |
| **DeepLearning.AI Agentic KG — Architecture of Multi-Agent System** (Lesson 3) | The intent→structure→validate pipeline mirrors DFA-based: compile formula → extract transition structure → validate plan against automaton |

---

## I-8: Fixed 2-Level Planning Depth

### Description
CoSTL is hardcoded to exactly 2 planning levels (HLP → LLP). For complex long-horizon tasks, a single high-level abstraction is insufficient. Nardi suggested generalizing to N levels of arbitrary depth, similar to HTN (Hierarchical Task Network) planning.

### Team signals
- Nardi (LLM LTL, ID 293): "Livello del piano arbitrario (non solo 2 ma N livelli di profondità in base alla complessità del piano)"
- Nardi (ID 293): "Utilizzo terminologia HTN: paper Aiello"
- Iocchi (ID 293): "HTN è troppo teorico e non ha mai funzionato nella pratica" — caution flag

### Scraped resource mapping
| Resource | Relevance |
|---|---|
| **Marktechpost — Hierarchical Planner AI Agent** ([code](https://github.com/Marktechpost/AI-Tutorial-Codes-Included/blob/main/AI%20Agents%20Codes/hierarchical_planner_ai_agent_open_source_llm_marktechpost.py)) | ⭐ Reference implementation of a hierarchical planner with multiple layers — study this before designing N-level decomposition |
| **AWS Agent Squad — Agent-as-Tools + SupervisorAgent** ([docs](https://awslabs.github.io/agent-squad/)) | Recursive delegation pattern: supervisor spawns sub-agents that can themselves spawn sub-agents — maps to N-level plan decomposition |
| **OctoTools — High-Level + Low-Level Planner** | Two-level planner that could be stacked recursively; task-specific toolset optimization provides a model for level-specific tool selection |
| **Marktechpost — Multi-Agent with Planning, Critique, Persistent Memory (CAMEL)** ([notebook](https://github.com/Marktechpost/AI-Tutorial-Codes-Included/blob/main/AI%20Agents%20Codes/camel_multi_agent_research_pipeline_Marktechpost.ipynb)) | CAMEL role-playing framework: each level of the hierarchy can be modeled as a specialized agent role with defined input/output contracts |

---

## Resource Quick-Reference

| Resource | URL | Best for |
|---|---|---|
| **Marktechpost 100+ Notebooks** | github.com/Marktechpost/AI-Tutorial-Codes-Included | I-2, I-3, I-4, I-5, I-6, I-7 |
| **agents-towards-production** | github.com/NirDiamant/agents-towards-production | I-3, I-5 |
| **OctoTools** | github.com/octotools/octotools + arxiv 2502.11271 | I-3, I-4, I-6, I-8 |
| **AWS Agent Squad** | github.com/awslabs/multi-agent-orchestrator | I-3, I-8 |
| **Hands-On-LLM** | github.com/HandsOnLLM/Hands-On-Large-Language-Models | I-1, I-6 |
| **DeepLearning.AI Agentic KG** | deeplearning.ai/short-courses/agentic-knowledge-graph-construction | I-1, I-2, I-5, I-7 |

---

*I-1 Layer 3 is the single next code change (1 prompt edit). I-2 has 5 LLP fixes done (L-1,3,4,7,8); 4 remain (L-2,6,9,11) — see LLP_ISSUES.md for code-level detail. I-3 and I-4 are the next architectural priorities (feedback loop + branch exploration) before the system can recover from failures gracefully. I-5 (RAG) and L-13 are the same idea at different levels. I-7 is the highest-leverage refactor when Spot becomes available. I-8 is long-term research — do not pursue until I-3/I-4 are stable. See CHECKPOINT.md for full execution status.*
