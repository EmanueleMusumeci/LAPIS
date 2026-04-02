"""
runner.py — LAPISRunner: executes the LAPIS planning pipeline with event callbacks.

Two modes:
  - LAPIS  : full pipeline (domain gen → adequacy → problem gen → plan → refine)
  - LLM+P  : GT domain injected, skip domain gen + adequacy, 0 refinements
  - MOCK   : no LLM calls; returns hardcoded sample data for UI testing

Set env var LAPIS_DEMO_MOCK=1 to activate mock mode.
"""

from __future__ import annotations

import os
import sys
import time
import tempfile
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

# Ensure src/ is importable regardless of cwd
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

MOCK_MODE = os.environ.get("LAPIS_DEMO_MOCK", "").strip() == "1"

# ─── Data structures ─────────────────────────────────────────────────────────

@dataclass
class StageResult:
    name: str
    status: str = "pending"   # pending | running | done | error | skipped
    duration: float = 0.0
    domain_pddl: str = ""
    problem_pddl: str = ""
    adequacy_analysis: str = ""
    domain_amended: bool = False
    problem_amended: bool = False
    schema_block: str = ""
    val_log: str = ""
    plan_actions: list = field(default_factory=list)
    refinement_history: list = field(default_factory=list)
    error_msg: str = ""
    # CoT sub-steps for adequacy (list of {"step": int, "label": str, "content": str})
    cot_steps: list = field(default_factory=list)


@dataclass
class RunResult:
    success: bool = False
    stages: list = field(default_factory=list)
    final_domain_pddl: str = ""
    final_problem_pddl: str = ""
    plan_actions: list = field(default_factory=list)
    plan_file_path: str = ""
    domain_file_path: str = ""
    problem_file_path: str = ""
    total_time: float = 0.0
    refinements: int = 0
    method: str = "lapis"   # "lapis" or "llmpp"
    error_msg: str = ""


# ─── Mock data ────────────────────────────────────────────────────────────────

MOCK_DOMAIN = """(define (domain blocksworld-4ops)
  (:requirements :strips)
  (:predicates
    (clear ?x)
    (on-table ?x)
    (arm-empty)
    (holding ?x)
    (on ?x ?y))

  (:action pickup
    :parameters (?ob)
    :precondition (and (clear ?ob) (on-table ?ob) (arm-empty))
    :effect (and (holding ?ob) (not (clear ?ob)) (not (on-table ?ob))
                 (not (arm-empty))))

  (:action putdown
    :parameters (?ob)
    :precondition (holding ?ob)
    :effect (and (clear ?ob) (arm-empty) (on-table ?ob)
                 (not (holding ?ob))))

  (:action stack
    :parameters (?ob ?underob)
    :precondition (and (clear ?underob) (holding ?ob))
    :effect (and (arm-empty) (clear ?ob) (on ?ob ?underob)
                 (not (clear ?underob)) (not (holding ?ob))))

  (:action unstack
    :parameters (?ob ?underob)
    :precondition (and (on ?ob ?underob) (clear ?ob) (arm-empty))
    :effect (and (holding ?ob) (clear ?underob)
                 (not (on ?ob ?underob)) (not (clear ?ob)) (not (arm-empty)))))
"""

MOCK_PROBLEM = """(define (problem BW-rand-3)
  (:domain blocksworld-4ops)
  (:objects b1 b2 b3)
  (:init
    (arm-empty)
    (on-table b1)
    (on b3 b1)
    (on b2 b3)
    (clear b2))
  (:goal
    (and (on b2 b3) (on b3 b1))))
"""

MOCK_PLAN = [
    "(unstack b2 b3)",
    "(putdown b2)",
    "(unstack b3 b1)",
    "(stack b3 b1)",
    "(pickup b2)",
    "(stack b2 b3)",
]


def _mock_run(
    method: str,
    on_stage_update: Optional[Callable[[StageResult], None]],
    tmp_dir: str,
) -> RunResult:
    """Return fabricated results without any real LLM or planner calls."""

    def _emit(sr: StageResult):
        if on_stage_update:
            on_stage_update(sr)

    stages: list[StageResult] = []

    stage_specs = [
        ("Domain Generation", 0.6),
        ("Domain Adequacy Check", 1.1),
        ("Problem Generation", 0.5),
        ("Planning + Refinement", 0.8),
    ]
    if method == "llmpp":
        stage_specs = [
            ("Domain Generation", 0.0),
            ("Problem Generation", 0.4),
            ("Planning + Refinement", 0.5),
        ]

    for name, dur in stage_specs:
        sr = StageResult(name=name, status="running")
        _emit(sr)
        time.sleep(min(dur, 0.3))   # brief pause for UI effect

        if name == "Domain Generation":
            if method == "llmpp":
                sr.status = "skipped"
                sr.domain_pddl = MOCK_DOMAIN
                sr.adequacy_analysis = "Using ground-truth domain (LLM+P mode)."
            else:
                sr.status = "done"
                sr.domain_pddl = MOCK_DOMAIN
        elif name == "Domain Adequacy Check":
            sr.status = "done"
            sr.adequacy_analysis = "No critical gaps found. Domain predicates cover all observed facts."
            sr.domain_amended = False
            sr.cot_steps = [
                {"step": 1, "label": "Predicate Extraction", "content": "PREDICATE: clear | PARAMS: ?x\nPREDICATE: on-table | PARAMS: ?x\nPREDICATE: arm-empty | PARAMS: (none)\nPREDICATE: holding | PARAMS: ?x\nPREDICATE: on | PARAMS: ?x ?y"},
                {"step": 2, "label": "Gap Analysis",         "content": "MAPPED: 'b2 is on top of b3' → (on b2 b3)\nMAPPED: 'b3 is on top of b1' → (on b3 b1)\nMAPPED: 'arm is empty' → (arm-empty)\nCRITICAL_GAPS: 0\nTOTAL_OBSERVATIONS: 5"},
                {"step": 3, "label": "Amendment",            "content": "No amendment needed — domain is adequate."},
            ]
        elif name == "Problem Generation":
            sr.status = "done"
            sr.problem_pddl = MOCK_PROBLEM
            sr.schema_block = "VALID TYPES: (none — typeless domain)\nPREDICATE SIGNATURES:\n  (clear ?x)\n  (on-table ?x)\n  (arm-empty)\n  (holding ?x)\n  (on ?x ?y)"
        elif name == "Planning + Refinement":
            sr.status = "done"
            sr.plan_actions = MOCK_PLAN
            sr.val_log = "Plan valid\nErrors: 0, warnings: 0"
            if method != "llmpp":
                sr.refinement_history = [
                    {
                        "iteration": 1,
                        "error": "Unknown predicate: on-table in (:init)",
                        "fix": "Added (on-table ?x) to :predicates",
                        "success": False,
                    },
                    {
                        "iteration": 2,
                        "error": "",
                        "fix": "Plan found after correction",
                        "success": True,
                    },
                ]
                sr.adequacy_analysis = "1 refinement required (predicate typo fixed)."

        sr.duration = dur
        stages.append(sr)
        _emit(sr)

    # Write mock files so tabs that try to read paths don't crash
    domain_path = os.path.join(tmp_dir, "domain.pddl")
    problem_path = os.path.join(tmp_dir, "problem.pddl")
    plan_path = os.path.join(tmp_dir, "plan.out")
    Path(domain_path).write_text(MOCK_DOMAIN)
    Path(problem_path).write_text(MOCK_PROBLEM)
    Path(plan_path).write_text("\n".join(MOCK_PLAN) + "\n")

    return RunResult(
        success=True,
        stages=stages,
        final_domain_pddl=MOCK_DOMAIN,
        final_problem_pddl=MOCK_PROBLEM,
        plan_actions=MOCK_PLAN,
        plan_file_path=plan_path,
        domain_file_path=domain_path,
        problem_file_path=problem_path,
        total_time=sum(d for _, d in stage_specs),
        refinements=1 if method != "llmpp" else 0,
        method=method,
    )


# ─── Real pipeline ────────────────────────────────────────────────────────────

class LAPISRunner:
    """
    Orchestrates the LAPIS planning pipeline.

    Parameters
    ----------
    agent       : an Agent instance (ClaudeAgent / GPTAgent)
    domain_name : e.g. "blocksworld"
    tmp_dir     : directory for intermediate files (created if absent)
    """

    def __init__(self, agent, domain_name: str = "blocksworld", tmp_dir: Optional[str] = None):
        self.agent = agent
        self.domain_name = domain_name.lower()
        self.tmp_dir = tmp_dir or str(Path(__file__).parent / "tmp")
        os.makedirs(self.tmp_dir, exist_ok=True)

    # ── helpers ──────────────────────────────────────────────────

    def _new_run_dir(self) -> str:
        """Create a unique subdirectory for this run's files."""
        run_id = f"run_{int(time.time()*1000)}"
        d = os.path.join(self.tmp_dir, run_id)
        os.makedirs(d, exist_ok=True)
        return d

    @staticmethod
    def _emit(sr: StageResult, cb: Optional[Callable]):
        if cb:
            cb(sr)

    # ── public API ───────────────────────────────────────────────

    def run(
        self,
        domain_nl: str,
        problem_nl: str,
        method: str = "lapis",
        max_refinements: int = 3,
        planner_name: str = "pyperplan",
        on_stage_update: Optional[Callable[[StageResult], None]] = None,
    ) -> RunResult:
        """
        Execute the pipeline and return a RunResult.

        Parameters
        ----------
        domain_nl       : NL description of the domain (actions, preconditions, effects)
        problem_nl      : NL description of the problem instance (objects + initial state + goal)
        method          : "lapis" or "llmpp"
        max_refinements : number of problem-refinement attempts
        planner_name    : "pyperplan" | "up_fd" | "fd"
        on_stage_update : callback called after each stage (or stage update)
        """
        if MOCK_MODE:
            run_dir = self._new_run_dir()
            return _mock_run(method, on_stage_update, run_dir)

        from src.lapis.planner.low.pddl_generation import (
            generate_domain,
            generate_problem,
            check_domain_adequacy,
            check_problem_adequacy,
            refine_problem,
            extract_schema,
            _format_schema_block,
        )
        from src.lapis.planner.low.pddl_verification import VAL_validate
        from src.lapis.planner.low.planner_utils import plan_with_output

        run_dir = self._new_run_dir()
        logs_dir = os.path.join(run_dir, "logs")
        os.makedirs(logs_dir, exist_ok=True)

        domain_path = os.path.join(run_dir, "domain.pddl")
        problem_path = os.path.join(run_dir, "problem.pddl")
        plan_path = os.path.join(run_dir, "plan.out")
        problem_dir = run_dir

        stages: list[StageResult] = []
        t_total_start = time.time()

        def _stage(name: str) -> StageResult:
            sr = StageResult(name=name, status="running")
            self._emit(sr, on_stage_update)
            return sr

        def _finish(sr: StageResult, status: str = "done", **kwargs):
            sr.status = status
            for k, v in kwargs.items():
                setattr(sr, k, v)
            sr.duration = round(time.time() - t0, 2)
            stages.append(sr)
            self._emit(sr, on_stage_update)

        # ── Stage 1: Domain Generation ──────────────────────────
        t0 = time.time()
        sr1 = _stage("Domain Generation")
        try:
            if method == "llmpp":
                # Use GT domain from data/llmpp/{domain}/p01/domain.pddl
                gt_domain = _find_gt_domain(self.domain_name)
                if gt_domain:
                    shutil.copy(gt_domain, domain_path)
                    with open(domain_path) as f:
                        domain_pddl_text = f.read()
                    _finish(sr1, "skipped",
                            domain_pddl=domain_pddl_text,
                            adequacy_analysis="Using ground-truth domain (LLM+P mode).")
                else:
                    _finish(sr1, "error",
                            error_msg=f"GT domain not found for '{self.domain_name}'")
                    return RunResult(success=False, stages=stages,
                                     error_msg=sr1.error_msg, method=method)
            else:
                generate_domain(
                    domain_file_path=domain_path,
                    domain_description=domain_nl,
                    agent=self.agent,
                    logs_dir=logs_dir,
                    clean_domain_prompt=True,
                )
                with open(domain_path) as f:
                    domain_pddl_text = f.read()
                _finish(sr1, "done", domain_pddl=domain_pddl_text)
        except Exception as e:
            _finish(sr1, "error", error_msg=str(e))
            return RunResult(success=False, stages=stages,
                             error_msg=str(e), method=method)

        # ── Stage 2: Domain Adequacy Check (LAPIS only) ─────────
        if method == "lapis":
            t0 = time.time()
            sr2 = _stage("Domain Adequacy Check")
            try:
                with open(domain_path) as f:
                    domain_pddl_text = f.read()

                # Intercept CoT steps by monkey-patching LLM calls — we capture
                # responses from each of the 3 internal steps via a light wrapper.
                cot_steps: list[dict] = []
                original_llm_call = self.agent.llm_call

                _step_counter = [0]
                _step_labels = ["Predicate Extraction", "Gap Analysis", "Amendment"]

                def _capturing_llm_call(prompt, question, **kwargs):
                    result = original_llm_call(prompt, question, **kwargs)
                    idx = _step_counter[0]
                    if idx < len(_step_labels):
                        cot_steps.append({
                            "step": idx + 1,
                            "label": _step_labels[idx],
                            "content": result,
                        })
                    _step_counter[0] += 1
                    return result

                self.agent.llm_call = _capturing_llm_call
                amended_domain = check_domain_adequacy(
                    domain_pddl=domain_pddl_text,
                    raw_observation=problem_nl,
                    objects_list=_extract_objects_hint(problem_nl),
                    agent=self.agent,
                    logs_dir=logs_dir,
                )
                self.agent.llm_call = original_llm_call

                was_amended = (amended_domain.strip() != domain_pddl_text.strip())
                if was_amended:
                    with open(domain_path, "w") as f:
                        f.write(amended_domain)
                    domain_pddl_text = amended_domain

                gap_text = ""
                if len(cot_steps) >= 2:
                    gap_text = cot_steps[1]["content"]

                _finish(sr2, "done",
                        domain_pddl=domain_pddl_text,
                        adequacy_analysis=gap_text,
                        domain_amended=was_amended,
                        cot_steps=cot_steps)
            except Exception as e:
                self.agent.llm_call = original_llm_call
                _finish(sr2, "error", error_msg=str(e))
                return RunResult(success=False, stages=stages,
                                 error_msg=str(e), method=method)

        # ── Stage 3: Problem Generation ──────────────────────────
        t0 = time.time()
        sr3 = _stage("Problem Generation")
        try:
            with open(domain_path) as f:
                domain_pddl_text = f.read()

            schema = extract_schema(domain_pddl_text)
            schema_block = _format_schema_block(schema)

            generate_problem(
                domain_file_path=domain_path,
                task=_extract_goal(problem_nl),
                environment=_extract_world_state(problem_nl),
                problem_file_path=problem_path,
                agent=self.agent,
                logs_dir=logs_dir,
                inject_domain_schema=True,
            )
            with open(problem_path) as f:
                problem_pddl_text = f.read()

            # Optional: problem adequacy check for LAPIS
            problem_amended = False
            if method == "lapis":
                amended_problem = check_problem_adequacy(
                    problem_pddl=problem_pddl_text,
                    domain_pddl=domain_pddl_text,
                    raw_observation=problem_nl,
                    objects_list=_extract_objects_hint(problem_nl),
                    agent=self.agent,
                    logs_dir=logs_dir,
                )
                if amended_problem.strip() != problem_pddl_text.strip():
                    with open(problem_path, "w") as f:
                        f.write(amended_problem)
                    problem_pddl_text = amended_problem
                    problem_amended = True

            _finish(sr3, "done",
                    problem_pddl=problem_pddl_text,
                    problem_amended=problem_amended,
                    schema_block=schema_block)
        except Exception as e:
            _finish(sr3, "error", error_msg=str(e))
            return RunResult(success=False, stages=stages,
                             error_msg=str(e), method=method)

        # ── Stage 4: Planning + Refinement Loop ──────────────────
        t0 = time.time()
        sr4 = _stage("Planning + Refinement")
        try:
            max_ref = 0 if method == "llmpp" else max_refinements
            plan_actions, refinement_history, val_log, n_refs = _plan_refine_loop(
                domain_path=domain_path,
                problem_path=problem_path,
                problem_dir=problem_dir,
                plan_path=plan_path,
                planner_name=planner_name,
                max_refinements=max_ref,
                agent=self.agent,
                problem_nl=problem_nl,
                logs_dir=logs_dir,
                on_update=lambda msg: self._emit(
                    StageResult(name="Planning + Refinement",
                                status="running",
                                adequacy_analysis=msg), on_stage_update),
            )

            with open(domain_path) as f:
                final_domain = f.read()
            with open(problem_path) as f:
                final_problem = f.read()

            success = len(plan_actions) > 0
            _finish(sr4,
                    "done" if success else "error",
                    plan_actions=plan_actions,
                    val_log=val_log,
                    refinement_history=refinement_history,
                    error_msg="" if success else "No plan found after refinements")

            return RunResult(
                success=success,
                stages=stages,
                final_domain_pddl=final_domain,
                final_problem_pddl=final_problem,
                plan_actions=plan_actions,
                plan_file_path=plan_path,
                domain_file_path=domain_path,
                problem_file_path=problem_path,
                total_time=round(time.time() - t_total_start, 2),
                refinements=n_refs,
                method=method,
                error_msg="" if success else "Planning failed.",
            )
        except Exception as e:
            _finish(sr4, "error", error_msg=str(e))
            return RunResult(success=False, stages=stages,
                             error_msg=str(e), method=method,
                             total_time=round(time.time() - t_total_start, 2))


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _find_gt_domain(domain_name: str) -> Optional[str]:
    """Find the ground-truth domain.pddl for a named domain."""
    base = _REPO_ROOT / "data" / "llmpp" / domain_name / "p01" / "domain.pddl"
    if base.exists():
        return str(base)
    return None


def _extract_objects_hint(problem_nl: str) -> str:
    """Heuristic: return lines that look like object declarations."""
    lines = [l.strip() for l in problem_nl.splitlines() if l.strip()]
    # Return first 5 lines as an objects hint
    return "\n".join(lines[:5])


def _extract_goal(problem_nl: str) -> str:
    """
    Heuristic: lines containing 'goal' or 'should' are the goal description.
    Falls back to last paragraph.
    """
    lines = problem_nl.splitlines()
    goal_lines = [l for l in lines if "goal" in l.lower() or "should" in l.lower()]
    if goal_lines:
        return "\n".join(goal_lines)
    # Last non-empty lines
    non_empty = [l for l in lines if l.strip()]
    return "\n".join(non_empty[-3:]) if non_empty else problem_nl


def _extract_world_state(problem_nl: str) -> str:
    """Return the full problem NL as the world state context."""
    return problem_nl


def _plan_refine_loop(
    domain_path: str,
    problem_path: str,
    problem_dir: str,
    plan_path: str,
    planner_name: str,
    max_refinements: int,
    agent,
    problem_nl: str,
    logs_dir: str,
    on_update: Callable,
) -> tuple[list, list, str, int]:
    """
    Run the planner; on failure, call refine_problem up to max_refinements times.

    Returns (plan_actions, refinement_history, val_log, n_refinements).
    """
    from src.lapis.planner.low.pddl_generation import refine_problem
    from src.lapis.planner.low.pddl_verification import VAL_validate
    from src.lapis.planner.low.planner_utils import plan_with_output

    refinement_history: list[dict] = []
    val_log = ""

    on_update("Running planner…")
    plan, pddlenv_err, planner_err, _ = plan_with_output(
        domain_path, problem_dir, plan_path, planner_name=planner_name, timeout=60
    )

    if plan:
        val_ok, val_log = VAL_validate(domain_path, problem_path, plan_path)
        return _read_plan(plan_path, plan), refinement_history, val_log, 0

    # Refinement loop
    for i in range(max_refinements):
        on_update(f"Refinement {i+1}/{max_refinements}…")

        val_ok, val_out = VAL_validate(domain_path, problem_path)
        err_summary = (pddlenv_err or "") + (planner_err or "") + val_out

        try:
            new_problem_pddl, ref_hist = refine_problem(
                domain_file_path=domain_path,
                problem_file_path=problem_path,
                environment=problem_nl,
                task=_extract_goal(problem_nl),
                logs_dir=logs_dir,
                workflow_iteration=0,
                refinement_iteration=i,
                agent=agent,
                pddlenv_error_log=pddlenv_err,
                planner_error_log=planner_err,
                VAL_validation_log=val_out,
            )
        except Exception as ex:
            refinement_history.append({
                "iteration": i + 1,
                "error": str(ex),
                "fix": "refinement call failed",
                "success": False,
            })
            continue

        with open(problem_path, "w") as f:
            f.write(new_problem_pddl)

        plan, pddlenv_err, planner_err, _ = plan_with_output(
            domain_path, problem_dir, plan_path, planner_name=planner_name, timeout=60
        )

        entry = {
            "iteration": i + 1,
            "error": err_summary[:300] if err_summary else "",
            "fix": (ref_hist[0]["solution"] if ref_hist else "see logs"),
            "success": bool(plan),
        }
        refinement_history.append(entry)

        if plan:
            val_ok, val_log = VAL_validate(domain_path, problem_path, plan_path)
            return _read_plan(plan_path, plan), refinement_history, val_log, i + 1

    return [], refinement_history, val_log, max_refinements


def _read_plan(plan_path: str, plan_fallback) -> list:
    """Read plan from file; fall back to the list returned by plan_with_output."""
    try:
        with open(plan_path) as f:
            lines = [l.strip() for l in f if l.strip() and not l.startswith(";")]
        if lines:
            return lines
    except Exception:
        pass
    if isinstance(plan_fallback, list):
        return [str(a) for a in plan_fallback]
    return []
