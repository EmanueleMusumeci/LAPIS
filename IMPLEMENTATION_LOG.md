# LAPIS Implementation Log

Implementation milestones for ICAPS 2026 demo development, ordered chronologically.

---

## 1. Semantic Verification Benchmark
**Completed**: 2026-04-05 16:53

Comprehensive semantic verification tests across 7 IPC domains (140 problems).

### Features
- Modular pluggable extractor architecture (commit 85fbb1c)
- Fixed regex false positive bug (balanced parenthesis matching)
- Domain-level semantic checks

### Domains Tested
Blocksworld, Barman, Storage, Termes, Grippers, Tyreworld, Floortile (20 problems each)

### Scripts Created
- `monitor_benchmark_progress.sh`
- `check_completion.sh`
- `aggregate_semantic_results.py`

---

## 2. Lexicon Standardization Scripts
**Completed**: 2026-04-05 21:00

Scripts for standardized Lexicon benchmark (20 problems/domain).

### Files Created
- `run_lexicon_standardization.sh` - Master orchestration
- `scripts/run_lexicon_lapis_additional.py` - LAPIS on Blocksworld/BabyAI 11-20
- `scripts/run_lexicon_baselines.py` - Direct LLM baselines (Gemini 3.1 Pro, GPT-5.4, Claude Opus 4.6)
- `scripts/aggregate_lexicon_results.py`
- `scripts/generate_lexicon_table.py`

### Cost Estimate
~$6.10 total, ~7 hours runtime

---

## 3. Oracle Grounding Pipeline
**Completed**: 2026-04-06 02:48

Oracle grounding in separate files to preserve original LAPIS pipeline.

### Files Created
- `src/lapis/pipelines/low_level_planning_oracle.py` (825 lines)
- `src/lapis/pipelines/lapis_low_level_oracle.py` (263 lines)

### Key Functions
- `_get_simulator_raw_state_report()` - Extract GT simulator state
- `_map_simulator_state_to_assignment()` - LLM maps state to PDDL predicates
- `_setup_gt_simulator()` - Initialize GT simulator
- `refine_domain_and_problem_unified()` - Unified refinement

### Architecture
| Feature | Self-Consistent | Oracle |
|---------|----------------|--------|
| :init generation | LLM invents from NL | GT simulator → LLM mapping |
| Refinement | Problem-only | Unified domain+problem |
| Validation | VAL only | VAL + simulator (gen + GT) |

### Usage
```bash
python run_benchmark.py --domain blocksworld --method lapis \
  --generate_domain --ablation full_adequacy --semantic_checks \
  --refine_domain --oracle_grounding --model claude-sonnet-4-6
```

---

## 4. Oracle Benchmark Infrastructure
**Completed**: 2026-04-06 04:41

Self-supervised benchmark system for 7 IPC domains (140 problems).

### Files Created
- `tasks/FINAL_BENCHMARK_TASK_{DOMAIN}.md` (7 task definitions)
- `run_oracle_benchmark_all.py` - Master orchestrator
- `run_oracle_benchmark_{domain}.py` - Per-domain runners (7 files)
- `monitor_benchmarks.sh` - Real-time dashboard
- `preflight_check.sh` - Environment validator

### Features
- Checkpoint system (resumes on crash)
- API error retry with backoff
- Parallel execution (6-8 hours for 140 problems)
- Real-time monitoring

### Architecture
```
run_oracle_benchmark_all.py (Master)
    +-> run_oracle_benchmark_{domain}.py (Background)
        +-> LowLevelPlanningOraclePipeline
            +-> ClaudeAgent + GT Simulator
```

---

*Consolidated from: SETUP_COMPLETE.md, LEXICON_READY_TO_RUN.md, ORACLE_IMPLEMENTATION_COMPLETE.md, BENCHMARK_SETUP_COMPLETE.md*
*Generated: 2026-04-06*
