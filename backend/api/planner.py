"""
planner.py — Run a classical planner on user-provided PDDL and return the plan.
"""
from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["planner"])

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class PlanRequest(BaseModel):
    domain_pddl: str
    problem_pddl: str
    planner: str = "up_fd"
    timeout: int = 60


class PlanResponse(BaseModel):
    success: bool
    plan: list[str] = []
    error: str = ""


@router.post("/plan", response_model=PlanResponse)
async def run_planner(req: PlanRequest) -> PlanResponse:
    """Run a classical planner on given PDDL domain + problem, return plan actions."""
    import sys
    if str(_REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT))

    from src.lapis.planner.low.planner_utils import plan_with_output
    from src.lapis.planner.low.pddl_verification import VAL_validate, translate_plan

    with tempfile.TemporaryDirectory() as tmp:
        domain_path = os.path.join(tmp, "domain.pddl")
        problem_path = os.path.join(tmp, "problem.pddl")
        plan_path = os.path.join(tmp, "plan.out")

        with open(domain_path, "w") as f:
            f.write(req.domain_pddl)
        with open(problem_path, "w") as f:
            f.write(req.problem_pddl)

        try:
            plan, pddlenv_err, planner_err, _ = await asyncio.to_thread(
                plan_with_output,
                domain_path, tmp, plan_path,
                planner_name=req.planner, timeout=req.timeout,
            )

            if plan is None:
                err = planner_err or pddlenv_err or "Planner returned no plan"
                return PlanResponse(success=False, error=err)

            # Translate and read plan
            translated = os.path.join(tmp, "plan_translated.txt")
            await asyncio.to_thread(translate_plan, plan_path, translated)

            try:
                with open(translated) as f:
                    actions = [
                        line.strip() for line in f
                        if line.strip() and not line.startswith(";")
                    ]
            except Exception:
                actions = [str(a) for a in plan]

            return PlanResponse(success=True, plan=actions)

        except Exception as exc:
            return PlanResponse(success=False, error=str(exc))
