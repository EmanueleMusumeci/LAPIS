"""
runner.py — LAPISRunner adapted for FastAPI (no Streamlit dependencies).

Executes the LAPIS planning pipeline with async event callbacks for WebSocket updates.

Two modes:
  - LAPIS : full pipeline (domain gen -> adequacy -> problem gen -> plan -> refine)
  - LLM+P : GT domain injected, skip domain gen + adequacy, 0 refinements
"""
from __future__ import annotations

import asyncio
import html
import os
import re
import sys
import time
import shutil
from pathlib import Path
from typing import Callable, Optional, Awaitable

from .models import (
    StageResult, RunResult, StageStatus,
    RefinementEntry, CoTStep, PipelineConfig
)

# Ensure src/ is importable regardless of cwd
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


# --- Helpers ---

def _find_gt_domain(domain_name: str) -> Optional[str]:
    """Find the ground-truth domain.pddl for a named domain."""
    base = _REPO_ROOT / "data" / "llmpp" / domain_name / "p01" / "domain.pddl"
    if base.exists():
        return str(base)
    return None


def _extract_objects_hint(problem_nl: str) -> str:
    """Heuristic: return lines that look like object declarations."""
    lines = [line.strip() for line in problem_nl.splitlines() if line.strip()]
    return "\n".join(lines[:5])


def _extract_goal(problem_nl: str) -> str:
    """Heuristic: lines containing 'goal' or 'should' are the goal description."""
    lines = problem_nl.splitlines()
    goal_lines = [line for line in lines if "goal" in line.lower() or "should" in line.lower()]
    if goal_lines:
        return "\n".join(goal_lines)
    non_empty = [line for line in lines if line.strip()]
    return "\n".join(non_empty[-3:]) if non_empty else problem_nl


def _extract_world_state(problem_nl: str) -> str:
    """Return the full problem NL as the world state context."""
    return problem_nl


def _read_plan(plan_path: str, plan_fallback) -> list[str]:
    """Read plan from file; fall back to the list returned by plan_with_output."""
    try:
        with open(plan_path) as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith(";")]
        if lines:
            return lines
    except Exception:
        pass
    if isinstance(plan_fallback, list):
        return [str(a) for a in plan_fallback]
    return []


def sanitize_error_message(error: Exception) -> str:
    """Normalize backend errors into short, UI-safe messages."""
    raw = str(error or "").strip()
    if not raw:
        return "Unknown error"

    compact = " ".join(raw.split())
    if len(compact) > 1200:
        compact = compact[:1200] + "..."

    if re.search(r"api[_ ]?key", compact, re.IGNORECASE):
        return "Missing or invalid API key. Please check backend environment variables."

    return html.escape(compact)


# --- Real pipeline ---

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
        self.tmp_dir = tmp_dir or str(_REPO_ROOT / "backend" / "tmp")
        os.makedirs(self.tmp_dir, exist_ok=True)

    def _new_run_dir(self) -> str:
        """Create a unique subdirectory for this run's files."""
        run_id = f"run_{int(time.time()*1000)}"
        d = os.path.join(self.tmp_dir, run_id)
        os.makedirs(d, exist_ok=True)
        return d

    @staticmethod
    async def _emit(sr: StageResult, cb: Optional[Callable[[StageResult], Awaitable[None]]]):
        if cb:
            await cb(sr)

    async def run(
        self,
        config: PipelineConfig,
        on_stage_update: Optional[Callable[[StageResult], Awaitable[None]]] = None,
    ) -> RunResult:
        """
        Execute the pipeline and return a RunResult.

        Parameters
        ----------
        config          : PipelineConfig with all run parameters
        on_stage_update : async callback called after each stage (or stage update)
        """
        method = config.method.value

        # Import pipeline components
        from src.lapis.planner.low.pddl_generation import (
            generate_domain,
            generate_problem,
            check_domain_adequacy,
            check_problem_adequacy,
            refine_problem,
            refine_domain,
            extract_schema,
            _format_schema_block,
        )
        from src.lapis.planner.low.pddl_verification import VAL_validate, translate_plan, VAL_ground
        from src.lapis.planner.low.planner_utils import plan_with_output
        from src.lapis.planner.low.semantic_verification import run_semantic_checks

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
            sr = StageResult(name=name, status=StageStatus.RUNNING)
            return sr

        async def _finish(sr: StageResult, t0: float, status: StageStatus = StageStatus.DONE, **kwargs):
            sr.status = status
            for k, v in kwargs.items():
                setattr(sr, k, v)
            sr.duration = round(time.time() - t0, 2)
            stages.append(sr)
            await self._emit(sr, on_stage_update)

        # --- Stage 1: Domain Generation ---
        t0 = time.time()
        sr1 = _stage("Domain Generation")
        await self._emit(sr1, on_stage_update)

        try:
            if method == "llmpp":
                gt_domain = _find_gt_domain(self.domain_name)
                if gt_domain:
                    shutil.copy(gt_domain, domain_path)
                    with open(domain_path) as f:
                        domain_pddl_text = f.read()
                    await _finish(sr1, t0, StageStatus.SKIPPED,
                                  domain_pddl=domain_pddl_text,
                                  adequacy_analysis="Using ground-truth domain (LLM+P mode).")
                else:
                    await _finish(sr1, t0, StageStatus.ERROR,
                                  error_msg=f"GT domain not found for '{self.domain_name}'")
                    return RunResult(success=False, stages=stages,
                                     error_msg=sr1.error_msg, method=method)
            else:
                generate_domain(
                    domain_file_path=domain_path,
                    domain_description=config.domain_nl,
                    agent=self.agent,
                    logs_dir=logs_dir,
                    clean_domain_prompt=True,
                )
                with open(domain_path) as f:
                    domain_pddl_text = f.read()
                await _finish(sr1, t0, StageStatus.DONE, domain_pddl=domain_pddl_text)
        except Exception as e:
            await _finish(sr1, t0, StageStatus.ERROR, error_msg=str(e))
            return RunResult(success=False, stages=stages,
                             error_msg=str(e), method=method)

        # --- Stage 2: Domain Adequacy Check (LAPIS only) ---
        if method == "lapis" and not config.skip_adequacy:
            t0 = time.time()
            sr2 = _stage("Domain Adequacy Check")
            await self._emit(sr2, on_stage_update)

            try:
                with open(domain_path) as f:
                    domain_pddl_text = f.read()

                cot_steps: list[CoTStep] = []
                original_llm_call = self.agent.llm_call
                _step_counter = [0]
                _step_labels = ["Predicate Extraction", "Gap Analysis", "Amendment"]

                def _capturing_llm_call(prompt, question, **kwargs):
                    result = original_llm_call(prompt, question, **kwargs)
                    idx = _step_counter[0]
                    if idx < len(_step_labels):
                        cot_steps.append(CoTStep(
                            step=idx + 1,
                            label=_step_labels[idx],
                            content=result,
                        ))
                    _step_counter[0] += 1
                    return result

                self.agent.llm_call = _capturing_llm_call
                amended_domain = check_domain_adequacy(
                    domain_pddl=domain_pddl_text,
                    raw_observation=config.problem_nl,
                    objects_list=_extract_objects_hint(config.problem_nl),
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
                    gap_text = cot_steps[1].content

                await _finish(sr2, t0, StageStatus.DONE,
                              domain_pddl=domain_pddl_text,
                              adequacy_analysis=gap_text,
                              domain_amended=was_amended,
                              cot_steps=cot_steps)
            except Exception as e:
                self.agent.llm_call = original_llm_call
                await _finish(sr2, t0, StageStatus.ERROR, error_msg=str(e))
                return RunResult(success=False, stages=stages,
                                 error_msg=str(e), method=method)

        # --- Stage 3: Problem Generation ---
        t0 = time.time()
        sr3 = _stage("Problem Generation")
        await self._emit(sr3, on_stage_update)

        try:
            with open(domain_path) as f:
                domain_pddl_text = f.read()

            schema = extract_schema(domain_pddl_text)
            schema_block = _format_schema_block(schema)

            generate_problem(
                domain_file_path=domain_path,
                task=_extract_goal(config.problem_nl),
                environment=_extract_world_state(config.problem_nl),
                problem_file_path=problem_path,
                agent=self.agent,
                logs_dir=logs_dir,
                inject_domain_schema=True,
            )
            with open(problem_path) as f:
                problem_pddl_text = f.read()

            problem_amended = False
            if method == "lapis":
                amended_problem = check_problem_adequacy(
                    problem_pddl=problem_pddl_text,
                    domain_pddl=domain_pddl_text,
                    raw_observation=config.problem_nl,
                    objects_list=_extract_objects_hint(config.problem_nl),
                    agent=self.agent,
                    logs_dir=logs_dir,
                )
                if amended_problem.strip() != problem_pddl_text.strip():
                    with open(problem_path, "w") as f:
                        f.write(amended_problem)
                    problem_pddl_text = amended_problem
                    problem_amended = True

            await _finish(sr3, t0, StageStatus.DONE,
                          problem_pddl=problem_pddl_text,
                          problem_amended=problem_amended,
                          schema_block=schema_block)
        except Exception as e:
            await _finish(sr3, t0, StageStatus.ERROR, error_msg=str(e))
            return RunResult(success=False, stages=stages,
                             error_msg=str(e), method=method)

        # --- Stage 4: Planning + Refinement Loop ---
        t0 = time.time()
        sr4 = _stage("Planning + Refinement")
        await self._emit(sr4, on_stage_update)

        try:
            max_ref = 0 if method == "llmpp" else config.max_refinements
            plan_actions, refinement_history, val_log, n_refs = await self._plan_refine_loop(
                domain_path=domain_path,
                problem_path=problem_path,
                problem_dir=problem_dir,
                plan_path=plan_path,
                planner_name=config.planner_name,
                planner_timeout=config.planner_timeout,
                max_refinements=max_ref,
                problem_nl=config.problem_nl,
                domain_nl=config.domain_nl,
                semantic_checks=(config.semantic_checks and method == "lapis"),
                refine_domain_enabled=(config.refine_domain and method == "lapis"),
                extractor_type=config.extractor_type,
                current_goal=_extract_goal(config.problem_nl),
                logs_dir=logs_dir,
                on_update=lambda msg: self._emit(
                    StageResult(name="Planning + Refinement",
                                status=StageStatus.RUNNING,
                                adequacy_analysis=msg), on_stage_update),
            )

            with open(domain_path) as f:
                final_domain = f.read()
            with open(problem_path) as f:
                final_problem = f.read()

            success = len(plan_actions) > 0
            await _finish(sr4, t0,
                          StageStatus.DONE if success else StageStatus.ERROR,
                          plan_actions=plan_actions,
                          val_log=val_log,
                          refinement_history=refinement_history,
                          error_msg="" if success else "No plan found after refinements")

            # Generate plan animation if successful and domain supports it
            animation_url = ""
            step_images = []
            if success and self.domain_name.lower() in ["blocksworld", "blocks"]:
                try:
                    animation_url, step_images = await _generate_plan_animation(
                        domain_path, problem_path, plan_actions, problem_dir
                    )
                except Exception as e:
                    print(f"[WARN] Failed to generate plan animation: {e}")

            return RunResult(
                success=success,
                stages=stages,
                final_domain_pddl=final_domain,
                final_problem_pddl=final_problem,
                plan_actions=plan_actions,
                plan_file_path=plan_path,
                domain_file_path=domain_path,
                problem_file_path=problem_path,
                plan_animation_url=animation_url,
                plan_step_images=step_images,
                total_time=round(time.time() - t_total_start, 2),
                refinements=n_refs,
                method=method,
                error_msg="" if success else "Planning failed.",
            )
        except Exception as e:
            await _finish(sr4, t0, StageStatus.ERROR, error_msg=str(e))
            return RunResult(success=False, stages=stages,
                             error_msg=str(e), method=method,
                             total_time=round(time.time() - t_total_start, 2))

    async def _plan_refine_loop(
        self,
        domain_path: str,
        problem_path: str,
        problem_dir: str,
        plan_path: str,
        planner_name: str,
        planner_timeout: int,
        max_refinements: int,
        problem_nl: str,
        domain_nl: str,
        semantic_checks: bool,
        refine_domain_enabled: bool,
        extractor_type: str,
        current_goal: str,
        logs_dir: str,
        on_update,
    ) -> tuple[list[str], list[RefinementEntry], str, int]:
        """
        Run the planner; on failure, call refine_problem up to max_refinements times.

        Returns (plan_actions, refinement_history, val_log, n_refinements).
        """
        from src.lapis.planner.low.pddl_generation import refine_problem
        from src.lapis.planner.low.pddl_generation import refine_domain
        from src.lapis.planner.low.pddl_verification import VAL_validate, translate_plan, VAL_ground
        from src.lapis.planner.low.planner_utils import plan_with_output
        from src.lapis.planner.low.semantic_verification import run_semantic_checks

        refinement_history: list[RefinementEntry] = []
        val_log = ""
        pddlenv_err = ""
        planner_err = ""
        val_grounding_log = ""
        semantic_diagnosis = ""
        semantic_result = None
        planning_successful = False
        val_grounding_successful = False
        semantic_passed = True

        async def _plan_and_validate(suffix: str):
            nonlocal val_log, pddlenv_err, planner_err, val_grounding_log
            nonlocal planning_successful, val_grounding_successful
            nonlocal semantic_passed, semantic_diagnosis, semantic_result

            plan, pddlenv_err, planner_err, _ = plan_with_output(
                domain_path, problem_dir, plan_path, planner_name=planner_name, timeout=planner_timeout
            )
            planning_successful = plan is not None

            val_successful = False
            val_ground_successful = False
            val_log = ""
            val_grounding_log = ""

            if planning_successful:
                translated_plan_path = os.path.join(problem_dir, f"translated_plan_{suffix}.txt")
                translate_plan(plan_path, translated_plan_path)
                val_successful, val_log = VAL_validate(domain_path, problem_path, translated_plan_path)
                if val_successful:
                    val_ground_successful, val_grounding_log = VAL_ground(domain_path, problem_path)

            val_grounding_successful = val_successful and val_ground_successful

            semantic_passed = True
            semantic_diagnosis = ""
            semantic_result = None
            if semantic_checks and val_successful:
                with open(domain_path) as f:
                    domain_content = f.read()
                with open(problem_path) as f:
                    problem_content = f.read()
                semantic_result = run_semantic_checks(
                    domain_content,
                    problem_content,
                    strict=False,
                    extractor_type=extractor_type,
                )
                semantic_passed = semantic_result.get("passed", True)
                if not semantic_passed:
                    semantic_diagnosis = semantic_result.get("combined_diagnosis", "")

            return plan

        await on_update("Running planner...")
        plan = await _plan_and_validate("0")

        should_refine = (
            (not planning_successful)
            or (not val_grounding_successful)
            or (semantic_checks and not semantic_passed)
        )
        if not should_refine and plan:
            return _read_plan(plan_path, plan), refinement_history, val_log, 0

        # Refinement loop (experiment path)
        for i in range(max_refinements):
            await on_update(f"Refinement {i + 1}/{max_refinements}...")

            combined_val_log = val_log or ""
            if semantic_diagnosis:
                combined_val_log = f"{combined_val_log}\n\n{semantic_diagnosis}" if combined_val_log else semantic_diagnosis

            try:
                domain_refined = False
                if refine_domain_enabled and semantic_result:
                    domain_level_errors = semantic_result.get("domain_level_errors", [])
                    if domain_level_errors:
                        await on_update("Semantic domain errors detected; refining domain...")
                        new_domain_pddl, _ = refine_domain(
                            domain_file_path=domain_path,
                            problem_file_path=problem_path,
                            environment=domain_nl,
                            task=current_goal,
                            logs_dir=logs_dir,
                            workflow_iteration=0,
                            refinement_iteration=i,
                            agent=self.agent,
                            pddlenv_error_log=pddlenv_err,
                            planner_error_log=planner_err,
                            VAL_validation_log=combined_val_log,
                            VAL_grounding_log=val_grounding_log,
                        )
                        with open(domain_path, "w") as f:
                            f.write(new_domain_pddl)
                        domain_refined = True

                new_problem_pddl, ref_hist = refine_problem(
                    domain_file_path=domain_path,
                    problem_file_path=problem_path,
                    environment=problem_nl,
                    task=current_goal,
                    logs_dir=logs_dir,
                    workflow_iteration=0,
                    refinement_iteration=i,
                    agent=self.agent,
                    pddlenv_error_log=pddlenv_err,
                    planner_error_log=planner_err,
                    VAL_validation_log=combined_val_log,
                    VAL_grounding_log=val_grounding_log,
                )
            except Exception as ex:
                refinement_history.append(RefinementEntry(
                    iteration=i + 1,
                    error=str(ex),
                    fix="refinement call failed",
                    success=False,
                ))
                continue

            with open(problem_path, "w") as f:
                f.write(new_problem_pddl)

            plan = await _plan_and_validate(str(i + 1))

            fix_text = "see logs"
            if ref_hist:
                fix_text = ref_hist[0].get("solution") or ref_hist[0].get("issue") or "see logs"
            entry_error = combined_val_log or pddlenv_err or planner_err
            if domain_refined:
                fix_text = f"Domain+Problem refinement. {fix_text}".strip()

            entry = RefinementEntry(
                iteration=i + 1,
                error=(entry_error or "")[:300],
                fix=fix_text,
                success=bool(plan and val_grounding_successful and (not semantic_checks or semantic_passed)),
            )
            refinement_history.append(entry)

            done = bool(plan and val_grounding_successful and (not semantic_checks or semantic_passed))
            if done:
                return _read_plan(plan_path, plan), refinement_history, val_log, i + 1

        final_log = val_log
        if semantic_diagnosis:
            final_log = f"{final_log}\n\n{semantic_diagnosis}" if final_log else semantic_diagnosis
        return [], refinement_history, final_log, max_refinements


async def _generate_plan_animation(
    domain_path: str,
    problem_path: str,
    plan_actions: list[str],
    problem_dir: str,
) -> tuple[str, list[str]]:
    """
    Generate plan animation GIF and extract individual step images.

    Returns:
        (animation_url, step_image_urls) - URLs relative to /static/results/
    """
    import uuid
    from src.lapis.plan_renderer import render_blocksworld_gif

    # Create unique directory for this run
    run_id = str(uuid.uuid4())[:8]
    results_root = Path(__file__).parent.parent.parent / "results_web"
    run_dir = results_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    # Generate GIF
    gif_path = str(run_dir / "plan.gif")
    gif_ok = render_blocksworld_gif(
        domain_file=domain_path,
        problem_file=problem_path,
        action_strs=plan_actions,
        output_path=gif_path,
        fps=2,
    )

    if not gif_ok or not Path(gif_path).exists():
        return "", []

    # Extract frames as individual images
    step_images = []
    try:
        from PIL import Image
        with Image.open(gif_path) as img:
            frame_idx = 0
            while True:
                try:
                    img.seek(frame_idx)
                    frame_path = run_dir / f"step_{frame_idx}.png"
                    img.save(str(frame_path), "PNG")
                    step_images.append(f"/static/results/{run_id}/step_{frame_idx}.png")
                    frame_idx += 1
                except EOFError:
                    break
    except Exception as e:
        print(f"[WARN] Failed to extract GIF frames: {e}")

    animation_url = f"/static/results/{run_id}/plan.gif"
    return animation_url, step_images


def make_agent(model_id: str):
    """Create an agent instance for the given model ID."""
    if model_id.startswith("claude"):
        from src.lapis.agents.claude import ClaudeAgent
        return ClaudeAgent(model=model_id)
    else:
        from src.lapis.agents.gpt import GPTAgent
        return GPTAgent(model=model_id)
