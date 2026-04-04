"""
Baseline: Direct LLM planning without PDDL.

For each problem .nl file, sends the NL description to the LLM and asks
it to produce a plan as a sequence of grounded actions. Then validates
the plan against the GT oracle domain.

Usage:
    python scripts/run_direct_llm_baseline.py \
        --domains_dir third-party/llm-pddl/domains/ \
        --output results/direct_llm_results.json \
        --model claude-sonnet-4-6
"""

import anthropic
import json
import re
import time
import argparse
from pathlib import Path

# ---------- Prompt Templates ----------

PLAN_PROMPT = """You are solving a planning problem described in natural language.

TASK DESCRIPTION:
{nl_description}

Think step by step:
1. Identify the initial state (what is true right now).
2. Identify the goal (what needs to be true).
3. Figure out what sequence of actions transforms the initial state into the goal.

Then output your plan as a sequence of PDDL-style actions, one per line, like:
(action-name arg1 arg2 ...)

Use the exact object names from the task description. Output ONLY the plan
actions after your reasoning, inside a PLAN block:

[PLAN]
(action1 arg1 arg2)
(action2 arg3 arg4)
...
[END]"""


# ---------- Core Logic ----------

def load_nl_description(nl_path: str) -> str:
    """Load a .nl file and return its content."""
    return Path(nl_path).read_text().strip()


def extract_plan_from_response(response_text: str) -> list[str]:
    """
    Parse the LLM's response to extract the plan actions.

    Looks for a [PLAN]...[END] block first. Falls back to extracting
    any lines matching the (action-name args...) pattern.
    """
    # Try to find delimited plan block
    plan_match = re.search(
        r'\[PLAN\]\s*\n(.*?)\n\s*\[END\]',
        response_text,
        re.DOTALL
    )

    if plan_match:
        plan_text = plan_match.group(1)
    else:
        # Fallback: use everything after the last occurrence of "PLAN"
        plan_text = response_text

    # Extract lines that look like PDDL actions: (word word ...)
    actions = re.findall(r'\([\w-]+(?:\s+[\w-]+)*\)', plan_text)
    return actions


def run_direct_llm(
    nl_description: str,
    client: anthropic.Anthropic,
    model: str
) -> dict:
    """Run the LLM on a single planning problem and parse its output."""
    start = time.time()

    response = client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": PLAN_PROMPT.format(nl_description=nl_description)
        }]
    )

    elapsed = time.time() - start
    raw = response.content[0].text
    actions = extract_plan_from_response(raw)

    return {
        "system": "direct_llm",
        "raw_output": raw,
        "plan": actions,
        "time_seconds": elapsed,
        "token_usage": response.usage.input_tokens + response.usage.output_tokens,
    }


# ---------- Main ----------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--domains_dir", required=True)
    parser.add_argument("--output", default="results/direct_llm_results.json")
    parser.add_argument("--model", default="claude-sonnet-4-6")
    parser.add_argument("--domains", nargs="+",
                        default=["blocksworld", "barman", "storage", "termes",
                                 "grippers", "floortile", "tyreworld"])
    parser.add_argument("--max_problems", type=int, default=20)
    args = parser.parse_args()

    client = anthropic.Anthropic()
    all_results = []

    # Load existing results for resume support
    output_path = Path(args.output)
    if output_path.exists():
        with open(output_path) as f:
            all_results = json.load(f)
        existing_keys = {
            (r["domain"], r.get("problem_id")) for r in all_results
        }
        print(f"Resuming: {len(all_results)} existing results loaded.")
    else:
        existing_keys = set()

    for domain in args.domains:
        domain_dir = Path(args.domains_dir) / domain
        nl_files = sorted(domain_dir.glob("*.nl"))[:args.max_problems]

        for i, nl_file in enumerate(nl_files, start=1):
            if (domain, i) in existing_keys:
                print(f"[direct_llm] {domain}/p{i:02d} — SKIP (already done)")
                continue

            print(f"[direct_llm] {domain}/p{i:02d}...", end=" ", flush=True)

            nl_desc = load_nl_description(str(nl_file))
            result = run_direct_llm(nl_desc, client, args.model)

            result.update({
                "domain": domain,
                "problem_id": i,
                "llm_model": args.model,
                # Oracle validation will be added by task_4_oracle_validator
                "success_oracle": None,
                "generated_domain_pddl": None,
                "generated_problem_pddl": None,
                "refinement_iterations": 0,
                "semantic_score": None,
                "error": None,
            })

            n_actions = len(result["plan"])
            print(f"{n_actions} actions parsed, {result['time_seconds']:.1f}s")

            all_results.append(result)

            # Save incrementally
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(all_results, f, indent=2)

    print(f"\nDone. {len(all_results)} results saved to {args.output}")


if __name__ == "__main__":
    main()
