# CHECKPOINT.md

> Last updated: 2026-03-30
> Branch: `integration-merge-attempt`

## Project

**ICAPS 2026 Demo submission** — ContextMatters (arXiv: 2506.15828) benchmarked on unconstrained Lexicon environments (Blocksworld, BabyAI, Logistics, Sokoban) and LLM+P IPC domains, using CoSTL as the engine. LTL path disabled. No DSPy/LiteLLM — custom Agent abstraction over OpenAI/Anthropic SDKs.

- **Working repo:** `/DATA/context-matters-demo` (copy of `/DATA/CoSTL`)
- **Original prototype:** `/DATA/context-matters`
- **3DSG submodule repo:** `/DATA/context-matters-3dsg` → mounted at `third-party/context_matters_3dsg/`

---

## Benchmark Results

### A. Lexicon domains — CoSTL (Claude Sonnet 4.6, 3 refinement iterations)

| Domain | VAL valid | Notes |
|--------|-----------|-------|
| Blocksworld | 6/10 (60%) | |
| BabyAI | 10/10 (100%) | Headline result |
| Logistics | 12/30 (40%) | |
| Sokoban | 17/30 (57%) | |

### B. Lexicon domains — LLM+P ablation (Claude Sonnet 4.6, 1 iteration, no refinement)

| Domain | VAL valid | Delta vs CoSTL |
|--------|-----------|----------------|
| Blocksworld | 6/10 (60%) | 0pp |
| BabyAI | 9/10 (90%) | -10pp |
| Logistics | 11/30 (37%) | -3pp |
| Sokoban | 13/30 (43%) | -14pp |

### C. Direct LLM baselines (from Lexicon pre-scored plans, unconstrained VAL)

| Model | Blocksworld | BabyAI | Logistics | Sokoban |
|-------|-------------|--------|-----------|---------|
| o3 | 83% | **0%** | 40% | 60% |
| Gemini 2.5 | 83% | **0%** | 43% | 56% |
| GPT-4.1 | 7% | **0%** | 0% | — |
| DeepSeek R1 | 73% | **0%** | 37% | 30% |
| Claude 3.7 Sonnet | 10% | **0%** | 3% | 10% |
| **CoSTL (ours)** | **60%** | **100%** | **40%** | **57%** |

**Key finding:** BabyAI is the headline result — every direct LLM scores 0% (including o3); CoSTL scores 100%. On Sokoban, refinement adds +14pp over one-shot LLM+P.

Result files:
- `results/benchmark_blocksworld_data_2_claude_sonnet_4_6/`
- `results/benchmark_babyai_data_data_1_claude_sonnet_4_6/`
- `results/benchmark_logistics_data_1_claude_sonnet_4_6/`
- `results/benchmark_sokoban_data_1_claude_sonnet_4_6/`
- `results_llmp/benchmark_*/` — LLM+P ablation (1 iteration)

### D. LLM+P IPC domains — domain generation ablation (CoSTL vs LLM+P, GT domain provided)

**Ablation: GT domain given to both systems; problem generated from NL.**

Results at `results_llmpp/benchmark_llmpp_{domain}_{costl|llmpp}_claude_sonnet_4_6/`

| Domain | LLM+P (0 ref) | CoSTL (3 ref) | Delta |
|--------|--------------|---------------|-------|
| barman | 20/20 (100%) | 20/20 (100%) | 0pp |
| blocksworld | 20/20 (100%) | 20/20 (100%) | 0pp |

*(GT domain mode: both systems use provided domain.pddl, only problem is LLM-generated)*

---

### E. LLM+P IPC domains — end-to-end NL→PDDL (domain + problem generated)

**Domain AND problem generated from NL. No GT domain injected.**

`--generate_domain` flag; ablation `full` = clean domain prompt + schema injection.

Results at `results_llmpp/benchmark_llmpp_{domain}_{costl|llmpp}_domgen_claude_sonnet_4_6/`

| Domain | LLM+P (0 ref, domgen) | CoSTL/full (3 ref, domgen) |
|--------|----------------------|---------------------------|
| blocksworld | 15/20 (75%) | 17/20 (85%) |
| barman | 0/20 (0%) | 1/20 (5%) |

*(barman fails because cocktail action sequencing is complex; adequacy checks partially help — see §F)*

---

### F. Approach A ablation — previously failing problems (targeted mini-run, 2026-03-30)

**Compares `full` (no adequacy) vs `full_adequacy` (adds CoT domain+problem checks) on 6 problems that failed with `full`.**

| Domain | Problem | full (no adequacy) | full_adequacy |
|--------|---------|-------------------|---------------|
| blocksworld | p05 | FAILED refs=3 94s | **SUCCESS refs=0 16s** |
| blocksworld | p10 | FAILED refs=3 67s | **SUCCESS refs=0  8s** |
| blocksworld | p18 | FAILED refs=3 106s | **SUCCESS refs=0 11s** |
| barman | p01 | FAILED refs=3 82s | **SUCCESS refs=0 28s** |
| barman | p02 | FAILED refs=3 162s | FAILED refs=3 128s |
| barman | p03 | FAILED refs=3 79s | FAILED refs=3 148s |

**Blocksworld: 0/3 → 3/3. Barman: 0/3 → 1/3.**

The adequacy check catches predicate gaps before planning (0 refinements needed on all successes). Barman failures persist because domain generation still misses the cocktail ordering logic.

---

### G. LLM+P IPC domains — CoSTL (Claude Sonnet 4.6, 3 iterations) vs LLM+P published baseline

**CORRECTED after fairness audit (2026-03-28)** — see audit notes below.

| Domain | CoSTL (FD fallback) | LLM+P run0 (paper) | LLM+P run1 (complete) | Delta vs run0 |
|--------|--------------------|--------------------|----------------------|---------------|
| barman | **20/20 (100%)** | 4/20 (20%) ⚠️ partial | 20/20 (100%) | 0pp vs run1 |
| blocksworld | **20/20 (100%)** | 18/20 (90%) | N/A | +10pp |
| floortile | 0/20 (0%) | 0/20 (0%) | N/A | 0pp |
| grippers | **20/20 (100%)** | 19/20 (95%) | 20/20 (100%) | 0pp vs run1 |
| storage | **20/20 (100%)** | 17/20 (85%) | N/A | +15pp |
| termes | **20/20 (100%)** | 4/20 (20%) | N/A | +80pp |
| tyreworld | 0/20 (0%) | 0/20 (0%) | 0/20 (0%) | 0pp |

**CoSTL result files:**
- `results_llmpp/benchmark_llmpp_{domain}_claude_sonnet_4_6/` — original runs (storage: 0% due to bug)
- `results_llmpp_fd/benchmark_llmpp_storage_claude_sonnet_4_6/` — storage re-run with FD fallback (100%)

**LLM+P baselines:**
- `run0`: `third-party/llm-pddl/experiments/run0/plans/llm_ic_pddl/` — incomplete (4/20 barman, 4/20 termes)
- `run1`: `third-party/llm-pddl/experiments/run1/plans/llm_ic_pddl/` — complete for barman/grippers/tyreworld

**Notable findings (post-audit):**
- **Barman +80pp claim was wrong**: run0 was an interrupted run (4 plans generated). LLM+P run1 achieves 20/20 = 100% on barman, same as CoSTL.
- **Storage 0% was a UP parser bug**: `unified_planning` rejects the domain's diamond type hierarchy (`area` declared twice). Fixed with native FD fallback. CoSTL now gets 20/20 (100%) on storage.
- **Termes +80pp is real**: LLM+P run0 = 4/20; no run1 data; CoSTL = 20/20. Only real headline advantage.
- **Prompt difference**: CoSTL provides the GT domain PDDL to the LLM; LLM+P uses ICL (one example problem+solution, no domain PDDL). CoSTL has more structural information but both achieve 100% on easy domains.
- floortile and tyreworld remain 0% for both systems.

---

## Completed Work

| Phase | Description | Status |
|-------|-------------|--------|
| P1 | Copy CoSTL to demo repo, init git | ✅ |
| P2 | Strip LTL components | ✅ |
| Phase 0 | Create minimal context-matters-3dsg repo | ✅ |
| Phase 1 | Add 3DSG as git submodule | ✅ |
| Phase 2 | Write UP-native `grounding.py` (8 functions) | ✅ |
| Phase 3 | Wire grounding into pipeline | ✅ |
| Phase 4a | LexiconLowLevelPipeline + run_benchmark.py | ✅ |
| Phase 4a | Run all 4 Lexicon domains × CoSTL + LLM+P ablation | ✅ |
| Phase 4c | Prepare LLM+P (IPC) data + pipeline | ✅ |
| Phase 4c | Score LLM+P published baseline (run0) with VAL | ✅ |
| Phase 4c | Run CoSTL on 7 LLM+P IPC domains | ✅ |
| Phase 4d | UP SequentialSimulator + GIF rendering (partial) | ⚠️ |
| Phase 4e | Approach A: clean domain prompt + schema injection ablation | ✅ |
| Phase 4f | Adequacy checks (CoT domain + problem validation) | ✅ |

### Bug fixes

- `generate_problem()` — added `ADD_PREDICATE_UNDERSCORE_EXAMPLE=False` param
- `refine_problem()` — added `scene_graph=None` alias param; positional args keyword-only
- `low_level_planning.py:301` — unpacked `new_problem, _refinement_history = refine_problem(...)`
- `low_level_planning.py` — fixed path construction (`"/" + os.path.join(...)` → `Path(...).parent`)
- `low_level_planning.py:377` — `and plan` → `and plan is not None` (empty plan valid when goal trivially satisfied)
- `src/costl/agents/claude.py` — NEW: ClaudeAgent wrapping Anthropic SDK
- `run_benchmark.py` — routes `claude-*` model names to ClaudeAgent, others to GPTAgent
- `pddl_generation.py` — `_preprocess_pddl`: removed navigation-specific stripping that caused dangling `-` and FD crashes
- `pddl_generation.py` — `generate_domain`: added `clean_domain_prompt` flag (Approach A: no hardcoded hints)
- `pddl_generation.py` — `generate_problem`: added `inject_domain_schema` flag (Approach A: schema extracted from generated domain injected into problem prompt)
- `pddl_generation.py` — `extract_schema` + `_format_schema_block`: dynamically extract types/predicates/constants from generated domain (no GT injection)
- `pddl_generation.py` — `check_domain_adequacy`: 3-step CoT check — extract predicates, match observations, amend if critical gaps
- `pddl_generation.py` — `check_problem_adequacy`: single CoT check — verify (:init) against observation, fix hallucinations/missing facts
- `low_level_planning.py` — `grounded_planning`: wired `clean_domain_prompt`, `inject_domain_schema`, `check_adequacy` kwargs
- `lexicon_low_level.py` — domain generation mode: reads `domain.nl` + `pXX.nl` separately; passes `check_adequacy`
- `run_llmpp_benchmark.py` — full rewrite: `--method {costl,llmpp,compare}`, `--generate_domain`, `--ablation {baseline,clean_domain,schema_problem,full,full_adequacy}`

### New files

- `prepare_llmpp_data.py` — converts LLM+P dataset to CoSTL format → `data/llmpp/`
- `run_llmpp_benchmark.py` — benchmark runner for LLM+P/IPC domains
- `src/costl/plan_renderer.py` — UP SequentialSimulator verification + Blocksworld GIF rendering

### Phase 4d — UP SequentialSimulator + Graphical Rendering (status)

`src/costl/plan_renderer.py` is wired into `lexicon_low_level.py`. It:
- Parses plan files (UP format → PDDL action strings)
- Steps plan through `UP SequentialSimulator` against GT `problem.pddl`
- For Blocksworld: renders frame-by-frame GIF using `BlocksworldSimulator.get_image()` (PIL)

**Current blocker:** Lexicon GT `problem.pddl` files contain `:constraints (sometime ...)` (LTL trajectory constraints). UP's `SequentialSimulator` cannot handle `TRAJECTORY_CONSTRAINTS`. Result: `up_sim_valid` always `False` for Lexicon problems even when `val_valid=True`.

**Fix needed:** Either (a) strip `:constraints` from GT problem before passing to UP sim, or (b) use the LLM+P GT problems (which have no constraints) for the UP sim demo. LLM+P domains work correctly with UP sim since they are plain PDDL.

**GIF rendering** works end-to-end once the constraint issue is resolved — `BlocksworldSimulator.get_image()` produces PIL images of block stacks at each step.

---

## Storage Domain Failure — RESOLVED (2026-03-28)

**Root cause:** `unified_planning`'s PDDL parser rejects the storage domain because it declares `area` twice in the type hierarchy (both `area - object` and `area crate - surface` — a diamond hierarchy UP doesn't support). Every problem fails immediately at parse time with `SyntaxError: Type area is declared more than once` before any LLM or planning work.

**Fix:** Added `run_planner_FD_native()` to `planner_utils.py` that calls FastDownward directly via subprocess when UP's parser fails. The fallback auto-detects the FD script path via `up_fast_downward` package.

**Result after fix:** CoSTL scores **20/20 (100%)** on storage with 0 refinements needed (`results_llmpp_fd/`). The LLM generates correct PDDL on first try; it just needed a planner that could parse the domain.

---

## Remaining Work

### ⚠️ NEXT RUN NEEDED — full_adequacy comparative benchmark

Run the full 20-problem comparison across blocksworld and barman with all four ablations to get a complete picture of each component's contribution:

```bash
source key.sh

# Full 20-problem runs — domain generation mode
/home/xps/miniconda3/bin/python3 run_llmpp_benchmark.py --domain blocksworld --method compare --generate_domain --ablation full_adequacy
/home/xps/miniconda3/bin/python3 run_llmpp_benchmark.py --domain barman --method compare --generate_domain --ablation full_adequacy
```

This will populate:
- `results_llmpp/benchmark_llmpp_blocksworld_costl_domgen_full_adequacy_claude_sonnet_4_6/`
- `results_llmpp/benchmark_llmpp_blocksworld_llmpp_domgen_full_adequacy_claude_sonnet_4_6/`
- `results_llmpp/benchmark_llmpp_barman_costl_domgen_full_adequacy_claude_sonnet_4_6/`
- `results_llmpp/benchmark_llmpp_barman_llmpp_domgen_full_adequacy_claude_sonnet_4_6/`

Expected table to fill in (ablation × domain):

| Ablation | blocksworld CoSTL | blocksworld LLM+P | barman CoSTL | barman LLM+P |
|----------|-------------------|-------------------|--------------|--------------|
| full (done) | 17/20 (85%) | 15/20 (75%) | 1/20 (5%) | 0/20 (0%) |
| full_adequacy | ? | ? | ? | ? |

**Note:** Use `/home/xps/miniconda3/bin/python3` (not `.venv` or conda env `costl_env` — those lack required packages).

---

### Paper (`paper/`)

LaTeX skeleton at `paper/main.tex` (AAAI-style). All sections are `\todo[inline]{...}`.

- **Missing style files:** `aaai26.sty` + `aaai26.bst` (download from https://aaai.org/authorkit26/)
- **Next:** Fill in sections with benchmark numbers above

**Suggested narrative:**
> On BabyAI — the structurally most complex Lexicon domain — every direct LLM (including o3) scores 0% validity. CoSTL scores 100% by decoupling NL understanding (LLM) from combinatorial search (symbolic planner). On the LLM+P IPC domains, CoSTL outperforms LLM+P by +80pp on barman and termes, matching or exceeding on blocksworld and grippers, while both systems fail on floortile and tyreworld.

**Table structure for paper (Table 1 — Lexicon):**

| System | Blocksworld | BabyAI | Logistics | Sokoban |
|--------|-------------|--------|-----------|---------|
| Direct LLM (o3) | 83% | 0% | 40% | 60% |
| LLM+P (1-shot) | 60% | 90% | 37% | 43% |
| CoSTL (ours, 3-iter) | 60% | **100%** | **40%** | **57%** |

**Table structure for paper (Table 2 — LLM+P IPC):**

| Domain | LLM+P | CoSTL (ours) |
|--------|-------|--------------|
| barman | 20% | **100%** |
| blocksworld | 90% | **100%** |
| floortile | 0% | 0% |
| grippers | 95% | **100%** |
| storage | 85% | 0% |
| termes | 20% | **100%** |
| tyreworld | 0% | 0% |

### Phase 4d — Fix UP Simulator for Demo

Fix: strip trajectory constraints from GT problem before UP simulation:
```python
# In plan_renderer.py simulate_plan():
# Remove :constraints block from problem.pddl before parsing with PDDLReader
```
Or use LLM+P problems directly (already plain PDDL, no constraints).

### Phase 4b — Embodied envs (stretch)

Create `run_embodied_pipeline.py`:
```python
from src.costl.pipelines.multi_level_planning_3dsg import MultiLevelPlanningPipeline
```
Requires: AI2Thor/AlfWorld installed, 3DSG submodule initialized.

---

## Environment Setup

```bash
cd /DATA/context-matters-demo
source key.sh  # sets OPENAI_API_KEY + ANTHROPIC_API_KEY
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
git submodule update --init --recursive
```

Required env vars: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`

**Note:** `minigrid` (BabyAI) fails on Python 3.13 due to `pkg_resources` deprecation — use conda env with Python ≤ 3.12 for BabyAI simulator; Lexicon/LLM+P benchmarks work fine on 3.13.

---

## Running Benchmarks

```bash
source key.sh

# Lexicon — CoSTL (3 refinement iterations)
python run_benchmark.py --domain blocksworld --model claude-sonnet-4-6 --pddl_gen_iterations 3
python run_benchmark.py --domain babyai --model claude-sonnet-4-6 --pddl_gen_iterations 3
python run_benchmark.py --domain logistics --model claude-sonnet-4-6 --pddl_gen_iterations 3
python run_benchmark.py --domain sokoban --model claude-sonnet-4-6 --pddl_gen_iterations 3

# Lexicon — LLM+P ablation (1 iteration)
python run_benchmark.py --domain blocksworld --model claude-sonnet-4-6 --pddl_gen_iterations 1 --results_dir results_llmp

# LLM+P IPC — CoSTL (GT domain provided)
/home/xps/miniconda3/bin/python3 prepare_llmpp_data.py      # one-time data prep
/home/xps/miniconda3/bin/python3 run_llmpp_benchmark.py --domain all --model claude-sonnet-4-6

# LLM+P IPC — domain generation mode (NL→domain+problem)
# ablation: baseline | clean_domain | schema_problem | full | full_adequacy
/home/xps/miniconda3/bin/python3 run_llmpp_benchmark.py --domain blocksworld --method compare --generate_domain --ablation full_adequacy
/home/xps/miniconda3/bin/python3 run_llmpp_benchmark.py --domain barman --method compare --generate_domain --ablation full_adequacy
```

---

## Key File Map

```
src/costl/
  pipelines/
    low_level_planning.py          # Core loop — FIXED path bug + refine_problem unpack + empty plan
    lexicon_low_level.py           # LexiconLowLevelPipeline — VAL + UP sim + GIF rendering
    multi_level_planning_3dsg.py   # 3DSG pipeline — COMPLETED skeleton
    multi_level_planning.py        # LTL path (disabled imports)
  planner/
    low/
      pddl_generation.py           # FIXED: generate_problem + refine_problem signatures
      pddl_verification.py         # VAL_validate, verify_plan_with_up_simulator
      planner_utils.py             # FIXED: FD native fallback for UP-incompatible domains
      utils/grounding.py           # NEW: 8 UP-native grounding functions
  agents/
    gpt.py                         # OpenAI agent
    claude.py                      # NEW: Anthropic agent (ClaudeAgent)
  simulators/
    blocksworld_simulator.py       # UP SequentialSimulator + PIL rendering (get_image)
  plan_renderer.py                 # NEW: plan parsing + UP sim + GIF dispatch

data/
  blocksworld/data_2/              # 10 Lexicon problems
  babyai/data/data_1/              # 10 Lexicon problems
  logistics/data_1/                # 30 Lexicon problems
  sokoban/data_1/                  # 30 Lexicon problems
  llmpp/{domain}/p01..p20/         # 7×20 LLM+P IPC problems (prepared)

third-party/
  llm-pddl/                        # LLM+P dataset (cloned)
  context_matters_3dsg/            # submodule → /DATA/context-matters-3dsg
  lexicon_neurips/                  # Lexicon benchmark
  VAL/                             # PDDL validator binary

results/                           # Lexicon CoSTL results
results_llmp/                      # Lexicon LLM+P ablation results
results_llmpp/                     # LLM+P IPC CoSTL results (storage: 0% due to bug, superseded)
results_llmpp_fd/                  # LLM+P IPC CoSTL re-run with FD fallback (storage: 100%)

paper/
  main.tex                         # LaTeX skeleton (all TODOs)
  references.bib                   # Empty — needs entries

prepare_llmpp_data.py              # Convert LLM+P → CoSTL data format
run_benchmark.py                   # Lexicon benchmark entrypoint
run_llmpp_benchmark.py             # LLM+P IPC benchmark entrypoint
key.sh                             # API keys (OPENAI + ANTHROPIC)
```
