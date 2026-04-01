# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Goal

This workspace produces benchmark results and an extended abstract for the **ICAPS 2026 Demo track** (deadline: see `https://icaps26.icaps-conference.org/calls/demos/`). The demo showcases **ContextMatters** (arxiv: 2506.15828), using the faster CoSTL implementation from `/DATA/CoSTL` as the engine (the original prototype is at `/DATA/context-matters`).

The scope is the **low-level planner only, without LTL constraints**, evaluated on unconstrained environments from the Lexicon benchmark. Primary targets: **Blocksworld** and **BabyAI** (no environment feedback). Secondary (time-permitting): **AI2Thor / AlfWorld / VirtualHome** (with environment feedback, requires 3DSG reintegration).

## Setup

The working repo is a copy of `/DATA/CoSTL` placed here. Install dependencies:

```bash
# Automated (creates venv, installs requirements-lexicon.txt):
chmod +x setup_lexicon_env.sh && ./setup_lexicon_env.sh

# Or manually:
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
git submodule update --init --recursive
mkdir -p third-party/lexicon_neurips/intermediate_sas
```

Required env vars for real LLM calls: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`.

## Running Benchmarks

```bash
# Generate benchmark problems (blocksworld, N problems, seed, num_blocks):
python3 third-party/lexicon_neurips/generate_benchmark.py blocksworld 100 1 2

# Run low-level-only pipeline on Lexicon (unconstrained):
python run_lexicon_pipeline.py

# Run multi-level pipeline (high+low) on a domain/batch:
python run_pipeline.py --domain blocksworld --pipeline multi_level --batch_id data_1

# Verify a stored plan:
python3 third-party/lexicon_neurips/verify_plan.py blocksworld 2 100 o3

# Choose planner backend (default: pyperplan; up_fd = FastDownward via Unified Planning):
python run_pipeline.py --domain blocksworld --pipeline multi_level --batch_id data_1 --planner up_fd
```

## Architecture

```
src/costl/
  pipelines/
    base.py                    # BasePipeline ABC: run() iterates splits -> _process_task()
    low_level_planning.py      # LowLevelPlanningPipeline: PDDL gen+refine+plan+VAL loop
    multi_level_planning.py    # Adds HighLevelPlanner + LTL trace checking above LLP
    multi_level_planning_3dsg.py  # 3DSG variant (needs 3DSG submodule, stripped from CoSTL)
    lexicon.py                 # LexiconPipeline: thin wrapper for Lexicon benchmark eval
    baseline.py                # BaselinePipeline: direct Lexicon library integration

  planner/
    low/                       # Low-level: PDDL generation, problem refinement, VAL validation
      pddl_generation.py       # generate_domain(), generate_problem(), refine_problem()
      pddl_verification.py     # VAL_validate(), VAL_ground(), translate_plan()
      planner_utils.py         # plan_with_output() — calls unified-planning backends
      planner.py               # LowLevelPlanner class (orchestrates low/ modules)
      heuristics.py            # Plan quality heuristics
      domain_parser.py         # PDDL domain parsing helpers
    high/
      planner.py               # HighLevelPlanner: NL -> domain/goal/constraints -> plan loop
      Planner/                 # LTL-based iterative plan generation:
        formula_generator.py   # LTL formula from NL constraints (TO REMOVE/COMMENT for demo)
        trace_generator.py     # Plan -> trace for LTL checking (TO REMOVE/COMMENT)
        trace_check.py         # Formal LTL trace verification (TO REMOVE/COMMENT)
        plan_generator.py      # Plan generation step
        nl_description_generator.py  # NL -> domain/problem/actions/goal/constraints
        feedback_translator.py
      Planner_ConstraintDriven/  # Alternative constraint-driven planner (LTL, TO REMOVE)
      Domains/
        blocksworld/data_{1..4}/  # Pre-generated problem instances
        babyai/data_{1..3}/

  simulators/
    blocksworld_simulator.py   # UP SequentialSimulator wrapping Lexicon blocksworld
    babyai_simulator.py        # MiniGrid-based BabyAI simulator
    ai2thor_simulator.py       # AI2Thor (env feedback, requires 3DSG)
    alfworld_simulator.py      # AlfWorld (env feedback, requires 3DSG)
    virtualhome_simulator.py   # VirtualHome (env feedback, requires 3DSG)
    base_simulator.py          # BaseSimulator ABC
    scenario.py                # Scenario (cost model)

  agents/
    agent.py                   # Agent base (wraps LLM calls)
    gpt.py / llama.py          # Provider-specific agents

  utils/
    log.py                     # save_file(), save_statistics(), copy_file()
    graph.py                   # read_graph_from_path(), get_verbose_scene_graph()
    compile_verifier.py        # verify_plan_with_compiled_val() for Lexicon GT check
    pddl.py / logic_utils.py

third-party/
  lexicon_neurips/             # Lexicon benchmark (submodule); domains: blocksworld, babyai, ...
  LTL_Verifier/                # ltl_verifier Python package (only needed for LTL path)
  VAL/                         # PDDL validator binary
  alfworld/ virtualhome/       # Simulator submodules (optional)
  symk_wrapper/                # SymK planner wrapper (optional)
```

## Key Design Decisions

**Two pipeline paths:**
1. **LTL path** (`multi_level_planning.py`): `HighLevelPlanner` generates LTL formulas, traces are formally verified via `trace_check`, then `LowLevelPlanner` decomposes each subgoal. This is the full CoSTL system.
2. **Unconstrained / demo path** (target): `LowLevelPlanningPipeline` or `LexiconPipeline` directly. No LTL formula generation, no trace verification, no `Planner/` or `Planner_ConstraintDriven/` involvement.

**LTL components to remove/comment for the demo:**
- `src/costl/planner/high/Planner/formula_generator.py` — LTL formula generation
- `src/costl/planner/high/Planner/trace_generator.py` and `trace_check.py` — trace generation + verification
- `src/costl/planner/high/Planner_ConstraintDriven/` — entire constraint-driven planner
- `third-party/LTL_Verifier/` — LTL verifier submodule
- In `multi_level_planning.py`: imports from `trace_check`, `formula_generator`, and `unified_planning` LTL operators (`Always`, `Sometime`, etc.)

**3DSG reintegration (for embodied env pipeline):**
- `multi_level_planning_3dsg.py` is the pipeline variant that grounded plans in a 3D Scene Graph; this was removed from CoSTL but exists in the original ContextMatters at `/DATA/context-matters`.
- The 3DSG adapter and graph utilities live in `src/costl/planner/low/utils/graph.py` (partially) and need restoration from `/DATA/context-matters/src/context_matters/`.
- For the embodied envs (AI2Thor/AlfWorld/VirtualHome), re-add 3DSG support as a git submodule (only 3DSG + adapter, not full ContextMatters).

**Lexicon benchmark data flow:**
- Problems stored at `third-party/lexicon_neurips/domains/{domain}/data/{batch_id}/{problem_id}/`
- Each problem folder has `domain.pddl`, `problem.pddl`, `compiled_domain.pddl`, `compiled_problem.pddl`
- `compiled_*` files encode LTL constraints as PDDL automata — for unconstrained evaluation, use base `domain.pddl`/`problem.pddl` only
- Results written to `results/{experiment_name}/{timestamp}/`; each problem gets a `manifold.json` summary

**Low-level planning loop** (in `LowLevelPlanningPipeline.grounded_planning`):
1. (Optional) Generate PDDL domain from NL description
2. Generate PDDL problem from scene graph + goal
3. Run planner (`plan_with_output` via unified-planning)
4. If planning fails: refine problem with LLM feedback (up to `pddl_gen_iterations` times)
5. VAL validation + grounding check after each attempt
6. (Optional) Ground plan in 3D Scene Graph

## Notes

- Planner backend is configurable: `pyperplan` (default, pure Python), `up_fd` (FastDownward via UP), `fd` (native binary), `symk` (local wrapper).
- The `LexiconPipeline` uses `env_class` (e.g., `Blocksworld` from lexicon) to handle NL prompt construction and response parsing — it wraps Lexicon's own eval loop rather than the CoSTL PDDL refinement loop.
- `VAL` binary is in `third-party/VAL/`; `translate_plan` converts unified-planning plan format to VAL-parseable format before validation.
- The high-level planner's `Domains/{domain}/data_{n}/` folders are separate from `third-party/lexicon_neurips/domains/{domain}/data/` — the former is CoSTL's own dataset (Gibson scenes, NL task descriptions), the latter is Lexicon's benchmark.
