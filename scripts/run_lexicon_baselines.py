#!/usr/bin/env python3
"""
Run direct LLM baselines on Lexicon benchmark.

Runs direct LLM planning (no PDDL formalization) on:
- Blocksworld (20 problems)
- Logistics (20 problems, subset of 30)
- Sokoban (20 problems, subset of 30)
- BabyAI (20 problems)

Models: gemini-3.1-pro, gpt-5.4, claude-opus-4.6
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime

def call_gemini(prompt, model="gemini-3.1-pro"):
    """Call Google Gemini API."""
    import google.generativeai as genai

    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY not set")

    genai.configure(api_key=api_key)
    model_obj = genai.GenerativeModel(model)

    response = model_obj.generate_content(prompt)

    # Estimate cost (Gemini 3.1 Pro: $2/M in, $12/M out)
    input_tokens = len(prompt.split()) * 1.3  # rough estimate
    output_tokens = len(response.text.split()) * 1.3
    cost = (input_tokens / 1_000_000 * 2.0) + (output_tokens / 1_000_000 * 12.0)

    return response.text, cost

def call_gpt(prompt, model="gpt-5.4"):
    """Call OpenAI GPT API."""
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4000
    )

    # Extract cost from usage
    usage = response.usage
    cost = (usage.prompt_tokens / 1_000_000 * 2.5) + (usage.completion_tokens / 1_000_000 * 15.0)

    return response.choices[0].message.content, cost

def call_claude(prompt, model="claude-opus-4-6"):
    """Call Anthropic Claude API."""
    import anthropic

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    response = client.messages.create(
        model=model,
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )

    # Calculate cost (Opus 4.6: $5/M in, $25/M out)
    usage = response.usage
    cost = (usage.input_tokens / 1_000_000 * 5.0) + (usage.output_tokens / 1_000_000 * 25.0)

    return response.content[0].text, cost

def create_planning_prompt(domain_name, nl_description):
    """Create direct planning prompt (no PDDL)."""
    return f"""You are an AI planning assistant. Given a planning problem description, generate a step-by-step plan to achieve the goal.

Domain: {domain_name}

Problem Description:
{nl_description}

Generate a concrete, executable plan as a numbered list of actions. Each action should be clear and specific.

Plan:"""

def verify_plan(plan_text, goal_description):
    """Simple heuristic verification of plan."""
    # Very basic: check if plan is non-empty and has numbered steps
    lines = [l.strip() for l in plan_text.split('\n') if l.strip()]
    has_numbers = any(l[0].isdigit() for l in lines if l)
    has_content = len(lines) >= 3

    return has_numbers and has_content

def run_baseline(model_name, model_func):
    """Run baseline on all domains."""

    # Domain configuration
    domains = {
        "blocksworld": range(1, 21),
        "logistics": range(1, 21),
        "sokoban": range(1, 21),
        "babyai": range(1, 21)
    }

    lexicon_path = Path("third-party/lexicon_neurips/domains")
    if not lexicon_path.exists():
        print(f"ERROR: Lexicon path not found: {lexicon_path}")
        print("Please ensure third-party/lexicon_neurips is properly set up")
        return

    output_dir = Path(f"results_lexicon_standardized/baselines/{model_name}")
    output_dir.mkdir(parents=True, exist_ok=True)

    results = {}
    total_cost = 0

    print("=" * 60)
    print(f"Running Baseline: {model_name}")
    print("=" * 60)
    print(f"Output: {output_dir}")
    print()

    for domain_name, problem_range in domains.items():
        print(f"\n{'='*60}")
        print(f"Domain: {domain_name}")
        print(f"{'='*60}\n")

        domain_results = []
        domain_path = lexicon_path / domain_name

        if not domain_path.exists():
            print(f"WARNING: Domain path not found: {domain_path}")
            continue

        for problem_id in problem_range:
            print(f"\nProblem {problem_id}/20:", end=" ")

            # Find problem directory
            problem_dirs = list(domain_path.glob(f"*_{problem_id}"))
            if not problem_dirs:
                print(f"NOT FOUND")
                continue

            problem_dir = problem_dirs[0]
            nl_file = problem_dir / "description.txt"

            if not nl_file.exists():
                print(f"NO DESCRIPTION")
                continue

            # Read NL description
            with open(nl_file) as f:
                nl_description = f.read()

            try:
                start_time = time.time()

                # Create prompt and call model
                prompt = create_planning_prompt(domain_name, nl_description)
                plan_text, cost = model_func(prompt)

                elapsed = time.time() - start_time

                # Verify plan (basic heuristic)
                success = verify_plan(plan_text, nl_description)

                domain_results.append({
                    "problem_id": problem_id,
                    "success": success,
                    "cost": cost,
                    "time": elapsed,
                    "plan_length": len(plan_text.split('\n'))
                })

                total_cost += cost

                print(f"{'✓' if success else '✗'} ${cost:.4f} {elapsed:.1f}s")

                # Save individual result
                problem_output = output_dir / domain_name / f"problem_{problem_id}.json"
                problem_output.parent.mkdir(parents=True, exist_ok=True)
                with open(problem_output, 'w') as f:
                    json.dump({
                        "problem_id": problem_id,
                        "success": success,
                        "cost": cost,
                        "time": elapsed,
                        "plan": plan_text
                    }, f, indent=2)

            except Exception as e:
                print(f"ERROR: {e}")
                domain_results.append({
                    "problem_id": problem_id,
                    "success": False,
                    "error": str(e)
                })

        # Calculate domain statistics
        successes = sum(1 for r in domain_results if r.get("success", False))
        total = len(domain_results)
        success_rate = (successes / total * 100) if total > 0 else 0

        results[domain_name] = {
            "problems": domain_results,
            "success_rate": success_rate,
            "successes": successes,
            "total": total
        }

        print(f"\n{domain_name.upper()} Summary: {successes}/{total} ({success_rate:.1f}%)")

    # Save summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "model": model_name,
        "total_cost": total_cost,
        "results": results
    }

    summary_file = output_dir / "summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n{'='*60}")
    print("COMPLETE")
    print(f"{'='*60}")
    print(f"Total cost: ${total_cost:.2f}")
    print(f"Summary: {summary_file}")

def main():
    parser = argparse.ArgumentParser(description="Run Lexicon baseline models")
    parser.add_argument("--model", required=True,
                       choices=["gemini-3.1-pro", "gpt-5.4", "claude-opus-4.6"],
                       help="Model to run")
    args = parser.parse_args()

    model_map = {
        "gemini-3.1-pro": ("gemini-3.1-pro", lambda p: call_gemini(p, "gemini-3.1-pro")),
        "gpt-5.4": ("gpt-5.4", lambda p: call_gpt(p, "gpt-5.4")),
        "claude-opus-4.6": ("claude-opus-4.6", lambda p: call_claude(p, "claude-opus-4-6"))
    }

    model_name, model_func = model_map[args.model]
    run_baseline(model_name, model_func)

if __name__ == "__main__":
    main()
