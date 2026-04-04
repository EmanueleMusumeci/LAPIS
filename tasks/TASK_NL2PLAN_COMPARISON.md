# Task: NL2Plan Baseline Comparison

**Priority**: Medium (nice-to-have for demo track, strengthens narrative)
**Estimated Time**: 4-8 hours (mostly waiting for experiments)
**Dependencies**: NL2Plan Docker image, API keys

---

## Objective

Run NL2Plan on the same LLM+P benchmark domains to enable direct architecture comparison. This addresses the fairness analysis concern that "comparing against LLM+P alone is insufficient."

---

## Background

NL2Plan (AAAI 2025) is the primary Tier 1 competitor for full NL-to-PDDL synthesis:
- 6-step pipeline: task parsing → type extraction → action extraction → predicate extraction → problem generation → validation
- Uses GPT-4o
- Docker available

The comparison evaluates **architecture**, not model capability (both are frontier-class).

---

## Setup

### 1. Get NL2Plan

```bash
# Clone repository
git clone https://github.com/mrlab-ai/NL2Plan.git /DATA/lapis/third-party/NL2Plan

# Or use Docker
docker pull mrlab/nl2plan:latest
```

### 2. Prepare Benchmark Data

NL2Plan needs NL task descriptions in its format. Convert from LLM+P format:

```python
# scripts/convert_to_nl2plan_format.py

import json
import os

LLMPP_DOMAINS = ["blocksworld", "barman", "storage", "termes", "grippers", "tyreworld", "floortile"]
LLMPP_PATH = "third-party/llm-pddl/domains"
OUTPUT_PATH = "third-party/NL2Plan/benchmarks/llmpp"

def convert_domain(domain_name):
    """Convert LLM+P domain to NL2Plan format."""
    domain_path = f"{LLMPP_PATH}/{domain_name}"
    output_path = f"{OUTPUT_PATH}/{domain_name}"
    os.makedirs(output_path, exist_ok=True)

    for i in range(1, 21):  # 20 problems per domain
        nl_file = f"{domain_path}/p{i:02d}.nl"
        if os.path.exists(nl_file):
            with open(nl_file) as f:
                nl_text = f.read()

            # NL2Plan expects JSON format
            problem = {
                "domain": domain_name,
                "problem_id": f"p{i:02d}",
                "natural_language": nl_text,
                "ground_truth_domain": f"{domain_path}/domain.pddl",
                "ground_truth_problem": f"{domain_path}/p{i:02d}.pddl"
            }

            with open(f"{output_path}/p{i:02d}.json", "w") as f:
                json.dump(problem, f, indent=2)

if __name__ == "__main__":
    for domain in LLMPP_DOMAINS:
        convert_domain(domain)
        print(f"Converted {domain}")
```

---

## Experiment Protocol

### Run NL2Plan on Each Domain

```bash
# Using Docker
docker run -v /DATA/lapis:/workspace mrlab/nl2plan:latest \
    python run_benchmark.py \
    --input /workspace/third-party/NL2Plan/benchmarks/llmpp/blocksworld \
    --output /workspace/results_nl2plan/blocksworld \
    --model gpt-4o

# Repeat for each domain
for domain in blocksworld barman storage termes grippers tyreworld floortile; do
    docker run -v /DATA/lapis:/workspace mrlab/nl2plan:latest \
        python run_benchmark.py \
        --input /workspace/third-party/NL2Plan/benchmarks/llmpp/$domain \
        --output /workspace/results_nl2plan/$domain \
        --model gpt-4o
done
```

### Collect Results

```bash
# scripts/collect_nl2plan_results.py

import json
import os
from pathlib import Path

def collect_results(results_dir="results_nl2plan"):
    results = {}

    for domain_dir in Path(results_dir).iterdir():
        if domain_dir.is_dir():
            domain = domain_dir.name
            total = 0
            valid = 0

            for result_file in domain_dir.glob("*/result.json"):
                total += 1
                with open(result_file) as f:
                    result = json.load(f)
                if result.get("val_valid", False):
                    valid += 1

            results[domain] = {
                "total": total,
                "valid": valid,
                "success_rate": valid / total * 100 if total > 0 else 0
            }

    return results

if __name__ == "__main__":
    results = collect_results()
    print("\nNL2Plan Results:")
    print("-" * 40)
    for domain, data in sorted(results.items()):
        print(f"{domain}: {data['valid']}/{data['total']} ({data['success_rate']:.0f}%)")
```

---

## Expected Results Table

After running, update `EXPERIMENTAL_NOTES_FOR_PAPER.md` with:

| Domain | LLM+P | NL2Plan | LAPIS/Synth | LAPIS/Adequacy |
|--------|:-----:|:-------:|:-----------:|:--------------:|
| Blocksworld | 100% | ??% | -- | -- |
| Storage | 100% | ??% | 90% | 85% |
| Termes | 100% | ??% | 100% | 100% |
| Grippers | 100% | ??% | -- | 100% |
| Tyreworld | 95% | ??% | 75% | 65% |
| Floortile | -- | ??% | 94% | 88% |

---

## Paper Integration

If NL2Plan results are ready before deadline:

**In Related Work:**
> "NL2Plan (Gestrin et al., AAAI 2025) introduced a 6-step pipeline for full NL-to-PDDL synthesis. We compare directly against NL2Plan on the LLM+P benchmark, using their published Docker image with GPT-4o."

**In Results:**
> "Table 1 shows that LAPIS achieves comparable or higher success rates than NL2Plan on X/Y domains, despite using a simpler architecture with fewer pipeline stages."

If NOT ready before deadline:

**In Future Work:**
> "We are conducting an extended comparison against NL2Plan and other recent full-synthesis systems; preliminary results suggest competitive performance."

---

## Fallback if NL2Plan Doesn't Work

If Docker image issues or API problems:
1. Don't block submission
2. Use the existing LLM+P comparison as primary
3. Cite NL2Plan in related work without direct comparison
4. Frame as: "Direct comparison with NL2Plan is ongoing work"

---

## Model Difference Justification

If reviewers ask about GPT-4o vs Claude Sonnet 4.6:

> "Both NL2Plan and LAPIS use frontier-class LLMs from the same capability tier. NL2Plan was designed and optimized for OpenAI models; running it through a proxy to Claude would introduce confounds. The LLM+P baseline within LAPIS uses the same Claude Sonnet 4.6 engine, ensuring fair internal comparison. Our evaluation assesses architecture, not model capability."

---

## Success Criteria

1. NL2Plan runs on all 7 domains without crashing
2. Results collected in consistent format
3. Table updated in EXPERIMENTAL_NOTES
4. Paper text updated with comparison (or fallback text)

---

## What NOT To Do

- Don't modify NL2Plan code (use as-is for fair comparison)
- Don't run with Claude (use their default GPT-4o)
- Don't block paper submission on this comparison
- Don't cherry-pick domains where LAPIS wins
