"""
models.py — Pydantic models for the LAPIS FastAPI backend.

Defines data structures for:
- Pipeline configuration
- Stage results (real-time updates)
- Run results (final output)
- Preset definitions
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class StageStatus(str, Enum):
    """Status of a pipeline stage."""
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"
    SKIPPED = "skipped"


class RefinementEntry(BaseModel):
    """Single entry in the refinement history."""
    iteration: int
    error: str = ""
    fix: str = ""
    success: bool = False


class CoTStep(BaseModel):
    """Chain-of-thought step for adequacy analysis."""
    step: int
    label: str
    content: str


class StageResult(BaseModel):
    """Result of a single pipeline stage."""
    name: str
    status: StageStatus = StageStatus.PENDING
    duration: float = 0.0
    domain_pddl: str = ""
    problem_pddl: str = ""
    adequacy_analysis: str = ""
    domain_amended: bool = False
    problem_amended: bool = False
    schema_block: str = ""
    val_log: str = ""
    plan_actions: list[str] = Field(default_factory=list)
    refinement_history: list[RefinementEntry] = Field(default_factory=list)
    error_msg: str = ""
    cot_steps: list[CoTStep] = Field(default_factory=list)


class RunResult(BaseModel):
    """Final result of a pipeline run."""
    success: bool = False
    stages: list[StageResult] = Field(default_factory=list)
    final_domain_pddl: str = ""
    final_problem_pddl: str = ""
    plan_actions: list[str] = Field(default_factory=list)
    plan_file_path: str = ""
    domain_file_path: str = ""
    problem_file_path: str = ""
    plan_animation_url: str = ""  # URL to plan animation GIF
    plan_step_images: list[str] = Field(default_factory=list)  # URLs to individual step images
    total_time: float = 0.0
    refinements: int = 0
    method: str = "lapis"
    error_msg: str = ""


class PipelineMethod(str, Enum):
    """Pipeline execution method."""
    LAPIS = "lapis"
    LLMPP = "llmpp"


class PipelineConfig(BaseModel):
    """Configuration for a pipeline run."""
    domain_nl: str = Field(..., description="Natural language domain description")
    problem_nl: str = Field(..., description="Natural language problem description")
    method: PipelineMethod = PipelineMethod.LAPIS
    domain_name: str = "blocksworld"
    model_id: str = "claude-sonnet-4-6"
    planner_name: str = "up_fd"
    planner_timeout: int = Field(180, ge=30, le=600)
    max_refinements: int = Field(3, ge=0, le=10)
    skip_adequacy: bool = False
    semantic_checks: bool = True
    refine_domain: bool = True
    extractor_type: str = "auto"


class Preset(BaseModel):
    """A preset problem configuration."""
    id: str
    label: str
    domain: str
    problem_id: str
    domain_nl: str
    problem_nl: str


class PresetList(BaseModel):
    """List of available presets."""
    presets: list[Preset]
    domains: list[str]


# WebSocket message types

class WSMessageType(str, Enum):
    """WebSocket message types."""
    CONNECTED = "connected"
    STAGE_UPDATE = "stage_update"
    COMPLETE = "complete"
    ERROR = "error"
    RUN_STARTED = "run_started"
    INIT_SESSION = "INIT_SESSION"
    UPDATE = "UPDATE"
    USER_MESSAGE = "USER_MESSAGE"
    AGENT_MESSAGE = "AGENT_MESSAGE"
    PDDL_UPDATE = "PDDL_UPDATE"
    VERIFY_REQUEST = "VERIFY_REQUEST"
    VERIFY_RESULTS = "VERIFY_RESULTS"
    VIZ_BLUEPRINT = "VIZ_BLUEPRINT"


class WSMessage(BaseModel):
    """WebSocket message wrapper."""
    type: WSMessageType
    run_id: Optional[str] = None
    data: Optional[Any] = None
    message: Optional[str] = None


# API response models

class RunStatusResponse(BaseModel):
    """Response for GET /status endpoint."""
    run_id: str
    is_running: bool
    current_stage: Optional[str] = None
    stages: list[StageResult] = Field(default_factory=list)
    result: Optional[RunResult] = None


class RunStartResponse(BaseModel):
    """Response for POST /run endpoint."""
    run_id: str
    message: str = "Pipeline started"
