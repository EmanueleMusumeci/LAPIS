#!/usr/bin/env python3
"""
Run direct LLM baselines on IPC benchmark domains (blocksworld, storage, tyreworld, floortile).

Uses three frontier models:
- Gemini 3.1 Pro
- GPT-5.4
- Claude Opus 4.6

For each problem, the LLM receives:
1. Domain description (from domain.nl)
2. Problem description (from pN.nl)
3. Request to generate a plan

No PDDL formalization - direct NL-to-plan generation.
Results are validated using VAL where possible.
"""

import json
import os
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# API imports
import anthropic
import openai
from openai import OpenAI

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("WARNING: google-generativeai not installed. Gemini baselines will be skipped.")

# Pricing per 1M tokens (input, output)
# Using latest available models as of April 2026
MODEL_PRICING = {
    "gemini-3.1-pro-preview": (2.0, 12.0),    # Gemini 3.1 Pro (direct API)
    "google/gemini-3.1-pro-preview": (2.0, 12.0),  # Gemini 3.1 Pro (OpenRouter)
    "gpt-5.4": (2.5, 15.0),                    # GPT-5.4 (March 2026)
    "gpt-4o": (2.5, 10.0),                     # GPT-4o (fallback)
    "claude-opus-4-20250514": (15.0, 75.0),    # Claude Opus 4 (old)
    "claude-opus-4-6": (5.0, 25.0)             # Claude Opus 4.6 (Feb 2026)
}

DOMAINS = ["blocksworld", "storage", "tyreworld", "floortile"]
PROBLEMS_PER_DOMAIN = 20

def call_gemini(prompt: str, model: str = "gemini-3.1-pro-preview") -> Tuple[str, float]:
    """Call Gemini API and return (response, cost)."""
    if not GEMINI_AVAILABLE:
        return "", 0.0

    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model_obj = genai.GenerativeModel(model)

    response = model_obj.generate_content(prompt)
    text = response.text

    # Estimate tokens (rough approximation: 1 token ≈ 4 chars)
    input_tokens = len(prompt) / 4
    output_tokens = len(text) / 4

    input_price, output_price = MODEL_PRICING[model]
    cost = (input_tokens / 1_000_000 * input_price) + (output_tokens / 1_000_000 * output_price)

    return text, cost

def call_gpt(prompt: str, model: str = "gpt-5.4") -> Tuple[str, float]:
    """Call OpenAI GPT API and return (response, cost)."""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=4000
    )

    text = response.choices[0].message.content
    usage = response.usage

    input_price, output_price = MODEL_PRICING[model]
    cost = (usage.prompt_tokens / 1_000_000 * input_price) + (usage.completion_tokens / 1_000_000 * output_price)

    return text, cost

def call_claude(prompt: str, model: str = "claude-opus-4-6") -> Tuple[str, float]:
    """Call Anthropic Claude API and return (response, cost)."""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    response = client.messages.create(
        model=model,
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.content[0].text
    usage = response.usage

    input_price, output_price = MODEL_PRICING[model]
    cost = (usage.input_tokens / 1_000_000 * input_price) + (usage.output_tokens / 1_000_000 * output_price)

    return text, cost

def call_gemini_openrouter(prompt: str, model: str = "google/gemini-3.1-pro-preview") -> Tuple[str, float]:
    """Call Gemini via OpenRouter API and return (response, cost)."""
    client = OpenAI(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=4000
    )

    text = response.choices[0].message.content
    usage = response.usage

    input_price, output_price = MODEL_PRICING[model]
    cost = (usage.prompt_tokens / 1_000_000 * input_price) + (usage.completion_tokens / 1_000_000 * output_price)

    return text, cost

def extract_plan(response: str) -> List[str]:
    """Extract plan actions from LLM response.

    Looks for:
    - Numbered lists (1. action, 2. action)
    - Bullet points (- action, * action)
    - PDDL-style actions in parentheses
    """
    actions = []

    # Try to find PDDL-style actions: (action-name param1 param2)
    pddl_actions = re.findall(r'\([a-z_-]+(?:\s+[a-z0-9_-]+)*\)', response, re.IGNORECASE)
    if pddl_actions:
        return pddl_actions

    # Try numbered/bulleted lists
    lines = response.split('\n')
    for line in lines:
        line = line.strip()
        # Match: "1. action", "- action", "* action", etc.
        match = re.match(r'^(?:\d+[\.\)]\s*|[-*]\s*)(.+)$', line)
        if match:
            action = match.group(1).strip()
            if action and len(action) < 200:  # Sanity check
                actions.append(action)

    return actions

def validate_plan_with_val(domain_pddl: Path, problem_pddl: Path, actions: List[str]) -> bool:
    """Validate plan using VAL.

    Creates a temporary plan file and runs VAL validator.
    """
    if not actions:
        return False

    # Create plan file
    plan_file = Path("/tmp/baseline_plan.txt")
    with open(plan_file, 'w') as f:
        for action in actions:
            f.write(f"{action}\n")

    # Run VAL
    val_binary = Path("third-party/VAL/validate")
    if not val_binary.exists():
        return False

    try:
        import subprocess
        result = subprocess.run(
            [str(val_binary), str(domain_pddl), str(problem_pddl), str(plan_file)],
            capture_output=True,
            text=True,
            timeout=10
        )
        return "Plan valid" in result.stdout
    except Exception:
        return False

def run_baseline(model_name: str, call_fn, domains: List[str]) -> Dict:
    """Run baseline for a single model across all domains."""

    print(f"\n{'='*60}")
    print(f"Running {model_name}")
    print(f"{'='*60}\n")

    results = {}
    total_cost = 0.0

    for domain in domains:
        print(f"\n{domain.upper()}")
        print("-" * 40)

        domain_path = Path(f"third-party/llm-pddl/domains/{domain}")
        if not domain_path.exists():
            print(f"  WARNING: Domain not found: {domain_path}")
            continue

        # Read domain description
        domain_nl_file = domain_path / "domain.nl"
        if not domain_nl_file.exists():
            print(f"  WARNING: domain.nl not found")
            continue

        with open(domain_nl_file) as f:
            domain_description = f.read()

        domain_results = []

        for problem_id in range(1, PROBLEMS_PER_DOMAIN + 1):
            problem_nl_file = domain_path / f"p{problem_id:02d}.nl"
            problem_pddl_file = domain_path / f"p{problem_id:02d}.pddl"
            domain_pddl_file = domain_path / "domain.pddl"

            if not problem_nl_file.exists():
                print(f"  Problem {problem_id}: NOT FOUND")
                continue

            # Read problem description
            with open(problem_nl_file) as f:
                problem_description = f.read()

            # Construct prompt
            prompt = f"""You are a planning assistant. Given a domain description and a problem description, generate a valid plan.

DOMAIN DESCRIPTION:
{domain_description}

PROBLEM DESCRIPTION:
{problem_description}

Generate a plan as a sequence of actions that solves this problem. Output the plan as a numbered list or as PDDL-style actions in parentheses.
"""

            try:
                # Call LLM
                response, cost = call_fn(prompt)
                total_cost += cost

                # Extract plan
                actions = extract_plan(response)

                # Check if plan was generated
                plan_generated = len(actions) > 0

                # Try VAL validation if PDDL files exist
                val_success = False
                if plan_generated and domain_pddl_file.exists() and problem_pddl_file.exists():
                    val_success = validate_plan_with_val(domain_pddl_file, problem_pddl_file, actions)

                domain_results.append({
                    "problem_id": problem_id,
                    "success": val_success,
                    "plan_generated": plan_generated,
                    "plan_length": len(actions),
                    "cost": cost
                })

                status = "✓ VAL" if val_success else ("✓ GEN" if plan_generated else "✗ FAIL")
                print(f"  Problem {problem_id:2d}: {status} ({len(actions)} actions, ${cost:.4f})")

            except Exception as e:
                print(f"  Problem {problem_id:2d}: ✗ ERROR - {e}")
                domain_results.append({
                    "problem_id": problem_id,
                    "success": False,
                    "plan_generated": False,
                    "error": str(e)
                })

        # Calculate domain statistics
        val_successes = sum(1 for r in domain_results if r.get("success", False))
        gen_successes = sum(1 for r in domain_results if r.get("plan_generated", False))
        total = len(domain_results)

        val_rate = (val_successes / total * 100) if total > 0 else 0
        gen_rate = (gen_successes / total * 100) if total > 0 else 0

        results[domain] = {
            "problems": domain_results,
            "val_success_rate": val_rate,
            "gen_success_rate": gen_rate,
            "val_successes": val_successes,
            "gen_successes": gen_successes,
            "total": total
        }

        print(f"  Summary: VAL {val_successes}/{total} ({val_rate:.1f}%), GEN {gen_successes}/{total} ({gen_rate:.1f}%)")

    return {
        "model": model_name,
        "timestamp": datetime.now().isoformat(),
        "total_cost": total_cost,
        "results": results
    }

def main():
    print("=" * 60)
    print("IPC BASELINE EXPERIMENTS")
    print("=" * 60)
    print(f"Domains: {', '.join(DOMAINS)}")
    print(f"Problems per domain: {PROBLEMS_PER_DOMAIN}")
    print(f"Models: GPT-5.4, Claude Opus 4.6")
    print()

    # Check API keys
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set")
        return
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not set")
        return
    if not os.getenv("GEMINI_API_KEY"):
        print("WARNING: GEMINI_API_KEY not set - Gemini will be skipped")

    # Create output directory
    output_dir = Path("results_ipc_baselines")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run baselines
    baselines = []

    # Skip Gemini due to quota issues
    # if GEMINI_AVAILABLE and os.getenv("GEMINI_API_KEY"):
    #     gemini_results = run_baseline("gemini-3.1-pro-preview", call_gemini, DOMAINS)
    #     baselines.append(gemini_results)
    #     with open(output_dir / "gemini_3.1_pro_preview.json", 'w') as f:
    #         json.dump(gemini_results, f, indent=2)

    gpt_results = run_baseline("gpt-5.4", call_gpt, DOMAINS)
    baselines.append(gpt_results)
    with open(output_dir / "gpt_5.4.json", 'w') as f:
        json.dump(gpt_results, f, indent=2)

    claude_results = run_baseline("claude-opus-4-6", call_claude, DOMAINS)
    baselines.append(claude_results)
    with open(output_dir / "claude_opus_4_6.json", 'w') as f:
        json.dump(claude_results, f, indent=2)

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for baseline in baselines:
        model = baseline["model"]
        cost = baseline["total_cost"]
        print(f"\n{model}:")
        print(f"  Total cost: ${cost:.2f}")

        for domain in DOMAINS:
            if domain in baseline["results"]:
                dr = baseline["results"][domain]
                val_rate = dr["val_success_rate"]
                gen_rate = dr["gen_success_rate"]
                print(f"  {domain}: VAL {val_rate:.1f}%, GEN {gen_rate:.1f}%")

    print(f"\nResults saved to: {output_dir}/")

if __name__ == "__main__":
    main()
