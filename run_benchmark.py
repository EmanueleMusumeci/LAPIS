#!/usr/bin/env python3
"""
run_benchmark.py — CoSTL low-level planner benchmark on Lexicon problems.

Usage:
    python run_benchmark.py --domain blocksworld --batch_id data_2 --model gpt-4o
    python run_benchmark.py --domain babyai --batch_id data_1 --model claude-opus-4-6
    python run_benchmark.py --domain blocksworld --problems 100 102 104  # subset

Reads problems from:
    data/{domain}/{batch_id}/{problem_id}/nl            (NL description)
    data/{domain}/{batch_id}/{problem_id}/domain.pddl   (PDDL domain)
    data/{domain}/{batch_id}/{problem_id}/problem.pddl  (GT PDDL problem)

Results written to:
    results/benchmark_{domain}_{batch_id}_{model}/{timestamp}/
        results.csv          (one row per problem)
        summary.json         (aggregate stats)
        {problem_id}/manifold.json
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Ensure repo root is on path
sys.path.insert(0, str(Path(__file__).parent))


def discover_problems(data_dir: str, domain: str, batch_id: str) -> list:
    batch_path = Path(data_dir) / domain / batch_id
    if not batch_path.exists():
        raise FileNotFoundError(f"Batch directory not found: {batch_path}")
    problems = sorted(
        d.name for d in batch_path.iterdir()
        if d.is_dir() and d.name.isdigit() and (d / "nl").exists()
    )
    return problems


def build_summary(results_dir: str, domain: str, batch_id: str) -> dict:
    results_path = Path(results_dir)
    manifests = list(results_path.rglob("manifold.json"))

    total = len(manifests)
    planned = sum(1 for m in manifests if json.loads(m.read_text()).get("planning_successful"))
    valid = sum(1 for m in manifests if json.loads(m.read_text()).get("val_valid"))

    times = [json.loads(m.read_text())["timing"]["total_llm_s"] for m in manifests
             if "timing" in json.loads(m.read_text())]
    avg_time = round(sum(times) / len(times), 2) if times else 0.0

    plan_lens = [json.loads(m.read_text()).get("plan_length", 0) for m in manifests
                 if json.loads(m.read_text()).get("val_valid")]
    avg_plan_len = round(sum(plan_lens) / len(plan_lens), 1) if plan_lens else 0.0

    return {
        "domain": domain,
        "batch_id": batch_id,
        "total_problems": total,
        "planning_success": planned,
        "val_success": valid,
        "success_rate": round(valid / total, 3) if total else 0.0,
        "avg_llm_time_s": avg_time,
        "avg_plan_length": avg_plan_len,
    }


# Default batch IDs per domain (reflect the actual folder layout in data/)
DOMAIN_DEFAULTS = {
    "blocksworld": "data_2",
    "babyai": "data/data_1",   # data/babyai/data/data_1/{problem_id}/
    "logistics": "data_1",
    "sokoban": "data_1",
}


def main():
    parser = argparse.ArgumentParser(description="CoSTL low-level planner benchmark")
    parser.add_argument("--domain", default="blocksworld", help="Domain name (blocksworld or babyai)")
    parser.add_argument("--batch_id", default=None,
                        help="Batch ID subfolder (default: data_2 for blocksworld, data/data_1 for babyai)")
    parser.add_argument("--model", default="gpt-4o", help="LLM model name")
    parser.add_argument("--problems", nargs="*", default=None, help="Specific problem IDs; default: all")
    parser.add_argument("--pddl_gen_iterations", type=int, default=3, help="Max PDDL refinement iterations")
    parser.add_argument("--data_dir", default="data", help="Data directory (default: data/)")
    parser.add_argument("--results_dir", default="results", help="Results root directory")
    args = parser.parse_args()

    # Resolve batch_id default
    batch_id = args.batch_id or DOMAIN_DEFAULTS.get(args.domain, "data_2")

    # Discover problems
    problems = args.problems or discover_problems(args.data_dir, args.domain, batch_id)
    if not problems:
        print(f"No problems found in {args.data_dir}/{args.domain}/{batch_id}/")
        sys.exit(1)

    print(f"\nBenchmark: {args.domain}/{batch_id} | model={args.model} | {len(problems)} problems")
    print(f"Problems: {problems}\n")

    # Import after path setup to catch import errors early
    from src.costl.agents.gpt import GPTAgent
    from src.costl.agents.claude import ClaudeAgent
    from src.costl.pipelines.lexicon_low_level import LexiconLowLevelPipeline

    if args.model.startswith("claude"):
        agent = ClaudeAgent(model=args.model)
    else:
        agent = GPTAgent(model=args.model)

    experiment_name = f"benchmark_{args.domain}_{batch_id}_{args.model.replace('-', '_')}"

    pipeline = LexiconLowLevelPipeline(
        domain_name=args.domain,
        batch_id=batch_id,
        # LowLevelPlanningPipeline kwargs
        determine_possibility=False,
        prevent_impossibility=False,
        pddl_gen_iterations=args.pddl_gen_iterations,
        # BasePipeline kwargs
        agent=agent,
        base_dir=str(Path(__file__).parent),
        data_dir=args.data_dir,
        results_dir=args.results_dir,
        splits=problems,
        generate_domain=False,
        ground_in_sg=False,
    )

    # Override experiment name for clean output dir
    pipeline.experiment_name = experiment_name

    pipeline.run()

    # Generate summary
    run_results_dir = os.path.join(args.results_dir, experiment_name, pipeline.timestamp)
    summary = build_summary(run_results_dir, args.domain, batch_id)

    summary_path = Path(run_results_dir) / "summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n{'='*60}")
    print(f"BENCHMARK RESULTS: {args.domain}/{batch_id}")
    print(f"{'='*60}")
    print(f"  Total problems:    {summary['total_problems']}")
    print(f"  Planning success:  {summary['planning_success']}/{summary['total_problems']}")
    print(f"  VAL valid:         {summary['val_success']}/{summary['total_problems']} ({summary['success_rate']*100:.1f}%)")
    print(f"  Avg LLM time:      {summary['avg_llm_time_s']}s")
    print(f"  Avg plan length:   {summary['avg_plan_length']} steps")
    print(f"\nResults: {run_results_dir}")
    print(f"Summary: {summary_path}")


if __name__ == "__main__":
    main()
