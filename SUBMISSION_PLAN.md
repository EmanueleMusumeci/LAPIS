# SUBMISSION_PLAN.md — ICAPS 2026 Demo Track

---

## 1. System Name Decision

Current placeholder: **LAPIS** (*Language-Adaptive PDDL Iterative Synthesis*)

**Candidate shortlist:**

| Name | Expansion | Vibe |
|------|-----------|------|
| **LAPIS** | Language-Adaptive PDDL Iterative Synthesis | Gemstone — each refinement polishes the plan |
| **PRISM** | Planning via Refinement and Iterative Synthesis from natural-language Modalities | Light refracted into structure |
| **GRAIL** | Grounded Refinement for AI-Language planning | Quest metaphor |
| **FORGE** | Formal Objective Refinement via Generative Engines | Tool/craft metaphor |

**Recommendation:** LAPIS. It's short, positive, and the acronym is tight.
If rejected: PRISM as fallback.

**Action:** Decide before submission → do a global `sed -i 's/LAPIS/CHOSEN/g'` in `paper/main.tex`.

---

## 2. Anonymization Plan

Check the ICAPS 2026 demo call at:
  https://icaps26.icaps-conference.org/calls/demos/

**If single-blind (likely for demos):**
- No changes needed. Author block is already in the paper.
- Keep GitHub URL in the paper.

**If double-blind:**
In `paper/main.tex`, replace the author block:
```latex
% ANONYMOUS SUBMISSION
\author{Anonymous}
```
And replace the GitHub URL with an anonymous placeholder:
```latex
Code available at: \url{https://anonymous.4open.science/r/LAPIS-demo}
```
Use https://anonymous.4open.science to create an anonymous mirror of the GitHub repo.

The `paper/main.tex` already has a comment marking the author block with
"TODO (anonymization)" — search for it.

---

## 3. Website Plan

**URL:** https://emanuelemusumeci.github.io/ContextMattersDemo

**Setup steps:**
1. Create a `gh-pages` branch in the repo:
   ```bash
   git checkout --orphan gh-pages
   git reset --hard
   ```
2. Add a minimal `index.html` (or use Jekyll/Hugo).
3. Enable GitHub Pages in repo Settings → Pages → Source: `gh-pages` branch.

**Minimum viable content:**
- Title + 1-paragraph abstract
- Pipeline figure (TikZ rendered to PNG, or system diagram)
- Results table (copy from paper)
- Links: paper (arXiv / ICAPS proceedings), code (GitHub), demo video

**Demo video:** Record a 2–3 min screencast of:
- Blocksworld: NL input → PDDL domain → PDDL problem → plan → animation
- Barman: adequacy check on/off comparison
- Side-by-side with LLM+P baseline

Recommended tool: OBS Studio or `ffmpeg` screen capture.

**Action items:**
- [ ] Create `gh-pages` branch with `index.html`
- [ ] Add project website URL to paper once live
- [ ] Record demo video before submission deadline

---

## 4. Submission Checklist

- [ ] **Decide system name** (LAPIS or alternative)
- [ ] **Complete experiments** — see EXPERIMENTS.md for pending runs
- [ ] **Fill in results table** in `paper/main.tex` (all `---` cells)
- [ ] **Download AAAI author kit** from https://aaai.org/authorkit26/
      → drop `aaai26.sty` and `aaai26.bst` into `paper/`
      → uncomment `\usepackage[submission]{aaai26}` in `main.tex`
- [ ] **Check page limit** — 2 pages excluding references
- [ ] **Check anonymization policy** on ICAPS 2026 call page
- [ ] **Create GitHub Pages** website
- [ ] **Record demo video** (for submission or booth)
- [ ] **Fix ContextMatters BibTeX** — fill in full title/authors in references.bib
      (currently has TODO placeholder — the ICRA 2026 camera-ready title is
       "Context Matters! Relaxing Goals with LLMs for Feasible 3D Scene Planning")
- [ ] **Submit via EasyChair** (verify link on ICAPS 2026 call page)
- [ ] **Merge** `integration-merge-attempt` → `main` before final submission

---

## 5. Git / Repo Hygiene

**Current branch:** `integration-merge-attempt`
**Remote:** `git@github.com:EmanueleMusumeci/ContextMattersDemo.git`

Before final submission:
```bash
git checkout main
git merge integration-merge-attempt
git push origin main
```

Files to add to `.gitignore` before merge:
- `results_llmpp/` — large result dirs (or add to LFS)
- `data/llmpp/` — benchmark data
- `paper/main.aux`, `paper/main.pdf`, `paper/main.out` — build artifacts
- `key.sh` — API keys (should never be committed)

---

## 6. Deadline

Check: https://icaps26.icaps-conference.org/calls/demos/
