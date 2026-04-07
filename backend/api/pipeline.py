"""
pipeline.py — Pipeline execution API endpoints.

Provides REST endpoints for:
- POST /run: Start a pipeline run
- GET /status/{run_id}: Get run status
- POST /cancel/{run_id}: Cancel a running pipeline
"""
from __future__ import annotations

import asyncio
import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks

from ..models import (
    PipelineConfig, RunResult, RunStatusResponse, RunStartResponse,
    StageResult, StageStatus
)
from ..runner import LAPISRunner, make_agent

router = APIRouter(prefix="/api", tags=["pipeline"])

# Active runs storage
_active_runs: dict[str, dict] = {}


def _get_run(run_id: str) -> dict:
    """Get run info by ID or raise 404."""
    if run_id not in _active_runs:
        raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")
    return _active_runs[run_id]


async def _execute_pipeline(run_id: str, config: PipelineConfig):
    """Background task to execute the pipeline."""
    run_info = _active_runs.get(run_id)
    if not run_info:
        return

    try:
        agent = make_agent(config.model_id)
        runner = LAPISRunner(
            agent=agent,
            domain_name=config.domain_name,
        )

        async def on_stage_update(stage: StageResult):
            """Callback for stage updates."""
            if run_id in _active_runs:
                # Update or append stage
                existing_names = [s.name for s in _active_runs[run_id]["stages"]]
                if stage.name in existing_names:
                    idx = existing_names.index(stage.name)
                    _active_runs[run_id]["stages"][idx] = stage
                else:
                    _active_runs[run_id]["stages"].append(stage)

                # Update current stage
                if stage.status == StageStatus.RUNNING:
                    _active_runs[run_id]["current_stage"] = stage.name

        result = await runner.run(config, on_stage_update=on_stage_update)

        if run_id in _active_runs:
            _active_runs[run_id]["is_running"] = False
            _active_runs[run_id]["result"] = result
            _active_runs[run_id]["current_stage"] = None

    except Exception as e:
        if run_id in _active_runs:
            _active_runs[run_id]["is_running"] = False
            _active_runs[run_id]["error"] = str(e)
            _active_runs[run_id]["result"] = RunResult(
                success=False,
                error_msg=str(e),
                method=config.method.value,
            )


@router.post("/run", response_model=RunStartResponse)
async def start_run(config: PipelineConfig, background_tasks: BackgroundTasks) -> RunStartResponse:
    """
    Start a new pipeline run.

    Returns immediately with a run_id. Use /status/{run_id} or WebSocket
    to monitor progress.
    """
    run_id = str(uuid.uuid4())

    _active_runs[run_id] = {
        "run_id": run_id,
        "config": config,
        "is_running": True,
        "current_stage": None,
        "stages": [],
        "result": None,
        "error": None,
    }

    background_tasks.add_task(_execute_pipeline, run_id, config)

    return RunStartResponse(run_id=run_id, message="Pipeline started")


@router.get("/status/{run_id}", response_model=RunStatusResponse)
async def get_status(run_id: str) -> RunStatusResponse:
    """
    Get the current status of a pipeline run.
    """
    run_info = _get_run(run_id)

    return RunStatusResponse(
        run_id=run_id,
        is_running=run_info["is_running"],
        current_stage=run_info["current_stage"],
        stages=run_info["stages"],
        result=run_info["result"],
    )


@router.post("/cancel/{run_id}")
async def cancel_run(run_id: str) -> dict:
    """
    Cancel a running pipeline.

    Note: Cancellation is best-effort. LLM calls and planner execution
    may not be immediately interruptible.
    """
    run_info = _get_run(run_id)

    if not run_info["is_running"]:
        return {"message": "Run already completed", "run_id": run_id}

    # Mark as cancelled
    run_info["is_running"] = False
    run_info["error"] = "Cancelled by user"

    return {"message": "Cancellation requested", "run_id": run_id}


@router.get("/runs", response_model=list[RunStatusResponse])
async def list_runs() -> list[RunStatusResponse]:
    """
    List all runs (active and completed).
    """
    return [
        RunStatusResponse(
            run_id=run_id,
            is_running=info["is_running"],
            current_stage=info["current_stage"],
            stages=info["stages"],
            result=info["result"],
        )
        for run_id, info in _active_runs.items()
    ]


@router.delete("/runs/{run_id}")
async def delete_run(run_id: str) -> dict:
    """
    Delete a completed run from memory.
    """
    run_info = _get_run(run_id)

    if run_info["is_running"]:
        raise HTTPException(status_code=400, detail="Cannot delete running pipeline")

    del _active_runs[run_id]
    return {"message": "Run deleted", "run_id": run_id}


@router.delete("/runs")
async def clear_completed_runs() -> dict:
    """
    Clear all completed runs from memory.
    """
    to_delete = [
        run_id for run_id, info in _active_runs.items()
        if not info["is_running"]
    ]

    for run_id in to_delete:
        del _active_runs[run_id]

    return {"message": f"Cleared {len(to_delete)} completed runs"}
