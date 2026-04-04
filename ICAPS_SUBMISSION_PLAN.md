# ICAPS 2026 Demo Track Submission Plan

**Deadline**: 3 days from now
**Track**: Demo Track (2 pages + 10-min video)
**Video Weight**: 50% of evaluation

---

## Paper Structure: Section-by-Section Requirements

### Abstract (250 words max)

**MUST HAVE:**
- One-sentence problem statement (NL-to-PDDL synthesis bottleneck)
- LAPIS system description (synthesizes domain + problem, VAL-guided refinement)
- Key empirical finding (self-consistent synthesis can outperform oracle domains)
- Demo highlight (Streamlit dashboard, video link)

**NICE TO HAVE:**
- Comparison claim against NL2Plan (if results ready)
- Semantic verification mention (if implemented)

**MISSING:**
- Final video URL (placeholder OK for submission, update in camera-ready)

---

### Introduction (~0.5 page)

**MUST HAVE:**
- The NL-to-PDDL bottleneck problem (1-2 sentences)
- Why existing approaches fail: single-shot synthesis has no error recovery
- LAPIS contribution framed as **demo system**, not research novelty
- The coupling insight: why LLM-generated domains can outperform GT

**NICE TO HAVE:**
- Reference to ContextMatters (ICRA 2026) as foundation
- Brief mention of competitive landscape (NL2Plan, ISR-LLM)

**WHAT TO AVOID:**
- Claiming schema injection as novel (it's not in 2026)
- Claiming VAL-guided refinement as novel (ISR-LLM did it)
- Long related work discussion (save space for results)

---

### Related Work (~0.25 page)

**MUST HAVE:**
- LLM+P citation (the baseline we compare against)
- ContextMatters citation (our foundation)
- One sentence acknowledging NL2Plan/ISR-LLM exist

**NICE TO HAVE:**
- Planetarium citation (semantic correctness gap motivation)
- LLM-Modulo citation (theoretical justification for external verification)

**WHAT TO AVOID:**
- Detailed comparison table (no space)
- Claiming to beat systems we haven't benchmarked

---

### Methodology (~0.5 page)

**MUST HAVE:**
- Pipeline figure (already exists in main.tex)
- Four stages described discursively:
  1. Domain synthesis from NL
  2. Adequacy check (CoT verification)
  3. Problem synthesis with schema injection
  4. VAL-guided iterative refinement
- The 4 demo aspects woven into prose (not bullet lists):
  - **Robustness**: refinement loop recovers from errors
  - **Generalization**: works across 7 IPC domains without tuning
  - **Scalability**: handles 80+ step plans
  - **Deployment**: single API key, no PDDL expertise needed

**NICE TO HAVE:**
- Semantic verification stage (if implemented)
- Mention of init-locking constraint (one clause, not paragraph)

**WHAT TO AVOID:**
- Detailed algorithm pseudocode (no space)
- Extensive implementation details

---

### Experimental Setup (~0.25 page)

**MUST HAVE:**
- LLM+P benchmark: 7 domains, 20 problems each
- Model: Claude Sonnet 4.6
- Planner: FastDownward via unified-planning
- Conditions: LLM+P, LAPIS/GT, LAPIS/Synthesis, LAPIS/Adequacy

**NICE TO HAVE:**
- Lexicon benchmark mention (supporting evidence)
- NL2Plan comparison setup (if running)

**WHAT TO AVOID:**
- Long justification of model choice
- Detailed hyperparameters

---

### Results (~0.5 page)

**MUST HAVE:**
- Table 1: Success rates across domains and conditions
- Key finding highlighted: Synthesis > GT on complex domains (Floortile 94% vs 45%)
- Honest acknowledgment of failures (Tyreworld GT: 0%)

**NICE TO HAVE:**
- Table 2: NL2Plan comparison (if results ready)
- Lexicon results as secondary validation
- Semantic verification ablation (if implemented)

**DATA SOURCE:**
- Use EXPERIMENTAL_NOTES_FOR_PAPER.md as ground truth for all numbers

---

### Demo Description (~0.25 page)

**MUST HAVE:**
- Streamlit dashboard overview
- What users can do: input NL, see generated PDDL, watch refinement, view plan
- Video link (placeholder OK)
- Code repository link

**NICE TO HAVE:**
- Screenshot or figure of the UI
- Mention of side-by-side GT comparison feature

---

### Conclusion (~0.25 page)

**MUST HAVE:**
- Restate key finding (self-consistent synthesis insight)
- Demo value proposition (zero PDDL expertise required)
- Limitations acknowledged (syntactic-only validation)

**NICE TO HAVE:**
- Future work: semantic verification, NL2Plan comparison
- Mention of ongoing experiments

**WHAT TO AVOID:**
- Overstating contributions
- Promising features not demonstrated

---

## Implementation Tasks: Priority Order

### CRITICAL (Must complete before deadline)

| Task | Time | Owner | Status |
|------|------|-------|--------|
| Paper draft complete | 4h | - | TODO |
| Table 1 with final numbers | 1h | - | TODO |
| Video script written | 2h | - | TODO |
| Video recorded | 3h | - | TODO |
| Frontend stable for recording | 4h | - | TODO |

### HIGH (Should complete before deadline)

| Task | Time | Owner | Status |
|------|------|-------|--------|
| Frontend polish (see TASK_FRONTEND_IMPROVEMENTS.md) | 6h | - | TODO |
| NL2Plan results (if pipeline works) | 6h | - | IN PROGRESS |
| Paper review and revision | 2h | - | TODO |

### MEDIUM (Nice to have before deadline)

| Task | Time | Owner | Status |
|------|------|-------|--------|
| Semantic verification (see TASK_SEMANTIC_VERIFICATION.md) | 6h | - | TODO |
| Re-run experiments with semantic checks | 4h | - | TODO |
| Side-by-side PDDL comparison in UI | 3h | - | TODO |

### LOW (Can do after deadline / camera-ready)

| Task | Time | Owner | Status |
|------|------|-------|--------|
| Extended NL2Plan comparison | 8h | - | TODO |
| Additional domains (logistics, sokoban) | 8h | - | TODO |
| ISR-LLM comparison | 8h | - | TODO |
| Iteration sensitivity analysis | 4h | - | TODO |

---

## 3-Day Timeline

### Day 1 (Today)

**Morning:**
- [ ] Finalize Table 1 numbers from EXPERIMENTAL_NOTES
- [ ] Start paper draft (abstract, intro, methodology)
- [ ] Verify frontend runs without crashes

**Afternoon:**
- [ ] Continue paper draft (results, conclusion)
- [ ] Start video script
- [ ] Check NL2Plan experiment status

**Evening:**
- [ ] First complete paper draft
- [ ] Frontend improvements begin

### Day 2

**Morning:**
- [ ] Paper revision based on self-review
- [ ] Frontend polish continues
- [ ] NL2Plan results collection (if ready)

**Afternoon:**
- [ ] Video script finalization
- [ ] Test run video recording
- [ ] Update paper with NL2Plan results (if available)

**Evening:**
- [ ] Semantic verification implementation (if time permits)
- [ ] Second paper revision

### Day 3 (Deadline Day)

**Morning:**
- [ ] Final paper revision
- [ ] Video recording (multiple takes)
- [ ] Video editing and upload

**Afternoon:**
- [ ] Paper formatting check (2 pages, AAAI template)
- [ ] Video URL updated in paper
- [ ] Final submission

---

## What's Missing (Honest Assessment)

### For a Strong Demo Track Submission
| Item | Status | Blocker? |
|------|--------|----------|
| Working Streamlit demo | Exists | No |
| 7-domain ablation results | Complete | No |
| LLM+P baseline comparison | Complete | No |
| Video | Not recorded | **Yes** |
| Paper draft | Not written | **Yes** |

### For a Competitive Research Paper (NOT required for demo track)
| Item | Status | Impact |
|------|--------|--------|
| NL2Plan comparison | In progress | Medium |
| Semantic verification | Not implemented | Low for demo |
| ISR-LLM comparison | Not done | Low |
| Iteration sensitivity | Not done | Low |

---

## Risk Mitigation

### If NL2Plan fails to run
- Fallback: Use LLM+P as primary baseline, cite NL2Plan without comparison
- Text: "Direct comparison with recent full-synthesis systems is ongoing work"

### If semantic verification isn't ready
- Fallback: Don't mention it in the paper
- Focus on the coupling insight (Synthesis > GT) as the key finding

### If video recording has issues
- Record demo in shorter segments, edit together
- Worst case: screen recording with voiceover (acceptable for demo track)

### If frontend crashes during recording
- Use the simpler `app.py` instead of `app_premium.py`
- Pre-load a successful example, show cached results

---

## Files Reference

| File | Purpose |
|------|---------|
| `paper/main.tex` | Paper source (to be updated) |
| `EXPERIMENTAL_NOTES_FOR_PAPER.md` | Ground truth for results |
| `tasks/TASK_SEMANTIC_VERIFICATION.md` | Semantic verification spec |
| `tasks/TASK_FRONTEND_IMPROVEMENTS.md` | Frontend work spec |
| `tasks/TASK_NL2PLAN_COMPARISON.md` | NL2Plan comparison spec |
| `demo/app_premium.py` | Main demo application |

---

## Post-Deadline Work (Camera-Ready / Follow-up)

1. **Complete NL2Plan comparison** and update Table 1
2. **Implement semantic verification** and run full ablation
3. **Extended evaluation** on Lexicon benchmark
4. **Iteration sensitivity analysis** (1, 2, 3, 5 iterations)
5. **Polish video** with better animations/editing
6. **Prepare live demo** for conference presentation

---

*Last Updated: 2026-04-04*
