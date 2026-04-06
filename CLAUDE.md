# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Goal

This workspace produces benchmark results and an extended abstract for the **ICAPS 2026 Demo track** (deadline: see `https://icaps26.icaps-conference.org/calls/demos/`). The demo showcases **ContextMatters** (arxiv: 2506.15828), using the faster LAPIS implementation from `/DATA/LAPIS` as the engine (the original prototype is at `/DATA/context-matters`).

The scope is the **low-level planner only, without LTL constraints**, evaluated on unconstrained environments from the Lexicon benchmark. Primary targets: **Blocksworld** and **BabyAI** (no environment feedback). Secondary (time-permitting): **AI2Thor / AlfWorld / VirtualHome** (with environment feedback, requires 3DSG reintegration).

## Setup

The working repo is a copy of `/DATA/LAPIS` placed here. Install dependencies:

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

# Run LAPIS benchmark on IPC domains:
python run_benchmark.py --domain blocksworld --method lapis --generate_domain

# Verify a stored plan:
python3 third-party/lexicon_neurips/verify_plan.py blocksworld 2 100 o3

# Choose planner backend (default: pyperplan; up_fd = FastDownward via Unified Planning):
python run_benchmark.py --domain blocksworld --method lapis --planner up_fd
```

## Architecture

```
src/lapis/
  pipelines/
    base.py                    # BasePipeline ABC: run() iterates splits -> _process_task()
    low_level_planning.py      # LowLevelPlanningPipeline: PDDL gen+refine+plan+VAL loop
    low_level_planning_oracle.py  # Oracle variant with GT simulator grounding
    lapis_low_level.py         # LAPIS wrapper for IPC benchmarks
    lapis_low_level_oracle.py  # LAPIS oracle wrapper

  planner/
    low/                       # Low-level: PDDL generation, problem refinement, VAL validation
      pddl_generation.py       # generate_domain(), generate_problem(), refine_problem()
      pddl_verification.py     # VAL_validate(), VAL_ground(), translate_plan()
      planner_utils.py         # plan_with_output() — calls unified-planning backends
      planner.py               # LowLevelPlanner class (orchestrates low/ modules)
      heuristics.py            # Plan quality heuristics
      domain_parser.py         # PDDL domain parsing helpers

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

**Pipeline architecture:**
- Demo uses low-level planning only: `LowLevelPlanningPipeline` for direct PDDL synthesis
- No LTL constraints or high-level planner (removed from demo scope)
- Focus on unconstrained IPC domain problems

**Benchmark data flow:**
- IPC domains in `data/llmpp/{domain}/` with NL descriptions
- Results written to `results_llmpp/{experiment_name}/{timestamp}/`
- Each problem gets a `manifold.json` summary with metrics

**Low-level planning loop** (in `LowLevelPlanningPipeline`):
1. Generate PDDL domain from NL description (optional, can use GT)
2. Generate PDDL problem from NL + goal
3. Run planner (`plan_with_output` via unified-planning)
4. If planning fails: refine with LLM feedback (up to `pddl_gen_iterations` times)
5. VAL validation after each attempt
6. Optional semantic verification checks

## Notes

- Planner backend is configurable: `pyperplan` (default, pure Python), `up_fd` (FastDownward via UP), `fd` (native binary), `symk` (local wrapper).
- The `LexiconPipeline` uses `env_class` (e.g., `Blocksworld` from lexicon) to handle NL prompt construction and response parsing — it wraps Lexicon's own eval loop rather than the LAPIS PDDL refinement loop.
- `VAL` binary is in `third-party/VAL/`; `translate_plan` converts unified-planning plan format to VAL-parseable format before validation.
- The high-level planner's `Domains/{domain}/data_{n}/` folders are separate from `third-party/lexicon_neurips/domains/{domain}/data/` — the former is LAPIS's own dataset (Gibson scenes, NL task descriptions), the latter is Lexicon's benchmark.
