from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple
import json
import re
import shutil


@dataclass
class PerturbationExample:
    perturbation_type: str
    description: str
    domain_pddl: str
    problem_pddl: str


class PerturbationAgent:
    """Generate deterministic negative PDDL examples for verification QA.

    The generator creates three classes of perturbations from a valid pair:
    - GOAL_UNREACHABLE
    - PRECONDITION_CONFLICT
    - TYPE_MISMATCH
    """

    GOAL_UNREACHABLE = "GOAL_UNREACHABLE"
    PRECONDITION_CONFLICT = "PRECONDITION_CONFLICT"
    TYPE_MISMATCH = "TYPE_MISMATCH"

    def generate_perturbations(self, domain_pddl: str, problem_pddl: str) -> List[PerturbationExample]:
        perturbations: List[PerturbationExample] = []

        pert_domain, pert_problem = self._goal_unreachable(domain_pddl, problem_pddl)
        perturbations.append(
            PerturbationExample(
                perturbation_type=self.GOAL_UNREACHABLE,
                description="Rewrites the goal to a predicate not producible by any action.",
                domain_pddl=pert_domain,
                problem_pddl=pert_problem,
            )
        )

        pert_domain, pert_problem = self._precondition_conflict(domain_pddl, problem_pddl)
        perturbations.append(
            PerturbationExample(
                perturbation_type=self.PRECONDITION_CONFLICT,
                description="Injects a contradictory precondition in an action schema.",
                domain_pddl=pert_domain,
                problem_pddl=pert_problem,
            )
        )

        pert_domain, pert_problem = self._type_mismatch(domain_pddl, problem_pddl)
        perturbations.append(
            PerturbationExample(
                perturbation_type=self.TYPE_MISMATCH,
                description="Changes object typing so required action parameter types are missing.",
                domain_pddl=pert_domain,
                problem_pddl=pert_problem,
            )
        )

        return perturbations

    def build_validation_dataset(
        self,
        source_root: str | Path,
        output_root: str | Path,
        domains: List[str] | None = None,
        max_per_domain: int = 1,
    ) -> Dict[str, int]:
        source_root = Path(source_root)
        output_root = Path(output_root)

        positive_root = output_root / "positive"
        negative_root = output_root / "negative"
        positive_root.mkdir(parents=True, exist_ok=True)
        negative_root.mkdir(parents=True, exist_ok=True)

        domain_names = domains or sorted([p.name for p in source_root.iterdir() if p.is_dir()])
        summary = {
            "positive_pairs": 0,
            "negative_pairs": 0,
            "domains": len(domain_names),
        }

        for domain_name in domain_names:
            domain_dir = source_root / domain_name
            if not domain_dir.exists() or not domain_dir.is_dir():
                continue

            problem_dirs = sorted([p for p in domain_dir.iterdir() if p.is_dir()])[:max_per_domain]
            for problem_dir in problem_dirs:
                domain_file = problem_dir / "domain.pddl"
                problem_file = problem_dir / "problem.pddl"
                if not domain_file.exists() or not problem_file.exists():
                    continue

                problem_id = problem_dir.name
                positive_target = positive_root / domain_name / problem_id
                negative_target = negative_root / domain_name / problem_id
                positive_target.mkdir(parents=True, exist_ok=True)
                negative_target.mkdir(parents=True, exist_ok=True)

                shutil.copy2(domain_file, positive_target / "domain.pddl")
                shutil.copy2(problem_file, positive_target / "problem.pddl")
                summary["positive_pairs"] += 1

                domain_pddl = domain_file.read_text()
                problem_pddl = problem_file.read_text()
                perturbations = self.generate_perturbations(domain_pddl, problem_pddl)

                for item in perturbations:
                    neg_dir = negative_target / item.perturbation_type.lower()
                    neg_dir.mkdir(parents=True, exist_ok=True)
                    (neg_dir / "domain.pddl").write_text(item.domain_pddl)
                    (neg_dir / "problem.pddl").write_text(item.problem_pddl)
                    (neg_dir / "metadata.json").write_text(
                        json.dumps(
                            {
                                "type": item.perturbation_type,
                                "description": item.description,
                                "source_domain": domain_name,
                                "source_problem": problem_id,
                            },
                            indent=2,
                        )
                    )
                    summary["negative_pairs"] += 1

        (output_root / "summary.json").write_text(json.dumps(summary, indent=2))
        return summary

    def _goal_unreachable(self, domain_pddl: str, problem_pddl: str) -> Tuple[str, str]:
        goal_match = re.search(r"\(:goal([\s\S]*?)\)\s*\)\s*$", problem_pddl, flags=re.IGNORECASE)
        if not goal_match:
            return domain_pddl, problem_pddl + "\n; perturbation: goal_unreachable"

        goal_block = goal_match.group(1)
        pred_match = re.search(r"\(([^\s\)]+)", goal_block)
        if not pred_match:
            return domain_pddl, problem_pddl + "\n; perturbation: goal_unreachable"

        pred_name = pred_match.group(1)
        unreachable_pred = f"unreachable_{pred_name}"
        updated_goal_block = goal_block.replace(f"({pred_name}", f"({unreachable_pred}", 1)
        updated_problem = problem_pddl.replace(goal_block, updated_goal_block, 1)
        return domain_pddl, updated_problem

    def _precondition_conflict(self, domain_pddl: str, problem_pddl: str) -> Tuple[str, str]:
        marker = "(conflict_precond_marker)"
        pattern = re.compile(r":precondition\s*\(and", re.IGNORECASE)
        if not pattern.search(domain_pddl):
            return domain_pddl + "\n; perturbation: precondition_conflict", problem_pddl

        updated_domain = pattern.sub(f":precondition (and {marker}", domain_pddl, count=1)
        return updated_domain, problem_pddl

    def _type_mismatch(self, domain_pddl: str, problem_pddl: str) -> Tuple[str, str]:
        objects_match = re.search(r"\(:objects([\s\S]*?)\)\s*\(:init", problem_pddl, flags=re.IGNORECASE)
        if not objects_match:
            return domain_pddl, problem_pddl + "\n; perturbation: type_mismatch"

        objects_block = objects_match.group(1)
        typed_group_match = re.search(r"([a-zA-Z0-9_\-\s]+)-\s*([a-zA-Z0-9_-]+)", objects_block)
        if not typed_group_match:
            return domain_pddl, problem_pddl + "\n; perturbation: type_mismatch"

        object_list = typed_group_match.group(1).strip().split()
        original_type = typed_group_match.group(2)
        if len(object_list) <= 1:
            return domain_pddl, problem_pddl + "\n; perturbation: type_mismatch"

        # Move all objects away from the original type so action parameters of
        # that type become ungrounded.
        replacement = f"{' '.join(object_list)} - mismatch_type"

        updated_objects_block = objects_block.replace(typed_group_match.group(0), replacement, 1)
        updated_problem = problem_pddl.replace(objects_block, updated_objects_block, 1)
        return domain_pddl, updated_problem
