"""
Oracle plan validation against ground-truth PDDL domains.

Takes a plan (as a list of action strings or a plan file) and validates it
against the GT domain.pddl + GT problem.pddl using VAL or unified_planning.

This module is system-agnostic — it doesn't care which system produced the plan.

Usage as a library:
    from scripts.oracle_validate import oracle_validate
    result = oracle_validate("data/llmpp/blocksworld/p01/domain.pddl",
                             "data/llmpp/blocksworld/p01/problem.pddl",
                             plan_actions)

Usage as CLI:
    python scripts/oracle_validate.py single \
        --gt_domain data/llmpp/blocksworld/p01/domain.pddl \
        --gt_problem data/llmpp/blocksworld/p01/problem.pddl \
        --plan_file results/some_plan.txt
"""

import subprocess
import tempfile
import re
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class OracleResult:
    valid: bool
    method: str                          # "val" or "unified_planning"
    error: Optional[str] = None
    failed_at_step: Optional[int] = None
    failed_reason: Optional[str] = None

    def to_dict(self):
        return asdict(self)


# ---------- Method 1: VAL Validator (preferred) ----------

def validate_with_val(
    gt_domain_path: str,
    gt_problem_path: str,
    plan_actions: list[str],
    val_binary: str = "validate"
) -> OracleResult:
    """
    Use the VAL validator to check a plan against GT files.

    VAL expects a plan file in the format:
        (action-name arg1 arg2)
        (action-name arg3 arg4)
        ; cost = N (operator count)
    """
    # Write plan to a temp file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".plan", delete=False
    ) as f:
        for action in plan_actions:
            action = action.strip()
            if not action.startswith("("):
                action = f"({action})"
            f.write(action + "\n")
        plan_path = f.name

    try:
        cmd = [val_binary, gt_domain_path, gt_problem_path, plan_path]
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        output = proc.stdout + proc.stderr

        if "Plan valid" in output or "Successful plans" in output:
            return OracleResult(valid=True, method="val")

        # Try to extract failure details
        step_match = re.search(r"step (\d+)", output)
        failed_step = int(step_match.group(1)) if step_match else None

        return OracleResult(
            valid=False,
            method="val",
            error=output[:500],
            failed_at_step=failed_step,
            failed_reason=output[:200]
        )

    except FileNotFoundError:
        # VAL binary not found, fall back to unified_planning
        return validate_with_unified_planning(
            gt_domain_path, gt_problem_path, plan_actions
        )
    except subprocess.TimeoutExpired:
        return OracleResult(
            valid=False, method="val", error="VAL timed out after 30s"
        )
    finally:
        Path(plan_path).unlink(missing_ok=True)


# ---------- Method 2: Unified Planning (fallback) ----------

def validate_with_unified_planning(
    gt_domain_path: str,
    gt_problem_path: str,
    plan_actions: list[str]
) -> OracleResult:
    """
    Use the unified_planning library to validate a plan.
    Fallback if VAL binary is not available.
    """
    try:
        from unified_planning.io import PDDLReader
        from unified_planning.shortcuts import SequentialSimulator, get_environment
        from unified_planning.plans import ActionInstance

        reader = PDDLReader()
        problem = reader.parse_problem(gt_domain_path, gt_problem_path)
        action_map = {a.name: a for a in problem.actions}
        env = get_environment()

        sim = SequentialSimulator(problem)
        state = sim.get_initial_state()

        for i, action_str in enumerate(plan_actions):
            clean = action_str.strip().strip("()")
            parts = clean.split()
            if not parts:
                continue

            a_name = parts[0]
            # Normalize: replace underscores with hyphens (common mismatch)
            if a_name not in action_map:
                a_name_norm = a_name.replace("_", "-")
                if a_name_norm in action_map:
                    a_name = a_name_norm

            if a_name not in action_map:
                return OracleResult(
                    valid=False,
                    method="unified_planning",
                    error=f"Unknown action '{parts[0]}' at step {i+1}",
                    failed_at_step=i + 1
                )

            action = action_map[a_name]
            param_names = parts[1:]
            params = []
            for p in param_names:
                obj = next((o for o in problem.all_objects if o.name == p), None)
                if obj is None:
                    return OracleResult(
                        valid=False,
                        method="unified_planning",
                        error=f"Unknown object '{p}' in action at step {i+1}",
                        failed_at_step=i + 1
                    )
                params.append(env.expression_manager.ObjectExp(obj))

            ai = ActionInstance(action, tuple(params))
            if not sim.is_applicable(state, ai):
                unsatisfied = sim.get_unsatisfied_conditions(state, ai)
                return OracleResult(
                    valid=False,
                    method="unified_planning",
                    error=f"Not applicable at step {i+1}: {clean} | unsatisfied: {unsatisfied}",
                    failed_at_step=i + 1
                )
            state = sim.apply(state, ai)

        goal_reached = sim.is_goal(state)
        if not goal_reached:
            unsatisfied_goals = sim.get_unsatisfied_goals(state)
            return OracleResult(
                valid=False,
                method="unified_planning",
                error=f"Goal not reached: {unsatisfied_goals}"
            )
        return OracleResult(valid=True, method="unified_planning")

    except Exception as e:
        return OracleResult(
            valid=False,
            method="unified_planning",
            error=f"Validation error: {str(e)[:300]}"
        )


# ---------- Main Entry Point ----------

def oracle_validate(
    gt_domain_path: str,
    gt_problem_path: str,
    plan_actions: list[str]
) -> dict:
    """
    Validate a plan against ground truth.
    Tries VAL first, falls back to unified_planning.

    Args:
        gt_domain_path: path to ground truth domain.pddl
        gt_problem_path: path to ground truth problem.pddl
        plan_actions: list of action strings, e.g. ["(pick-up b1)", "(stack b1 b2)"]

    Returns:
        dict with keys: valid, method, error, failed_at_step, failed_reason
    """
    # Normalize action strings
    normalized = []
    for a in plan_actions:
        a = a.strip()
        if not a:
            continue
        # Remove any numbering (e.g., "1. (pick-up b1)" -> "(pick-up b1)")
        a = re.sub(r"^\d+\.\s*", "", a)
        normalized.append(a)

    if not normalized:
        return OracleResult(
            valid=False, method="none", error="Empty plan"
        ).to_dict()

    result = validate_with_val(gt_domain_path, gt_problem_path, normalized)
    return result.to_dict()


# ---------- Batch Processing ----------

def oracle_validate_results_file(
    results_path: str,
    gt_base_dir: str,
    output_path: str = None
):
    """
    Read a results JSON file (from any system), run oracle validation on
    each entry, and update the success_oracle field.

    The GT files are expected at:
        {gt_base_dir}/{domain}/p{problem_id:02d}/domain.pddl
        {gt_base_dir}/{domain}/p{problem_id:02d}/problem.pddl

    This matches the LAPIS data layout under data/llmpp/.
    """
    with open(results_path) as f:
        results = json.load(f)

    # Handle both list format and dict-with-results-key format
    if isinstance(results, dict):
        entries = results.get("results", results)
    else:
        entries = results

    validated_count = 0
    for entry in entries:
        if entry.get("success_oracle") is not None:
            continue  # already validated

        plan = entry.get("plan", [])
        if not plan:
            entry["success_oracle"] = False
            entry["oracle_error"] = "No plan produced"
            continue

        domain = entry["domain"]
        pid = entry["problem_id"]

        gt_domain = f"{gt_base_dir}/{domain}/p{pid:02d}/domain.pddl"
        gt_problem = f"{gt_base_dir}/{domain}/p{pid:02d}/problem.pddl"

        if not Path(gt_domain).exists() or not Path(gt_problem).exists():
            entry["success_oracle"] = False
            entry["oracle_error"] = f"GT files not found: {gt_domain}"
            continue

        oracle = oracle_validate(gt_domain, gt_problem, plan)
        entry["success_oracle"] = oracle["valid"]
        entry["oracle_error"] = oracle.get("error")
        entry["oracle_method"] = oracle.get("method")
        validated_count += 1

    out = output_path or results_path
    with open(out, "w") as f:
        json.dump(results, f, indent=2)

    # Print summary
    all_entries = entries
    validated = [e for e in all_entries if e.get("success_oracle") is not None]
    successes = sum(1 for e in validated if e["success_oracle"])
    print(f"Oracle validation: {successes}/{len(validated)} valid plans → {out}")


# ---------- CLI ----------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command")

    # Single plan validation
    single = sub.add_parser("single", help="Validate a single plan")
    single.add_argument("--gt_domain", required=True)
    single.add_argument("--gt_problem", required=True)
    single.add_argument("--plan_file", required=True)

    # Batch validation of a results file
    batch = sub.add_parser("batch", help="Validate all plans in a results file")
    batch.add_argument("--results", required=True, help="Path to results JSON")
    batch.add_argument("--gt_dir", required=True, help="Base directory for GT files")
    batch.add_argument("--output", default=None, help="Output path (default: overwrite input)")

    args = parser.parse_args()

    if args.command == "single":
        plan = Path(args.plan_file).read_text().strip().split("\n")
        result = oracle_validate(args.gt_domain, args.gt_problem, plan)
        print(json.dumps(result, indent=2))

    elif args.command == "batch":
        oracle_validate_results_file(args.results, args.gt_dir, args.output)

    else:
        parser.print_help()
