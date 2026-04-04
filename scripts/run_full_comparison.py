"""
Master benchmark runner for the LAPIS multi-baseline comparison.

Runs all configured systems on all domains × all problems, saves results
incrementally to a single JSON file, and runs oracle validation.

Usage:
    # Run everything (minus nl2plan)
    python scripts/run_full_comparison.py \
        --systems direct_llm llmpp lapis_c lapis_d \
        --gt_dir data/llmpp/

    # Run only specific systems or domains
    python scripts/run_full_comparison.py \
        --systems lapis_d \
        --domains blocksworld barman \
        --max_problems 10

    # Resume a previously interrupted run (skips completed entries)
    python scripts/run_full_comparison.py --resume
"""

from __future__ import annotations

import json
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional

# Ensure repo root importable
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.run_direct_llm_baseline import run_direct_llm, load_nl_description
from scripts.oracle_validate import oracle_validate


# --- Configuration ---

ALL_SYSTEMS = [
    "direct_llm",
    "llmpp",        # LAPIS Condition B (GT domain, no refinement)
    "lapis_c",      # Full synthesis, VAL refinement only (skip_adequacy=True)
    "lapis_d",      # Full synthesis, VAL + adequacy check
]

ALL_DOMAINS = [
    "blocksworld", "barman", "storage", "termes",
    "grippers", "floortile", "tyreworld"
]

PROBLEMS_PER_DOMAIN = 20
TIMEOUT_SECONDS = 300

_NL_ROOT = _REPO_ROOT / "third-party" / "llm-pddl" / "domains"


# --- LAPIS Runner (Conditions B, C, D) ---

def _find_nl_file(gt_dir: str, domain: str, problem_id: int) -> Optional[str]:
    """Find the NL description (domain + problem NL) for a given domain/problem."""
    # Try third-party llm-pddl first (cleaner single-domain description)
    nl_candidates = [
        _REPO_ROOT / "third-party" / "llm-pddl" / "domains" / domain / f"p{problem_id:02d}.nl",
        _REPO_ROOT / "data" / "llmpp" / domain / f"p{problem_id:02d}" / "nl",
    ]
    for p in nl_candidates:
        if p.exists():
            return str(p)
    return None


def _load_nl_pair(gt_dir: str, domain: str, problem_id: int) -> tuple[str, str]:
    """Return (domain_nl, problem_nl) from the NL file."""
    # Domain-level description
    domain_nl_path = _NL_ROOT / domain / "domain.nl"
    domain_nl = domain_nl_path.read_text().strip() if domain_nl_path.exists() else ""

    # Problem-level description
    nl_path = Path(gt_dir) / domain / f"p{problem_id:02d}" / "nl"
    if not nl_path.exists():
        nl_path = _NL_ROOT / domain / f"p{problem_id:02d}.nl"
    problem_nl = nl_path.read_text().strip() if nl_path.exists() else ""
    return domain_nl, problem_nl


def run_lapis(domain: str, problem_id: int, condition: str, gt_dir: str) -> dict:
    """
    Run LAPIS under a specific experimental condition (B, C, or D).

    Condition B  → llmpp mode (GT domain, no generation, no adequacy)
    Condition C  → lapis mode, no adequacy check
    Condition D  → lapis mode with adequacy check (default)
    """
    from demo.runner import LAPISRunner

    # Map condition to runner flags
    method_map = {"B": "llmpp", "C": "lapis", "D": "lapis"}
    adequacy_map = {"B": True, "C": True, "D": False}  # skip_adequacy flags

    method = method_map[condition]
    skip_adequacy = adequacy_map[condition]

    domain_nl, problem_nl = _load_nl_pair(gt_dir, domain, problem_id)
    if not problem_nl:
        return {
            "system": f"lapis_{condition.lower()}",
            "domain": domain,
            "problem_id": problem_id,
            "llm_model": "claude-sonnet-4-6",
            "success_internal": False,
            "error": f"NL file not found for {domain}/p{problem_id:02d}",
        }

    start = time.time()

    try:
        from src.lapis.agents.claude import ClaudeAgent
        agent = ClaudeAgent(model="claude-sonnet-4-6")

        runner = LAPISRunner(
            agent=agent,
            domain_name=domain,
            tmp_dir=str(_REPO_ROOT / "results" / "full_comparison_tmp"),
        )
        result = runner.run(
            domain_nl=domain_nl,
            problem_nl=problem_nl,
            method=method,
            max_refinements=3,
            planner_name="pyperplan",
            planner_timeout=180,
            skip_adequacy=skip_adequacy,
        )
        elapsed = time.time() - start

        return {
            "system": f"lapis_{condition.lower()}",
            "domain": domain,
            "problem_id": problem_id,
            "llm_model": "claude-sonnet-4-6",
            "success_internal": result.success,
            "generated_domain_pddl": result.final_domain_pddl,
            "generated_problem_pddl": result.final_problem_pddl,
            "plan": result.plan_actions,
            "token_usage": None,  # TBD: wire token counting
            "time_seconds": elapsed,
            "refinement_iterations": result.refinements,
            "semantic_score": None,
            "success_oracle": None,
            "error": result.error_msg or None,
        }

    except Exception as e:
        return {
            "system": f"lapis_{condition.lower()}",
            "domain": domain,
            "problem_id": problem_id,
            "llm_model": "claude-sonnet-4-6",
            "success_internal": False,
            "success_oracle": False,
            "time_seconds": time.time() - start,
            "error": str(e)[:500],
        }


def run_direct_llm_problem(domain: str, problem_id: int, gt_dir: str) -> dict:
    """Wrapper that loads the .nl file and runs the direct LLM baseline."""
    import anthropic

    domain_nl, problem_nl = _load_nl_pair(gt_dir, domain, problem_id)
    nl_desc = f"{domain_nl}\n\n{problem_nl}".strip()

    if not nl_desc:
        return {
            "system": "direct_llm",
            "domain": domain,
            "problem_id": problem_id,
            "error": "NL file not found",
        }

    client = anthropic.Anthropic()
    result = run_direct_llm(nl_desc, client, "claude-sonnet-4-6")
    result.update({
        "domain": domain,
        "problem_id": problem_id,
        "llm_model": "claude-sonnet-4-6",
        "generated_domain_pddl": None,
        "generated_problem_pddl": None,
        "refinement_iterations": 0,
        "semantic_score": None,
        "success_oracle": None,
    })
    return result


# --- Dispatcher ---

SYSTEM_TO_RUNNER = {
    "direct_llm": lambda d, p, cfg: run_direct_llm_problem(d, p, cfg["gt_dir"]),
    "llmpp":      lambda d, p, cfg: run_lapis(d, p, "B", cfg["gt_dir"]),
    "lapis_c":    lambda d, p, cfg: run_lapis(d, p, "C", cfg["gt_dir"]),
    "lapis_d":    lambda d, p, cfg: run_lapis(d, p, "D", cfg["gt_dir"]),
}


# --- Result Management ---

def load_existing_results(path: str) -> list:
    """Load previously saved results for resume mode."""
    if Path(path).exists():
        with open(path) as f:
            data = json.load(f)
        return data.get("results", data) if isinstance(data, dict) else data
    return []


def is_already_done(existing: list, system: str, domain: str, pid: int) -> bool:
    """Check if a specific (system, domain, problem) combo was already run successfully."""
    for entry in existing:
        if (entry.get("system") == system and
                entry.get("domain") == domain and
                entry.get("problem_id") == pid and
                entry.get("error") is None):
            return True
    return False


def save_results(results: list, path: str, meta: dict):
    """Save results with metadata, creating parent dirs if needed."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump({"meta": meta, "results": results}, f, indent=2)


def print_summary(results: list, systems: list, domains: list):
    print("\n" + "=" * 70)
    print("SUMMARY: Oracle Success Rates")
    print("=" * 70)
    for system in systems:
        sys_results = [r for r in results if r.get("system") == system]
        for domain in domains:
            dom_results = [r for r in sys_results if r.get("domain") == domain]
            if dom_results:
                successes = sum(1 for r in dom_results if r.get("success_oracle"))
                total_d = len(dom_results)
                pct = successes / total_d * 100
                print(f"  {system:15s} | {domain:15s} | {successes:2d}/{total_d:2d} ({pct:5.1f}%)")


def main():
    parser = argparse.ArgumentParser(description="Run full LAPIS comparison benchmark")
    parser.add_argument("--gt_dir", default="data/llmpp/",
                        help="Base directory containing GT domain/problem PDDL files")
    parser.add_argument("--output", default="results/full_comparison.json")
    parser.add_argument("--systems", nargs="+", default=ALL_SYSTEMS)
    parser.add_argument("--domains", nargs="+", default=ALL_DOMAINS)
    parser.add_argument("--max_problems", type=int, default=PROBLEMS_PER_DOMAIN)
    parser.add_argument("--resume", action="store_true",
                        help="Skip already-completed entries")
    parser.add_argument("--skip_oracle", action="store_true",
                        help="Skip oracle validation (run it separately later)")
    args = parser.parse_args()

    meta = {
        "timestamp": datetime.now().isoformat(),
        "domains": args.domains,
        "problems_per_domain": args.max_problems,
        "systems": args.systems,
        "gt_dir": args.gt_dir,
    }

    cfg = {"gt_dir": args.gt_dir}

    # Load existing results for resume mode
    existing = load_existing_results(args.output) if args.resume else []
    results = list(existing)

    total = len(args.systems) * len(args.domains) * args.max_problems
    done = 0

    for system in args.systems:
        if system not in SYSTEM_TO_RUNNER:
            print(f"WARNING: Unknown system '{system}', skipping")
            continue

        runner_fn = SYSTEM_TO_RUNNER[system]

        for domain in args.domains:
            for pid in range(1, args.max_problems + 1):
                done += 1

                if args.resume and is_already_done(existing, system, domain, pid):
                    print(f"[{done}/{total}] {system}/{domain}/p{pid:02d} — SKIP")
                    continue

                print(f"[{done}/{total}] {system}/{domain}/p{pid:02d}...", end=" ", flush=True)

                try:
                    entry = runner_fn(domain, pid, cfg)
                except Exception as e:
                    print(f"ERROR: {e}")
                    entry = {
                        "system": system, "domain": domain,
                        "problem_id": pid, "error": str(e),
                        "success_oracle": False,
                    }

                # Oracle validation (inline, if plan exists)
                if not args.skip_oracle and entry.get("plan") and entry.get("success_oracle") is None:
                    gt_domain = f"{args.gt_dir}/{domain}/p{pid:02d}/domain.pddl"
                    gt_problem = f"{args.gt_dir}/{domain}/p{pid:02d}/problem.pddl"

                    if Path(gt_domain).exists() and Path(gt_problem).exists():
                        oracle = oracle_validate(gt_domain, gt_problem, entry["plan"])
                        entry["success_oracle"] = oracle["valid"]
                        entry["oracle_error"] = oracle.get("error")
                        entry["oracle_method"] = oracle.get("method")
                    else:
                        entry["success_oracle"] = False
                        entry["oracle_error"] = "GT PDDL files not found"

                status = "✅" if entry.get("success_oracle") else "❌"
                t = entry.get("time_seconds", 0) or 0
                print(f"{status} ({t:.1f}s)")

                # Replace if re-running a failed entry, else append
                results = [
                    r for r in results
                    if not (r.get("system") == system and
                            r.get("domain") == domain and
                            r.get("problem_id") == pid)
                ]
                results.append(entry)

                # Incremental save after EVERY problem
                save_results(results, args.output, meta)

    print_summary(results, args.systems, args.domains)
    print(f"\nAll results saved to {args.output}")


if __name__ == "__main__":
    main()
