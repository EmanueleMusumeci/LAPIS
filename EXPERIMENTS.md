# EXPERIMENTS.md — LAPIS: ICAPS 2026 Demo

All experiments use Claude Sonnet 4.6 and the script:
```
/home/xps/miniconda3/bin/python3 run_llmpp_benchmark.py [args]
```
Always `source key.sh` first.

---

## Table 1 — LLM+P IPC Domains: Full Ablation (7 domains × 4 conditions)

This is the **paper's main results table**. Run each cell separately (cost ~$0.50–2.00 per domain run).

### Condition A: LAPIS/GT — GT domain provided, schema injection, 3 refinements
*(Upper bound; domain generation disabled)*
```bash
source key.sh
for domain in barman blocksworld floortile grippers storage termes tyreworld; do
  /home/xps/miniconda3/bin/python3 run_llmpp_benchmark.py \
    --domain $domain --method costl --model claude-sonnet-4-6
done
```
Results: `results_llmpp/benchmark_llmpp_{domain}_costl_claude_sonnet_4_6/`

**Status:**
| Domain | Done? | VAL% |
|--------|-------|------|
| barman | ✅ (20260329) | 100% |
| blocksworld | ✅ (20260329) | 100% |
| floortile | ✅ (20260329) | 0% |
| grippers | ✅ (20260329) | 100% |
| storage | ✅ (FD fallback) | 100% |
| termes | ✅ (20260329) | 100% |
| tyreworld | ✅ (20260329) | 0% |

---

### Condition B: LLM+P baseline — GT domain, single-shot, 0 refinements
```bash
source key.sh
for domain in barman blocksworld floortile grippers storage termes tyreworld; do
  /home/xps/miniconda3/bin/python3 run_llmpp_benchmark.py \
    --domain $domain --method llmpp --model claude-sonnet-4-6
done
```
Results: `results_llmpp/benchmark_llmpp_{domain}_llmpp_claude_sonnet_4_6/`

**Status:**
| Domain | Done? | VAL% |
|--------|-------|------|
| barman | ✅ | 100% |
| blocksworld | ✅ | 100% |
| floortile | ✅ | 0% |
| grippers | ✅ | 100% |
| storage | ✅ | 85% (UP bug) |
| termes | ✅ | 20% |
| tyreworld | ✅ | 0% |

> **Note:** LLM+P on storage appears 85% due to UP parse bug on the GT domain.
> Rerun with FD fallback if needed. Termes 20% is a real advantage for LAPIS/GT.

---

### Condition C: LAPIS/full — domain generated from NL, clean prompt + schema, 3 refinements, no adequacy
```bash
source key.sh
for domain in barman blocksworld floortile grippers storage termes tyreworld; do
  /home/xps/miniconda3/bin/python3 run_llmpp_benchmark.py \
    --domain $domain --method costl --generate_domain --ablation full \
    --model claude-sonnet-4-6
done
```
Results: `results_llmpp/benchmark_llmpp_{domain}_costl_domgen_claude_sonnet_4_6/`

**Status:**
| Domain | Done? | VAL% |
|--------|-------|------|
| barman | ✅ (20260329) | 5% (1/20) |
| blocksworld | ✅ (20260329) | 85% (17/20) |
| floortile | ❌ TODO | — |
| grippers | ❌ TODO | — |
| storage | ❌ TODO | — |
| termes | ❌ TODO | — |
| tyreworld | ❌ TODO | — |

---

### Condition D: LAPIS/full+adequacy — domain generated from NL, + CoT adequacy checks
```bash
source key.sh
for domain in barman blocksworld floortile grippers storage termes tyreworld; do
  /home/xps/miniconda3/bin/python3 run_llmpp_benchmark.py \
    --domain $domain --method costl --generate_domain --ablation full_adequacy \
    --model claude-sonnet-4-6
done
```
Results: `results_llmpp/benchmark_llmpp_{domain}_costl_domgen_full_adequacy_claude_sonnet_4_6/`

**Status:**
| Domain | Done? | VAL% |
|--------|-------|------|
| barman | ⚠️ partial (p01–p03 only) | 1/3 targeted |
| blocksworld | ⚠️ partial (p05,p10,p18 only) | 3/3 targeted |
| floortile | ❌ TODO | — |
| grippers | ❌ TODO | — |
| storage | ❌ TODO | — |
| termes | ❌ TODO | — |
| tyreworld | ❌ TODO | — |

**⚠️ PRIORITY: Run full 20-problem Condition D for all 7 domains.**

---

### Condition E (optional): LLM+P/domgen — same as C but 0 refinements (LLM+P-style but with domain generation)
```bash
source key.sh
for domain in barman blocksworld; do   # start with easy ones
  /home/xps/miniconda3/bin/python3 run_llmpp_benchmark.py \
    --domain $domain --method llmpp --generate_domain --ablation full \
    --model claude-sonnet-4-6
done
```
Results: `results_llmpp/benchmark_llmpp_{domain}_llmpp_domgen_claude_sonnet_4_6/`

**Status:**
| Domain | Done? | VAL% |
|--------|-------|------|
| barman | ✅ | 0% |
| blocksworld | ✅ | 75% |
| others | ❌ optional | — |

---

## Ablation Table 2 (paper supplement) — Prompt Ablation on Blocksworld + Barman

*How much does each Approach A component contribute?*

```bash
source key.sh
for ablation in baseline clean_domain schema_problem full full_adequacy; do
  for domain in blocksworld barman; do
    /home/xps/miniconda3/bin/python3 run_llmpp_benchmark.py \
      --domain $domain --method costl --generate_domain \
      --ablation $ablation --model claude-sonnet-4-6
  done
done
```

**Status:** All ❌ TODO (Conditions C/D partially done; baseline/clean_domain/schema_problem not yet run)

Expected table:

| Ablation | clean domain prompt | schema injection | adequacy CoT | blocksworld% | barman% |
|----------|:---:|:---:|:---:|---|---|
| baseline | ✗ | ✗ | ✗ | ? | ? |
| clean_domain | ✓ | ✗ | ✗ | ? | ? |
| schema_problem | ✗ | ✓ | ✗ | ? | ? |
| full | ✓ | ✓ | ✗ | 85 | 5 |
| full_adequacy | ✓ | ✓ | ✓ | ? | ? |

---

## Lexicon Benchmark Results (already complete — for reference)

Run with `run_benchmark.py`. Results already in `results/` and `results_llmp/`.

| Domain | CoSTL (3-iter) | LLM+P (1-iter) |
|--------|---------------|----------------|
| Blocksworld | 60% | 60% |
| BabyAI | **100%** | 90% |
| Logistics | 40% | 37% |
| Sokoban | 57% | 43% |

---

## Cost Estimates (Claude Sonnet 4.6)

| Run | Approx tokens | Est. cost |
|-----|--------------|-----------|
| 1 domain × 20 problems × LAPIS/full | ~200k tokens | ~$0.60 |
| 1 domain × 20 problems × LAPIS/full+adequacy | ~350k tokens | ~$1.05 |
| Full Condition C (7 domains) | ~1.4M tokens | ~$4.20 |
| Full Condition D (7 domains) | ~2.5M tokens | ~$7.50 |
| Full ablation Table 2 (5 ablations × 2 domains) | ~3M tokens | ~$9.00 |

---

## Run Order (Priority)

1. **[CRITICAL]** Complete Condition D (full_adequacy) for barman + blocksworld (full 20 problems)
2. **[HIGH]** Run Condition C for floortile, grippers, storage, termes, tyreworld
3. **[HIGH]** Run Condition D for floortile, grippers, storage, termes, tyreworld
4. **[MEDIUM]** Run ablation Table 2 (baseline, clean_domain, schema_problem on blocksworld + barman)
5. **[LOW]** Run Condition E (LLM+P/domgen) for remaining 5 domains
