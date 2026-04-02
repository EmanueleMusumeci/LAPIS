# CHECKPOINT.md — LAPIS ICAPS 2026 Demo

> Last updated: 2026-04-01

## Project

**ICAPS 2026 Demo submission** — LAPIS (Language-Adaptive PDDL Iterative Synthesis), based on ContextMatters (arXiv: 2506.15828). Evaluated on Lexicon benchmark domains and LLM+P IPC domains.

- **Working repo:** `/DATA/lapis`
- **Official paper:** `LAPIS__Language_Adaptive_PDDL_Iterative_Synthesis.zip`
- **Engine:** CoSTL low-level planner (LTL path disabled)

---

## Official Paper Tables

### Table 1: VAL success rate (%) — LLM+P IPC Domains (20 problems each)

| Domain | LLM+P | LAPIS/GT | LAPIS/full | LAPIS/full+adequacy |
|--------|-------|----------|------------|---------------------|
| blocksworld | 75 | 100 | 85 | 100 |
| barman | 0 | 100 | 5 | 5 |
| storage | 85 | 100 | **---** | **---** |
| termes | 20 | 100 | **---** | **---** |

**Missing:** storage and termes for LAPIS/full and LAPIS/full+adequacy

### Table 2: Direct LLM vs LAPIS — Lexicon Benchmark

| Model | BlocksWorld | Logistics | Sokoban |
|-------|-------------|-----------|---------|
| o3 | 83 | 40 | 60 |
| Gemini 2.5 | 83 | 43 | 56 |
| DeepSeek R1 | 73 | 37 | 30 |
| Claude 3.7 | 10 | 3 | 10 |
| **LAPIS (GPT-4o)** | 60 | 40 | 57 |

**Status:** Complete

---

## Experiment Status

### Completed

| Experiment | Status | Location |
|------------|--------|----------|
| Lexicon (4 domains) | ✅ | `results/` |
| LLM+P Condition A (LAPIS/GT, 7 domains) | ✅ | `results_llmpp/` |
| LLM+P Condition B (LLM+P baseline, 7 domains) | ✅ | `results_llmpp/` |
| LLM+P Condition C (LAPIS/full) — blocksworld, barman | ✅ | `results_llmpp/` |

### Pending (see EXPERIMENTS_PLAN.md)

| Experiment | Status | Priority |
|------------|--------|----------|
| storage LAPIS/full | TODO | HIGH |
| storage LAPIS/full+adequacy | TODO | HIGH |
| termes LAPIS/full | TODO | HIGH |
| termes LAPIS/full+adequacy | TODO | HIGH |

---

## Key Files

```
src/costl/
  pipelines/
    low_level_planning.py          # Core LLP loop
    lexicon_low_level.py           # Lexicon benchmark pipeline
  planner/
    low/
      pddl_generation.py           # Domain/problem gen + adequacy checks
      pddl_verification.py         # VAL validation
      planner_utils.py             # Planner backends (pyperplan, FD)
  agents/
    gpt.py                         # OpenAI agent
    claude.py                      # Anthropic agent

demo/
  app.py                           # Streamlit demo UI
  runner.py                        # Pipeline runner

data/
  llmpp/{domain}/p01..p20/         # LLM+P IPC problems

results/                           # Lexicon results
results_llmpp/                     # LLM+P IPC results
results_icaps2026/                 # Target for new experiments

paper/
  main.tex                         # LaTeX source

EXPERIMENTS_PLAN.md                # Experiment reproduction plan
UI_PLAN.md                         # Demo UI improvement plan
REFERENCE.md                       # Design decisions + LLP issues
```

---

## Environment

```bash
cd /DATA/lapis
source key.sh  # API keys
source .venv/bin/activate  # or use /home/xps/miniconda3/bin/python3
```

Required env vars: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`

---

## Running Experiments

```bash
# Missing experiments (see EXPERIMENTS_PLAN.md)
./run_icaps_experiments.sh

# Or manually:
source key.sh
python run_llmpp_benchmark.py --domain storage --method costl \
    --generate_domain --ablation full --model claude-sonnet-4-6

python run_llmpp_benchmark.py --domain storage --method costl \
    --generate_domain --ablation full_adequacy --model claude-sonnet-4-6
```

---

## Demo

```bash
# Mock mode (no API keys)
LAPIS_DEMO_MOCK=1 streamlit run demo/app.py

# Real mode
source key.sh && streamlit run demo/app.py
```

---

## Next Steps

1. **Run missing experiments** — storage and termes (see EXPERIMENTS_PLAN.md)
2. **Update paper Table 1** with new results
3. **Fix demo UI** — see UI_PLAN.md
4. **Record demo video**
5. **Submit to ICAPS 2026 Demo track**
