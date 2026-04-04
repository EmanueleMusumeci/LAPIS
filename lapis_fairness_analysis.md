# LAPIS Fairness & Soundness Analysis

**Purpose**: Consolidated reference for strengthening the ICAPS 2026 System Demo submission.  
**Source**: Full critical review conducted April 4, 2026.

---

## 1. Pipeline Soundness: What Holds Up

### Oracle-Walled Evaluation (Strong)

The most rigorous element of the LAPIS evaluation is the strict separation between the LLM's working environment and the ground-truth oracle. During Conditions C and D, the ground-truth domain is never seen by the LLM. The refinement loop validates the plan against the LLM's *own* generated domain using VAL. Ground truth is used only as a post-hoc oracle to compute success rates. This prevents the LLM from "cheating" by pattern-matching against human-authored PDDL and ensures that reported success rates reflect genuine task completion, not syntactic mimicry.

### `:init` Lock Constraint (Sound but Minor)

Preventing the LLM from modifying the initial state during repair is a valid safeguard — it stops the model from hallucinating an easier starting world to sidestep a syntactic error. However, this is a single design choice, not a contribution. It should be mentioned in one clause, not a full paragraph.

### Ablation Structure (Well-Designed)

The experimental conditions (B, B', C, D) form a clean ablation ladder where each row adds exactly one variable. This lets readers isolate the contribution of each component by reading the delta between adjacent rows. The "fair baseline" B' (LLM+P with a generated domain but no refinement loop) is particularly valuable — it quantifies the catastrophic failure of single-shot synthesis and motivates the entire refinement architecture.

---

## 2. Pipeline Soundness: What Needs Attention

### The Semantic Correctness Gap (Critical Weakness)

The entire refinement loop operates on **syntactic** feedback. VAL checks whether the PDDL is well-formed, whether types match, whether predicates are declared. It does NOT check whether the domain actually models the intended physics. Planetarium (Zuo et al., NAACL 2025) showed that LLM-generated PDDL is ~96% syntactically parseable but only ~25% semantically correct. This means a domain can pass all of LAPIS's current validation checks while modeling completely wrong physics. The plan would be "valid" in the LLM's imagined world but would fail against the oracle — and the system has no mechanism to diagnose *why* it failed or to correct the domain model rather than just the syntax.

**Implication for the paper**: Without a semantic verification layer, LAPIS's refinement loop is fixing the wrong layer. It repairs syntax while the domain models the wrong world. This is the gap that the proposed semantic verifier (Path 2) addresses.

### Adequacy Check Relies on Self-Critique (Weak)

Condition D's Chain-of-Thought adequacy check asks the LLM to verify whether its own generated domain covers the task requirements. Kambhampati et al. (ICML 2024) argued that LLM self-verification without external sound verifiers is unreliable — the model tends to confirm its own output. The ICAPS community is moving toward external adequacy checks (NL2Plan's structured pipeline, Planning in the Dark's conformal prediction for schema ranking). The adequacy check is useful as a cheap pre-filter but should not be presented as a robust verification mechanism.

### Refinement Loop Cap at 3 Iterations (Arbitrary)

The 3-iteration cap is not justified. Why not 5? Why not 1? The optimal number likely varies by domain complexity. The paper should either report sensitivity analysis (how does success rate change with 1, 2, 3, 5 iterations?) or justify the choice empirically (e.g., "diminishing returns after iteration 3 across all domains").

---

## 3. Baseline Fairness: LLM+P Alone Is Insufficient

### The Problem with Comparing Only Against LLM+P

LLM+P (Liu et al., 2023) only generates problem files given a ground-truth domain. Comparing LAPIS (which generates both domain and problem, uses iterative refinement, and adds semantic verification) against a system that doesn't even attempt domain generation is an asymmetric comparison. This is the equivalent of benchmarking a self-driving car against cruise control.

ICAPS 2026 reviewers will expect positioning against the current state of the art in full NL-to-PDDL synthesis, which now includes NL2Plan (AAAI 2025), Planning in the Dark (AAAI 2025), ISR-LLM (ICRA 2024), and others.

### Condition B vs. Conditions C/D: Unfair Advantage for the Baseline

Comparing LAPIS/full (synthesized domain) against LLM+P (given GT domain) gives the baseline an unfair advantage — it starts with a perfect domain. The fact that LAPIS sometimes matches or exceeds LLM+P despite this handicap (e.g., 100% on `storage` vs. 85%) is impressive, but the comparison is structurally unbalanced. The paper should frame this correctly: "Even with a generated domain, LAPIS matches the ceiling set by systems that receive a human-authored domain."

### The Model Difference Between NL2Plan and LAPIS

NL2Plan uses GPT-4o; LAPIS uses Claude Sonnet 4.6. This is a potential confound but is scientifically defensible for three reasons:

1. Both are frontier-class models from the same capability tier.
2. NL2Plan was designed and optimized for OpenAI models — running it through an API proxy to route to Claude would introduce its own confounds (different tokenization, different tool-calling behavior).
3. The LLM+P baseline within LAPIS already uses Claude Sonnet 4.6, giving it the same "engine advantage." If LAPIS still outperforms LLM+P, the architecture matters more than the model.

The paper should state this explicitly: "Both systems use frontier-class models; the comparison evaluates architecture, not model capability."

---

## 4. Novelty Assessment: Component-by-Component

### Zero-Shot Schema Injection — Not Novel in 2026

Extracting a PDDL schema (types, predicates, constants) and injecting it into the problem generation prompt is deterministic parsing. The L2P toolkit (Tantakoun, Muise & Zhu, 2025) provides modular open-source tools for exactly this. PDDL-GenAI (ICAPS 2025 Demo) integrates similar mechanisms into an existing IDE. The "zero-shot vs. few-shot" distinction is real but incremental — it removes example dependence, which is nice, but TIC (Agarwal & Sreepathy, 2024) achieves near-perfect accuracy on all LLM+P domains using a completely different intermediate representation strategy.

### Full Domain + Problem Generation — Crowded Space

NL2Plan, Planning in the Dark, and Oswald et al. (ICAPS 2024) all generate full domain + problem PDDL from natural language. LAPIS's approach is not architecturally distinct from these systems in terms of what it does; the difference is in how it validates the result.

### VAL-Guided Iterative Refinement — Well-Trodden

ISR-LLM (ICRA 2024) introduced iterative self-refinement with external validator feedback. Mahdavi et al. (NeurIPS 2024) introduced Exploration Walk metrics for richer feedback. La Malfa et al. (December 2025) built a multi-agent architecture with iterative planner+validator feedback. LAPIS's specific variant (VAL logs → LLM fix → re-plan, capped at 3 iterations) is functionally equivalent to what ISR-LLM does.

### CoT Adequacy Check — Prompt Engineering, Not Architecture

The adequacy check is a prompt engineering technique (ask the LLM to self-assess coverage). It doesn't introduce a new verification mechanism and is vulnerable to the self-critique reliability problem documented by Kambhampati et al.

### Semantic Verification (Proposed) — Genuinely Novel

No existing system integrates semantic verification (structural analysis + NL round-trip checking) into an iterative PDDL refinement loop. The structural analyzer (predicate coverage, action reachability, type grounding) catches guaranteed-unsolvable problems that VAL approves because they're syntactically legal. The NL round-trip verifier is the first application of back-translation as a semantic verification mechanism for PDDL. This is the contribution that differentiates LAPIS from everything else in the landscape.

---

## 5. The Competitive Landscape (What Reviewers Will Know)

### Tier 1: Direct Competitors (Same Problem, Must Compare)

| System | Venue | Domain Gen | Refinement | Semantic Check | Code Available |
|--------|-------|-----------|------------|----------------|----------------|
| **NL2Plan** | AAAI 2025 | 6-step pipeline | Syntactic validation + optional LLM feedback | No | Yes (Docker) |
| **Planning in the Dark** | AAAI 2025 | Schema library + semantic ranking | Conformal prediction | No | Unknown |
| **ISR-LLM** | ICRA 2024 | No (GT domain) | VAL-guided iterative | No | Unknown |
| **La Malfa et al.** | arXiv Dec 2025 | Multi-agent | VAL + uVAL iterative | No | Unknown |
| **LAPIS** | This work | Zero-shot + schema injection | VAL + structural + NL round-trip | **Yes** | Yes |

### Tier 2: Alternative Paradigms (Cite, Don't Benchmark)

| System | Venue | Approach | Why Different |
|--------|-------|----------|---------------|
| TIC | arXiv 2024 | NL → ASP → PDDL | Requires GT domain |
| Thought of Search | NeurIPS 2024 | LLM generates search code | Not PDDL, generates Python |
| Corrêa et al. | NeurIPS 2025 | LLM generates heuristic code | Heuristic synthesis, not domain modeling |

### Tier 3: Theoretical / Survey (Frame, Don't Compare)

| Work | Venue | Role |
|------|-------|------|
| LLM-Modulo (Kambhampati et al.) | ICML 2024 | Theoretical justification for external verification |
| Planetarium (Zuo et al.) | NAACL 2025 | The semantic correctness gap finding LAPIS builds on |
| Text2World (Hu et al.) | ACL Findings 2025 | Domain generation benchmark |
| L2P Toolkit (Tantakoun et al.) | 2025 | Open-source tooling context |
| Vallati et al. | ICAPS 2025 | KE perspective on LLM limitations |

### Tier 4: Prior Demo Track (Differentiate)

PDDL-GenAI (Wang et al., ICAPS 2025 Demo) deployed an NL-to-PDDL pipeline as a plugin for editor.planning.domains. A reviewer who saw that demo will immediately ask "what does LAPIS add?" The answer must be: semantic verification and systematic ablation, not just another pipeline.

---

## 6. Data Contamination Concern

Tantakoun et al. (ACL Findings 2025) warn that IPC domains like Blocksworld and Logistics are almost certainly present in LLM training data, inflating reported results. This affects ALL systems equally (LAPIS, NL2Plan, baselines), so it doesn't bias the comparison, but it means absolute success rates should be interpreted cautiously. The paper should note this and point to the Lexicon Benchmark domains (which include some novel domains) as supporting evidence.

AutoPlanBench 2.0 (ICAPS 2025) found that natural language prompts yield better LLM performance than PDDL prompts. Since LAPIS uses NL input, this is in its favor — but it also means the baseline receives the same NL-prompt advantage.

---

## 7. What the Paper Must and Must Not Do

### Must Do

- Compare against NL2Plan as the primary full-synthesis competitor.
- Include a direct LLM-as-planner baseline to show the floor.
- Frame the experimental conditions as an ablation study (each row adds one component).
- Present the semantic verification layer as the primary novel contribution.
- Cite and differentiate from: LLM+P, NL2Plan, Planning in the Dark, ISR-LLM, Planetarium, LLM-Modulo, PDDL-GenAI.
- Note the model difference (GPT-4o vs. Claude Sonnet 4.6) and argue it evaluates architecture, not model.
- Acknowledge data contamination as a shared concern.

### Must Not Do

- Frame LAPIS as "better than LLM+P" — that comparison is too easy and tells reviewers nothing new.
- Spend space on model tradeoffs (Sonnet vs. Opus vs. GPT-5) — one sentence suffices.
- Present the `:init` locking or schema extraction as contributions — they are engineering choices.
- Claim novelty for the iterative refinement loop without the semantic layer — ISR-LLM got there first.
- Include all Lexicon Benchmark results in detail — they're supporting evidence, not the main story.

---

## 8. The Recommended Framing (One Paragraph)

"Recent NL-to-PDDL systems like NL2Plan and Planning in the Dark have shown that LLMs can generate both domain and problem files from natural language. However, all existing iterative refinement approaches validate only syntactic correctness: VAL checks whether the PDDL is well-formed, not whether the domain models the right physics. Planetarium demonstrated that this gap is enormous — 96% of LLM-generated PDDL parses correctly but only 25% is semantically correct. LAPIS addresses this with the first semantic verification layer integrated into an iterative synthesis loop: deterministic structural analysis catches guaranteed-unsolvable problems that pass VAL, and NL round-trip verification detects domain models that are syntactically valid but physically wrong. Our controlled ablation across five experimental conditions isolates the contribution of each pipeline component, and our Streamlit-based demo lets users visually inspect every stage of the synthesis process."
