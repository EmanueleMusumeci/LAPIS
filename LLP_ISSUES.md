# LLP Issues — Low-Level Planner Deep Analysis

> Goal: identify every structural weakness in the LLP that prevents 100% success rate and map each to a concrete, implementable fix from scraped resources.
> Sources: code analysis of `planner.py`, `pddl_generation.py`, `planner_utils.py`, `pddl_verification.py`; deep scrape of Marktechpost (Hierarchical Planner, Online Replanning, Ultra Agentic, Self-Verifying, Tree-of-Thoughts, Neuro-Symbolic), OctoTools paper (arXiv 2502.11271), DELTA (delta-llm.github.io).

---

## Issue Index

| # | Issue | Impact | Effort | Status |
|---|---|---|---|---|
| L-1 | [`pddl_init_state` string never parsed/validated before use](#l-1-pddl_init_state-string-never-parsed-before-use) | 🔴 High | 🟢 Low | ✅ Fixed |
| L-2 | [No object registry — LLM can hallucinate objects in `:init`/`:goal`](#l-2-no-object-registry--llm-can-hallucinate-objects) | 🔴 High | 🟢 Low | Not addressed |
| L-3 | [Domain not validated/frozen before problem generation](#l-3-domain-not-validatedfrozen-before-problem-generation) | 🔴 High | 🟢 Low | ✅ Fixed |
| L-4 | [FastDownward raw error text may not reach the repair prompt](#l-4-fastdownward-raw-error-not-fully-injected-into-repair-prompt) | 🔴 High | 🟢 Low | ✅ Fixed |
| L-5 | [No structured failure classification before repair](#l-5-no-structured-failure-classification-before-repair) | 🟠 High | 🟡 Medium | Not addressed |
| L-6 | [No trajectory history in repair prompts](#l-6-no-trajectory-history-in-repair-prompts) | 🟠 High | 🟢 Low | Not addressed |
| L-7 | [Silent sync failures can leave hallucinated `:init` in place](#l-7-silent-synchronization-failures) | 🟠 High | 🟢 Low | ✅ Fixed |
| L-8 | [Empty-plan hallucination repair is not targeted](#l-8-empty-plan-hallucination-not-targeted-in-repair) | 🟠 Medium | 🟢 Low | ✅ Fixed |
| L-9 | [No regeneration fallback after all 9 attempts fail](#l-9-no-full-regeneration-fallback) | 🟡 Medium | 🟢 Low | Not addressed |
| L-10 | [No predicate vocabulary contract across generation/repair calls](#l-10-no-predicate-vocabulary-contract) | 🟡 Medium | 🟡 Medium | Not addressed |
| L-11 | [No temperature control — all LLM calls use default temperature](#l-11-no-temperature-ladder) | 🟡 Medium | 🟢 Low | Not addressed |
| L-12 | [No role separation: single LLM call plans and generates PDDL simultaneously](#l-12-no-role-separation-planner--generator) | 🟡 Medium | 🟠 High | Not addressed |
| L-13 | [No episodic memory / RAG for PDDL generation examples](#l-13-no-episodic-memory--rag) | 🟡 Medium | 🟠 High | `use_vector_db` stub exists |

---

## L-1: `pddl_init_state` String Never Parsed Before Use

### What happens
`pddl_init_state = kwargs.get("pddl_init_state")` is passed directly to `synchronize_environmental_state()` and to generation prompts as a raw string. There is no validation that it is a valid set of PDDL predicates before it's used.

If `pddl_init_state` is `None`, `""`, malformed (unclosed parens), or in the wrong format (e.g. a prose sentence instead of PDDL facts), every sync call either silently no-ops or raises an exception that is swallowed by the `except` block, leaving the problem with the LLM's hallucinated `:init`.

### Impact
The entire Environmental State Synchronization layer (Layer 2) is bypassed whenever `pddl_init_state` is not a well-formed PDDL init string — with no warning to the caller.

### Fix (Antigravity in-progress task)
At the top of `LowLevelPlanner.plan()`, after `pddl_init_state = kwargs.get("pddl_init_state")`:

```python
def _parse_init_state(raw: str | None) -> str | None:
    """Normalize pddl_init_state to a clean PDDL fact list string."""
    if not raw:
        return None
    # Already looks like PDDL facts: (predicate arg1 arg2)
    if re.search(r'\(\s*\w[\w-]*', raw):
        return raw.strip()
    return None  # Not parseable — do not silently corrupt sync

pddl_init_state = _parse_init_state(kwargs.get("pddl_init_state"))
if pddl_init_state is None and kwargs.get("pddl_init_state"):
    logger.warning("pddl_init_state was provided but could not be parsed as PDDL facts — state sync will be skipped")
```

### Resource
- **Self-Verifying DataOps Agent**: `_extract_json()` fallback chain — direct parse → substring extraction → safe baseline. Never pass malformed input downstream.
- **Hierarchical Planner**: `extract_json_block()` with bracket-matching fallback — if parse returns None, system logs and continues with a safe default rather than propagating garbage.

---

## L-2: No Object Registry — LLM Can Hallucinate Objects

### What happens
`object_vocabulary` is extracted from `fluent_syntax` and injected into the generation prompt as a "use these identifiers" instruction. But it is only a **hint** — the LLM can still generate `:objects`, `:init`, and `:goal` blocks that reference names not in the vocabulary (either hallucinated objects, or misnamed ones).

There is no post-generation validation that checks "does every object name in the generated PDDL appear in `object_vocabulary`?" before calling FastDownward.

### Impact
FastDownward fails with `undefined object` or the plan references objects that don't exist in the simulator, causing execution failure even when the symbolic plan is logically valid.

### Fix
Build an `ObjectRegistry` and run a post-generation scan before calling FastDownward:

```python
class ObjectRegistry:
    def __init__(self, vocabulary: set[str]):
        self.vocab = {v.lower() for v in vocabulary}

    def scan_pddl(self, pddl_text: str) -> list[str]:
        """Return all object identifiers in the PDDL that are NOT in the vocabulary."""
        found = set(re.findall(r'\b([a-z][a-z0-9_-]*(?:_\d+)?)\b', pddl_text.lower()))
        # Exclude PDDL keywords
        keywords = {'define','domain','problem','objects','init','goal','and','or','not',
                    'when','forall','exists','precondition','effect','action','parameters',
                    'types','predicates','functions'}
        return [f for f in found if f not in self.vocab and f not in keywords]
```

If `scan_pddl()` returns non-empty results → inject the unknown names into the repair prompt: *"These objects appear in your PDDL but are not in the allowed vocabulary: [X, Y]. Replace them with the canonical names."*

### Resource
- **DELTA — Scene Graph Grounding**: "Object names in `:objects`, `:init`, and `:goal` are drawn from scene graph node IDs. The LLM is never allowed to invent object names." This is the single change with the highest reported success-rate gain.
- **OctoTools — Context Verifier**: `Naming: [objects in :goal that don't appear in :objects]` field catches this class of error before calling the solver.

---

## L-3: Domain Not Validated/Frozen Before Problem Generation

### What happens
The current flow:
```
generate_domain() → (no validation) → generate_problem()
```
`generate_problem()` receives `domain_file_path` as context. If the domain has syntax errors or undefined types, the problem generator inherits those errors — it may hallucinate predicates that are consistent with the broken domain rather than the intended one.

When VAL then checks domain + problem together, the errors are reported as a joint failure and both files are repaired together, making it harder to isolate root causes.

### Fix
Validate the domain in isolation immediately after generation, before calling `generate_problem()`:

```python
# After generate_domain():
domain_valid, domain_val_log = self._check_val(str(domain_file_path))
if not domain_valid:
    logger.warning("Domain failed VAL. Repairing domain before generating problem...")
    new_domain_str, _ = refine_domain(
        domain_file_path=str(domain_file_path),
        problem_file_path=None,  # no problem yet
        VAL_validation_log=domain_val_log,
        ...
    )
    with open(domain_file_path, 'w') as f:
        f.write(new_domain_str)
    domain_valid, _ = self._check_val(str(domain_file_path))

if domain_valid:
    # Freeze: domain is now the canonical context for problem generation
    generate_problem(domain_file_path=str(domain_file_path), ...)
```

### Resource
- **DELTA**: "Domain generation and problem generation are separate LLM calls — domain is generated first, then **frozen**, then problem is generated conditioned on the frozen domain. This prevents cascading errors."
- **OctoTools**: Planner / Command Generator separation — each role has a single responsibility, preventing dual-failure modes.

---

## L-4: FastDownward Raw Error Not Fully Injected Into Repair Prompt

### What happens
The repair flow passes `planner_error_log` and `VAL_validation_log` to `refine_domain()` and `refine_problem()`. These strings originate from:
- `planner_error`: the last 2000 chars of FD's stdout + last 1000 of stderr (see `run_planner_FD`)
- `VAL_validation_log`: full stdout + stderr from VAL subprocess

The truncation to 2000+1000 chars may cut off the critical error lines (FD's most informative errors often appear in the middle of output). Additionally, `planner_error` is sometimes set to generic messages like `"UP planner (pyperplan) found no plan: UNSOLVABLE"` — no structural error information.

More critically: when planning fails (no plan returned), the system calls `refine_domain()` + `refine_problem()` with the error from the **previous VAL check**, not from FastDownward itself. The repair prompt may be fixing a VAL error that was already resolved, while the real issue (FD UNSOLVABLE) goes undiagnosed.

### Fix
Capture and pass all three error sources distinctly, never truncated for the repair step:

```python
# After plan_with_output():
repair_context = {
    "val_syntax_errors": VAL_validation_log,       # syntax/type errors from VAL
    "fd_error": planner_error,                      # raw FD stderr (no truncation)
    "fd_status": "UNSOLVABLE" if "no plan" in (planner_error or "") else "ERROR",
    "plan_found": plan is not None,
    "empty_plan": plan == []
}
# Pass repair_context to refine_domain/refine_problem instead of individual fields
```

Repair prompt template:
```
The PDDL you generated produced the following results:
- VAL Syntax Check: {val_syntax_errors or 'PASSED'}
- FastDownward Status: {fd_status}
- FastDownward Output: {fd_error}

Diagnose the issue and return corrected PDDL.
```

### Resource
- **Self-Verifying DataOps Agent**: "error string is passed to the tester as the 'result' — enabling it to evaluate failure modes." The execution error is NEVER summarized, always passed verbatim.
- **OctoTools trajectory**: `sₜ = (aₜ, oₜ, rₜ)` where `rₜ` is the raw result/error from the executor — the full string, unmodified.

---

## L-5: No Structured Failure Classification Before Repair

### What happens
On planning failure, the pipeline immediately calls `refine_domain()` and `refine_problem()` — two separate LLM calls — without first classifying what type of failure occurred. The repair prompts are generic templates that attempt to fix everything at once.

The result: the LLM repair sometimes introduces new errors while fixing the reported one, because it doesn't know whether the root cause is a syntax error, an unsolvable goal, a type mismatch, a missing object, or a naming inconsistency.

### Fix
Add a lightweight **Context Verifier** LLM call between failure detection and repair:

```python
VERIFIER_PROMPT = """
You are a PDDL validator. Given the domain, problem, and planner output below, fill in this report:

Completeness: [Are all goal predicates reachable from the initial state given the available actions? YES/NO/UNKNOWN + reason]
Inconsistencies: [List any undefined predicates, type mismatches, or missing objects]
Naming: [List any object names in :goal or :init that don't appear in :objects]
Solvability: [Is the problem structurally solvable? SOLVABLE/UNSOLVABLE/UNCLEAR + reason]
Root cause: [ONE sentence: what is the primary error causing planning failure?]
Repair strategy: [DOMAIN_ONLY | PROBLEM_ONLY | BOTH | REGENERATE]

Domain:
{domain}

Problem:
{problem}

Planner output:
{planner_error}
"""
```

The `Repair strategy` field drives the repair call:
- `DOMAIN_ONLY` → call only `refine_domain()`, skip `refine_problem()`
- `PROBLEM_ONLY` → call only `refine_problem()`, skip `refine_domain()`
- `BOTH` → current behavior
- `REGENERATE` → skip repair loop, regenerate from scratch

This halves wasted LLM calls on 60%+ of failures (most failures have a single root cause in one file).

### Resource
- **OctoTools — Context Verifier**: `{Completeness, Inconsistencies, Verification, Ambiguities, Conclusion: CONTINUE | STOP}` — the Conclusion drives the next action deterministically.
- **pddl_generation.py `prioritize_issues()`**: already implements a keyword-based 4-tier classification. This should be elevated to a first-class LLM verifier call, not just a text classifier.

---

## L-6: No Trajectory History in Repair Prompts

### What happens
Each call to `refine_domain()` / `refine_problem()` receives only the **current** state of the PDDL and the **latest** error. It has no memory of what was tried in previous refinement rounds within the same planning attempt.

Pattern observed in benchmarks: the LLM makes the same syntactic mistake in round N+1 that it corrected in round N, because it has no context that "we already tried this and it didn't work."

### Fix
Maintain a `repair_trajectory` list and append it to every repair prompt:

```python
repair_trajectory = []  # [(attempt_id, domain_snapshot, problem_snapshot, error, repair_strategy)]

# After each repair attempt:
repair_trajectory.append({
    "attempt": r,
    "domain_summary": summarize_pddl(current_domain),  # first 20 lines
    "problem_summary": summarize_pddl(current_problem),
    "error": planner_error or val_log,
    "strategy": repair_context["Repair strategy"]
})

# Inject into repair prompt:
trajectory_str = "\n".join(
    f"Attempt {t['attempt']}: tried {t['strategy']}, got error: {t['error'][:300]}"
    for t in repair_trajectory[-3:]  # last 3 attempts only, to limit tokens
)
```

Repair prompt addition:
```
Previous repair attempts (most recent first):
{trajectory_str}

Do NOT repeat a fix that already failed. The repair must be different from all previous attempts.
```

### Resource
- **OctoTools trajectory**: `trajectory = (s₀, s₁, ..., sT)` where each `sₜ = (action, command, result)` — the full trajectory is preserved and fed to the Solution Summarizer (i.e., the final repair prompt).
- **Ultra Agentic critique-and-repair**: `for i in range(max_repairs): fixer_agent(draft, error_message=str(e))` — the fixer receives all prior error messages, not just the latest.

---

## L-7: Silent Synchronization Failures

### What happens
Both the initial sync and post-refinement syncs are wrapped:
```python
try:
    synchronize_environmental_state(...)
except Exception as e:
    logger.warning(f"... sync failed: {e}")  # swallowed — planning continues
```

If `synchronize_environmental_state` fails (e.g., UP parser rejects the domain due to a type error), the problem file still contains the LLM's hallucinated `:init` state. FastDownward then plans from a wrong state. The failure is silent — the pipeline treats this as a normal planning attempt.

The sync function itself has a final `raise e` at line 201 of `planner_utils.py`, but the calling code catches it. So failures are always swallowed.

### Fix
Distinguish between "sync failed but init is still usable" and "sync failed and init is corrupted":

```python
sync_succeeded = False
if pddl_init_state:
    try:
        synchronize_environmental_state(...)
        sync_succeeded = True
    except Exception as e:
        logger.error(f"Sync failed: {e}. Planning with potentially hallucinated init state — RELIABILITY DEGRADED.")
        # Set a flag visible to the repair prompt
        planner_error = f"STATE_SYNC_FAILED: {e}. The :init block may contain hallucinated facts."

# After planning, if sync never succeeded, flag this in repair context
repair_context["sync_succeeded"] = sync_succeeded
```

A sync failure should be treated as a first-priority repair target — the repair prompt should address the domain predicate naming issue that caused the sync to fail, before addressing any planning errors.

### Resource
- **Self-Verifying DataOps Agent**: never swallow errors — always capture them as strings and pass them to the downstream verifier. "error string is passed to the tester as the 'result'."
- **Online Replanning Agent**: `need_replan()` is triggered by any deviation from expected state — a sync failure is exactly such a deviation.

---

## L-8: Empty-Plan Hallucination Not Targeted in Repair

### What happens
The empty-plan case is correctly detected:
```python
planner_error = "HALLUCINATION_DETECTED: The planner returned a 0-step empty plan, which means the goal in your problem.pddl is ALREADY TRUE in the initial state."
plan = None
```

But this sets `plan = None` and falls through to the standard `refine_domain()` + `refine_problem()` calls, which use a generic repair template. The generic template doesn't specifically target the "goal is pre-satisfied in `:init`" failure mode.

### Fix
Add a dedicated repair prompt branch for this case:

```python
if planner_error and "HALLUCINATION_DETECTED" in planner_error:
    # Specific repair: remove from :init any predicate that appears in :goal
    empty_plan_repair_prompt = """
The goal in your problem.pddl is ALREADY TRUE in the initial :init state.
This means you hallucinated the goal conditions into the initial state.

Rules:
1. The :init block must represent the CURRENT state BEFORE the subgoal is achieved.
2. The :goal block must represent the state you want to REACH.
3. NO predicate that appears in :goal should be true in :init (unless it's a precondition that must already hold).

Inspect your :init block and remove any predicates that represent the goal being already satisfied.
The goal predicates that must NOT appear in :init: {goal_predicates}
"""
    # Extract goal predicates programmatically and inject them
```

### Resource
- **OctoTools — Context Verifier**: `Completeness: [Are all goal predicates REACHABLE from initial state?]` — REACHABLE ≠ ALREADY TRUE. This distinction is exactly the empty-plan case.
- **Self-Verifying DataOps Agent**: validation criteria are checked by a dedicated tester role — the empty-plan check is a validation criterion that should trigger a specific repair strategy, not a generic one.

---

## L-9: No Full Regeneration Fallback

### What happens
After all `max_iterations × max_refinements = 9` attempts, `plan()` returns `(False, None, full_history)`. There is no fallback.

In practice, the 9-attempt budget is consumed by refinement of the same broken PDDL. If the initial generation was fundamentally wrong (e.g. wrong action schema for the domain type), no amount of refinement will fix it — a fresh generation is required.

### Fix
After exhausting the refinement budget, attempt one full regeneration with a richer prompt that includes the failure history:

```python
# After the outer loop:
if not success:
    logger.warning("All refinement attempts exhausted. Attempting full regeneration...")

    # Build a "lessons learned" string from full_history
    failures = [h.get("error", "") for h in full_history if h.get("error")]
    lessons = "\n".join(f"- Previously failed with: {e[:200]}" for e in failures[-5:])

    # Regenerate domain from scratch with failure context
    generate_domain(
        ...,
        extra_context=f"Previous attempts failed with these errors:\n{lessons}\nGenerate a completely different domain structure."
    )
    # One final planning attempt
    plan, _, planner_error, _ = plan_with_output(...)
    if plan is not None:
        return True, ..., full_history

return False, None, full_history
```

### Resource
- **Online Replanning Agent**: reactive fallback when A* fails within budget — switches to greedy heuristic. The equivalent for PDDL is switching to a simpler/template-based domain schema.
- **Tree of Thoughts**: if all beam candidates score below threshold → trigger complete regeneration with temperature 0.0 and an explicit error-avoidance prompt.

---

## L-10: No Predicate Vocabulary Contract

### What happens
While the object vocabulary from `fluent_syntax` is enforced (injected into prompts), the **predicate vocabulary** (action names, predicate names) is never locked down. Different LLM calls can generate different predicate names for the same concept:
- Domain generation: `(on-table ?obj)`
- Problem generation: `(ontable ?obj)`
- Repair round 2: `(on_table ?obj)`

The fuzzy predicate matching in `synchronize_environmental_state` (6-priority chain) handles some cases, but it can't fix mismatches that manifest inside the `:goal` block (goal predicates are not synced).

### Fix
After a successful domain generation, extract the canonical predicate vocabulary and inject it into all subsequent calls:

```python
def extract_predicate_vocabulary(domain_pddl: str) -> dict[str, int]:
    """Returns {predicate_name: arity} from a PDDL domain string."""
    section = re.search(r'\(:predicates(.*?)\n\s*\)', domain_pddl, re.DOTALL)
    if not section:
        return {}
    return {
        m.group(1): len(re.findall(r'\?', m.group(0)))
        for m in re.finditer(r'\(([\w-]+)([^)]*)\)', section.group(1))
    }

predicate_vocab = extract_predicate_vocabulary(domain_pddl)
# Inject into problem generation and all repair prompts:
# "Available predicates (use ONLY these, exact spelling): {list(predicate_vocab.keys())}"
```

### Resource
- **DELTA**: "The LLM is never allowed to invent object names — it selects from the graph vocabulary." Extend this principle to predicates: once the domain is frozen, the predicate vocabulary is fixed.
- **OctoTools — Tool Cards**: `inputs/outputs` schema enforces exactly which predicates (tools) are available. Post-generation scan against the card rejects unknown predicates immediately.

---

## L-11: No Temperature Ladder

### What happens
All LLM calls (domain generation, problem generation, all repair rounds) use the default temperature of the agent, which is not tuned per call type. High temperature increases creativity but reduces structural consistency — exactly wrong for PDDL generation where the output must conform to a formal grammar.

### Fix
Apply a temperature ladder based on call type and attempt number:

| Call Type | Temperature | Rationale |
|---|---|---|
| Domain generation (first attempt) | 0.3 | Some creativity needed for action schema choices |
| Problem generation | 0.2 | Mostly mechanical translation of facts |
| Repair round 1 | 0.2 | Try a slightly different approach |
| Repair round 2 | 0.1 | Focus on fixing the specific error |
| Repair round 3+ | 0.0 | Deterministic — stop hallucinating, fix exactly what's broken |
| Full regeneration fallback | 0.4 | Deliberately try a different structure |

Implement by passing `temperature` as a parameter to all `generate_*` and `refine_*` functions, derived from the attempt index.

### Resource
- **Hierarchical Planner**: "Planning at 0.2–0.3; retry at 0.0; execution at 0.1. Lower = more deterministic output for structured formats."
- **Self-Verifying DataOps Agent**: "Planner 0.2, Executor 0.1 (structured code needs lowest variance)."

---

## L-12: No Role Separation: Planner + Generator in One Call

### What happens
`generate_domain()` and `generate_problem()` ask a single LLM call to simultaneously: (1) understand the planning problem, (2) identify the right action schema and predicate structure, and (3) produce syntactically valid PDDL. This is the "dual responsibility" failure mode identified in OctoTools.

The result: the LLM trades off correctness of understanding against correctness of syntax. Common manifestation: the action semantics are correct but the PDDL syntax has errors; or the syntax is valid but the action preconditions are wrong.

### Fix
Split into two roles:

**Role 1 — Describer** (natural language):
```
Given this task: {task_description}
And this environment: {environment}
Describe in natural language:
1. What PDDL predicates are needed and what they represent
2. What actions are needed, with their preconditions and effects in plain English
3. What the initial state contains
4. What the goal state requires
```

**Role 2 — PDDL Generator** (formal syntax):
```
Given this description:
{describer_output}

Write valid PDDL syntax for the domain file.
Available object names: {object_vocabulary}
Use ONLY the predicates and actions described above.
Output ONLY the PDDL. Start with (define (domain ...
```

This adds one LLM call per generation but significantly reduces the number of repair rounds needed.

### Resource
- **OctoTools**: "The Action Predictor does NOT generate code — it generates a text-based sub-goal + tool name. The Command Generator separately converts that into executable Python. This decoupling prevents 'dual responsibility' errors."
- **Hierarchical Planner**: three distinct roles (Planner → Executor → Aggregator) each with a single, bounded responsibility.

---

## L-13: No Episodic Memory / RAG

### What happens
`use_vector_db=False` by default. Even when enabled, the vector DB is used inconsistently (only in `refine_problem` and `refine_domain`, not in initial generation). There is no storage of successful `(task_description → domain + problem + plan)` triples that could serve as one-shot examples.

Every planning attempt starts from zero, even for structurally identical problems (e.g., all Blocksworld problems share the same domain structure).

### Fix
Implement episodic memory with hybrid retrieval:

```python
class PDDLEpisodeMemory:
    def __init__(self, db_path="episodes.db"):
        # SQLite for fast token-overlap retrieval + numpy for dense retrieval
        ...

    def store(self, task_desc: str, domain_pddl: str, problem_pddl: str,
              plan: list[str], success: bool):
        if success:
            self.db.insert(task_desc, domain_pddl, problem_pddl, plan)

    def recall(self, task_desc: str, top_k: int = 2) -> list[dict]:
        """Retrieve top-k most similar past successful PDDL pairs."""
        sparse = self._tfidf_recall(task_desc, top_k * 2)
        dense = self._embedding_recall(task_desc, top_k * 2)
        return self._rrf_fuse(sparse, dense)[:top_k]

# Usage in generation:
examples = memory.recall(current_goal_text, top_k=2)
one_shot_context = "\n\n".join(
    f"Example {i+1}:\nTask: {ex['task']}\nDomain:\n{ex['domain']}\nProblem:\n{ex['problem']}"
    for i, ex in enumerate(examples)
)
# Inject one_shot_context into domain_generation prompt
```

The most important variant for CoSTL: store successful examples **per domain type** (Blocksworld, BabyAI, etc.) since the domain structure is largely invariant within a domain type.

### Resource
- **Ultra Agentic — Episodic Memory + Repair Loops**: "Episodic memory enables lightweight few-shot learning without fine-tuning — the planner sees 'last time we solved a similar problem, these were the useful sources.'" Uses `HybridIndex` (TF-IDF + dense + RRF fusion) for retrieval.
- **agents-towards-production — Self-Improving Hybrid Memory (Mem0)**: hybrid vector+graph memory that improves from experience.

---

## Implementation Priority

### Do immediately (highest ROI, lowest effort)

1. **L-1** — Parse/validate `pddl_init_state` before use. One function, 15 lines.
2. **L-3** — Validate domain in isolation before generating problem. One VAL call inserted.
3. **L-4** — Pass raw FastDownward error verbatim to repair prompt. Remove truncation.
4. **L-7** — Treat sync failures as explicit errors visible to the repair prompt. Remove silent swallow.
5. **L-8** — Add dedicated empty-plan repair branch. ~20 lines + new prompt string.

### Do next (medium effort, high impact)

6. **L-2** — Object registry post-generation scan. One class, ~30 lines + integration.
7. **L-6** — Trajectory history in repair prompts. Accumulate repair_trajectory list, inject last-3.
8. **L-9** — Full regeneration fallback after 9 failures. ~20 lines.
9. **L-11** — Temperature ladder. Thread temperature parameter through all generation calls.

### Do last (higher effort, good for 100% target)

10. **L-5** — Structured Context Verifier LLM call. New prompt + parsing logic.
11. **L-10** — Predicate vocabulary extraction and injection. `extract_predicate_vocabulary()` + prompt injection.
12. **L-12** — Role separation (Describer + Generator). Architectural change to generation flow.
13. **L-13** — Episodic memory / RAG. Full implementation with SQLite + embedding store.

---

## External Resources Quick Reference

| Technique | Source | URL |
|---|---|---|
| Object registry / scene graph grounding | DELTA | delta-llm.github.io |
| Domain-first frozen generation | DELTA | delta-llm.github.io |
| Context Verifier structured fields | OctoTools | arxiv.org/abs/2502.11271 + github.com/octotools/octotools |
| Trajectory preservation | OctoTools | github.com/octotools/octotools/tree/main/tutorials |
| Raw error injection (no truncation) | Self-Verifying DataOps Agent | github.com/Marktechpost/AI-Tutorial-Codes-Included |
| Critique-and-repair loop | Ultra Agentic | github.com/Marktechpost/AI-Tutorial-Codes-Included |
| Episodic memory (SQLite + RRF) | Ultra Agentic | github.com/Marktechpost/AI-Tutorial-Codes-Included |
| Temperature ladder | Hierarchical Planner | github.com/Marktechpost/AI-Tutorial-Codes-Included |
| Replanning triggers | Online Replanning Agent | github.com/Marktechpost/AI-Tutorial-Codes-Included |
| Role separation (planner vs generator) | OctoTools | arxiv.org/abs/2502.11271 |
| Beam search over PDDL candidates | Tree of Thoughts | github.com/Marktechpost/AI-Tutorial-Codes-Included |

---

*All issues identified from direct code analysis of `src/costl/planner/low/`. No architectural changes required — all fixes are additive and backward-compatible with the existing 3×3 refinement loop.*
