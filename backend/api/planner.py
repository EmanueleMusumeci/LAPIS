"""
planner.py — Run a classical planner on user-provided PDDL and return the plan.
Also provides a simulate-steps endpoint to compute per-step state diffs.
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


class SimStepsRequest(BaseModel):
    domain_pddl: str
    problem_pddl: str
    plan: list[str]  # Already-computed plan actions


class StepState(BaseModel):
    action: str           # Normalized PDDL action string
    added: list[str]      # Facts added by this action
    removed: list[str]    # Facts removed by this action
    all_facts: list[str]  # All true facts after this action


class SimStepsResponse(BaseModel):
    success: bool
    init_facts: list[str] = []   # Facts true before any action
    goal_facts: list[str] = []   # Goal facts to achieve
    steps: list[StepState] = []
    goal_reached: bool = False
    error: str = ""


def _simulate_steps(domain_pddl: str, problem_pddl: str, plan: list[str]) -> SimStepsResponse:
    """Simulate plan step-by-step using unified_planning SequentialSimulator."""
    import sys
    if str(_REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT))

    try:
        from unified_planning.io import PDDLReader
        from unified_planning.shortcuts import SequentialSimulator, get_environment
        from unified_planning.plans import ActionInstance
        from src.lapis.utils.pddl_preprocessor import preprocess_pddl_for_up
    except ImportError as e:
        return SimStepsResponse(success=False, error=f"unified_planning not available: {e}")

    with tempfile.TemporaryDirectory() as tmp:
        domain_path = os.path.join(tmp, "domain.pddl")
        problem_path = os.path.join(tmp, "problem.pddl")
        with open(domain_path, "w") as f:
            f.write(domain_pddl)
        with open(problem_path, "w") as f:
            f.write(problem_pddl)

        try:
            try:
                dp, pp = preprocess_pddl_for_up(domain_path, problem_path)
            except Exception:
                dp, pp = domain_path, problem_path

            reader = PDDLReader()
            problem = reader.parse_problem(dp, pp)
            env = get_environment()
            action_map = {a.name: a for a in problem.actions}

            def _state_to_facts(state) -> list[str]:
                facts = []
                for fluent in problem.fluents:
                    for obj_combo in _iter_grounded(fluent, problem):
                        try:
                            val = state.get_value(
                                env.expression_manager.FluentExp(fluent, obj_combo)
                            )
                            if val.is_true():
                                args = " ".join(o.name for o in obj_combo)
                                facts.append(f"({fluent.name}{' ' + args if args else ''})")
                        except Exception:
                            pass
                return sorted(facts)

            def _iter_grounded(fluent, problem):
                from itertools import product
                type_lists = [
                    [o for o in problem.all_objects if problem.has_type(o.type) and o.type == p.type]
                    for p in fluent.signature
                ]
                if not type_lists:
                    yield ()
                    return
                for combo in product(*type_lists):
                    yield combo

            sim = SequentialSimulator(problem)
            state = sim.get_initial_state()
            init_facts = _state_to_facts(state)

            # Extract goal facts
            goal_facts = []
            try:
                goal_exp = problem.goals[0] if problem.goals else None
                if goal_exp:
                    sub_goals = [goal_exp] if not goal_exp.is_and() else list(goal_exp.args)
                    for g in sub_goals:
                        goal_facts.append(str(g).replace("Bool:", "").strip())
            except Exception:
                pass

            steps: list[StepState] = []

            for action_str in plan:
                clean = action_str.strip().lstrip("(").rstrip(")")
                parts = clean.split()
                if not parts:
                    continue
                a_name = parts[0].lower()
                param_names = parts[1:]

                if a_name not in action_map:
                    steps.append(StepState(action=action_str, added=[], removed=[], all_facts=_state_to_facts(state)))
                    continue

                action = action_map[a_name]
                params = []
                ok = True
                for p in param_names:
                    obj = next((o for o in problem.all_objects if o.name.lower() == p.lower()), None)
                    if obj is None:
                        ok = False
                        break
                    params.append(env.expression_manager.ObjectExp(obj))

                if not ok or not sim.is_applicable(state, ActionInstance(action, tuple(params))):
                    steps.append(StepState(action=action_str, added=[], removed=[], all_facts=_state_to_facts(state)))
                    continue

                prev_facts = set(_state_to_facts(state))
                state = sim.apply(state, ActionInstance(action, tuple(params)))
                new_facts = set(_state_to_facts(state))

                steps.append(StepState(
                    action=action_str,
                    added=sorted(new_facts - prev_facts),
                    removed=sorted(prev_facts - new_facts),
                    all_facts=sorted(new_facts),
                ))

            goal_reached = sim.is_goal(state)
            return SimStepsResponse(
                success=True,
                init_facts=init_facts,
                goal_facts=goal_facts,
                steps=steps,
                goal_reached=goal_reached,
            )

    except Exception as exc:
        return SimStepsResponse(success=False, error=str(exc))


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


@router.post("/simulate-steps", response_model=SimStepsResponse)
async def simulate_steps(req: SimStepsRequest) -> SimStepsResponse:
    """Simulate a plan step-by-step and return per-step state diffs."""
    return await asyncio.to_thread(_simulate_steps, req.domain_pddl, req.problem_pddl, req.plan)


# ─── Graphical frame rendering ────────────────────────────────────────────────

# Maps detected domain name → simulator class path
_DOMAIN_SIMULATOR = {
    "blocksworld": "blocksworld_simulator.BlocksworldSimulator",
    "gridworld":   "babyai_simulator.BabyAISimulator",
    "grippers":    "grippers_simulator.GrippersSimulator",
    "barman":      "barman_simulator.BarmanSimulator",
    "floortile":   "floortile_simulator.FloortileSimulator",
    "storage":     "storage_simulator.StorageSimulator",
    "termes":      "termes_simulator.TermesSimulator",
    "tyreworld":   "tyreworld_simulator.TyreworldSimulator",
}


class SimFramesRequest(BaseModel):
    domain_pddl: str
    problem_pddl: str
    plan: list[str]
    domain_name: str   # e.g. "blocksworld", "barman", …


class SimFramesResponse(BaseModel):
    success: bool
    frames: list[str] = []   # base64-encoded PNG, one per step (step 0 = init)
    error: str = ""


def _render_frames(domain_pddl: str, problem_pddl: str, plan: list[str], domain_name: str) -> SimFramesResponse:
    """Render per-step images using the domain-specific simulator."""
    import sys
    import base64
    import io
    if str(_REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT))

    sim_path = _DOMAIN_SIMULATOR.get(domain_name.lower())
    if not sim_path:
        return SimFramesResponse(success=False, error=f"No graphical simulator for domain '{domain_name}'")

    try:
        from unified_planning.shortcuts import get_environment
        from unified_planning.plans import ActionInstance

        mod_name, cls_name = sim_path.rsplit(".", 1)
        sim_mod = __import__(f"src.lapis.simulators.{mod_name}", fromlist=[cls_name])
        SimClass = getattr(sim_mod, cls_name)
    except Exception as e:
        return SimFramesResponse(success=False, error=f"Could not load simulator: {e}")

    with tempfile.TemporaryDirectory() as tmp:
        domain_path = os.path.join(tmp, "domain.pddl")
        problem_path = os.path.join(tmp, "problem.pddl")
        with open(domain_path, "w") as f:
            f.write(domain_pddl)
        with open(problem_path, "w") as f:
            f.write(problem_pddl)

        try:
            sim = SimClass()
            ok = sim.setup(domain_path, problem_path)
            if not ok:
                return SimFramesResponse(success=False, error="Simulator setup failed")

            sim.reset()

            def _img_to_b64(img) -> str | None:
                if img is None:
                    return None
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

            frames: list[str] = []

            # Frame 0: initial state
            init_img = sim.get_image(action_text=None)
            b64 = _img_to_b64(init_img)
            if b64:
                frames.append(b64)

            # Use the simulator's own problem to avoid object-identity mismatches
            # that happen when parsing a second time with a fresh PDDLReader.
            problem = sim.problem
            env = get_environment()
            action_map = {a.name: a for a in problem.actions}

            for action_str in plan:
                clean = action_str.strip().lstrip("(").rstrip(")")
                parts = clean.split()
                if not parts:
                    continue
                a_name = parts[0].lower()
                param_names = parts[1:]

                if a_name not in action_map:
                    frames.append(frames[-1] if frames else "")
                    continue

                action = action_map[a_name]
                params = []
                ok_params = True
                for p in param_names:
                    obj = next((o for o in problem.all_objects if o.name.lower() == p.lower()), None)
                    if obj is None:
                        ok_params = False
                        break
                    params.append(env.expression_manager.ObjectExp(obj))

                if ok_params:
                    try:
                        ai = ActionInstance(action, tuple(params))
                        sim.step(ai)
                    except Exception:
                        # Action not applicable in current state — render frame unchanged
                        pass

                frame_img = sim.get_image(action_text=clean)
                b64 = _img_to_b64(frame_img)
                frames.append(b64 if b64 else (frames[-1] if frames else ""))

            return SimFramesResponse(success=True, frames=frames)

        except Exception as e:
            return SimFramesResponse(success=False, error=str(e))


@router.post("/simulate-frames", response_model=SimFramesResponse)
async def simulate_frames(req: SimFramesRequest) -> SimFramesResponse:
    """Render per-step graphical frames using domain-specific simulator."""
    return await asyncio.to_thread(
        _render_frames, req.domain_pddl, req.problem_pddl, req.plan, req.domain_name
    )
