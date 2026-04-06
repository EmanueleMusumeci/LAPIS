from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass, field
from typing import Any

from src.lapis.agents.editor_agent import EditorAgent
from src.lapis.agents.dialogue_manager import DialogueManager
from src.lapis.validators import VerificationService


DEFAULT_DOMAIN = """(define (domain demo)
  (:requirements :strips :typing)
  (:types block)
  (:predicates
    (on ?x - block ?y - block)
    (clear ?x - block)
    (ontable ?x - block)
  )
)
"""

DEFAULT_PROBLEM = """(define (problem demo-problem)
  (:domain demo)
  (:objects a b c - block)
  (:init (ontable a) (ontable b) (ontable c) (clear a) (clear b) (clear c))
  (:goal (on a b))
)
"""


@dataclass
class SessionState:
    """State tracked for one editor websocket session."""

    domain: str = DEFAULT_DOMAIN
    problem: str = DEFAULT_PROBLEM
    chat: list[dict[str, Any]] = field(default_factory=list)
    verification: dict[str, Any] | None = None
    blueprint: dict[str, Any] | None = None


class EditorOrchestrator:
    """State machine for editor synchronization and verification."""

    def __init__(self):
        self._lock = asyncio.Lock()
        self._state = SessionState()
        self._verifier = VerificationService()
        self._agent = EditorAgent()
        self._dialogue = DialogueManager()

    @property
    def state(self) -> SessionState:
        return self._state

    async def init_session(self, domain_name: str | None = None) -> dict[str, Any]:
        async with self._lock:
            if domain_name and domain_name.lower() in {"babyai", "minigrid", "gridworld"}:
                self._state.domain = self._default_grid_domain()
                self._state.problem = self._default_grid_problem()
            else:
                self._state.domain = DEFAULT_DOMAIN
                self._state.problem = DEFAULT_PROBLEM

            self._state.chat = []
            verification = self._run_verification_locked()
            blueprint = self._build_blueprint_locked()
            return {
                "domain": self._state.domain,
                "problem": self._state.problem,
                "verification": verification,
                "blueprint": blueprint,
            }

    async def process_user_message(self, text: str) -> dict[str, Any]:
        async with self._lock:
            user_text = text.strip()
            if user_text:
                self._state.chat.append({"role": "user", "text": user_text})

            response = self._agent.process(user_text, self._state.domain, self._state.problem)
            self._state.domain = response.domain
            self._state.problem = response.problem
            self._state.chat.append({"role": "agent", "text": response.reply})

            verification = self._run_verification_locked()
            blueprint = self._build_blueprint_locked()
            return {
                "response": response.reply,
                "domain": self._state.domain,
                "problem": self._state.problem,
                "verification": verification,
                "blueprint": blueprint,
            }

    async def sync_pddl(self, domain: str, problem: str, source: str = "text") -> dict[str, Any]:
        async with self._lock:
            self._state.domain = domain
            self._state.problem = problem
            verification = self._run_verification_locked()
            blueprint = self._build_blueprint_locked()
            return {
                "domain": domain,
                "problem": problem,
                "source": source,
                "verification": verification,
                "blueprint": blueprint,
            }

    async def run_verification(self) -> dict[str, Any]:
        async with self._lock:
            return self._run_verification_locked()

    def _run_verification_locked(self) -> dict[str, Any]:
        result = self._verifier.verify(self._state.domain, self._state.problem, run_asp=True)
        payload = {
            "valid": result.valid,
            "errors": result.errors,
            "warnings": result.warnings,
        }
        self._state.verification = payload
        return payload

    async def get_ui_blueprint(self) -> dict[str, Any]:
        async with self._lock:
            return self._build_blueprint_locked()

    def _build_blueprint_locked(self) -> dict[str, Any]:
        domain = self._state.domain.lower()
        problem = self._state.problem

        if "on ?x" in domain or "block" in domain:
            blueprint = self._build_blocksworld_blueprint(problem)
        elif "agentinroom" in domain or "room" in domain:
            blueprint = self._build_gridworld_blueprint(problem)
        else:
            blueprint = self._dialogue.generate_blueprint(self._state.domain, self._state.problem)

        self._state.blueprint = blueprint
        return blueprint

    def _build_blocksworld_blueprint(self, problem: str) -> dict[str, Any]:
        blocks = re.findall(r"([a-zA-Z0-9_-]+)\s*-\s*block", problem, flags=re.IGNORECASE)
        if not blocks:
            blocks = ["a", "b", "c"]

        objects = [
            {
                "id": block,
                "label": block,
                "draggable": True,
                "color": "amber",
            }
            for block in blocks
        ]
        actions = [
            {
                "type": "drag",
                "target_id": "*",
                "update_predicate": "(on {target} {destination})",
            },
            {
                "type": "click",
                "target_id": "*",
                "update_predicate": "(ontable {target})",
            },
        ]
        return {
            "layout": "canvas",
            "objects": objects,
            "actions": actions,
        }

    def _build_gridworld_blueprint(self, problem: str) -> dict[str, Any]:
        rooms = re.findall(r"([a-zA-Z0-9_-]+)\s*-\s*room", problem, flags=re.IGNORECASE)
        if not rooms:
            rooms = ["room1", "room2"]

        objects = [
            {
                "id": room,
                "label": room,
                "draggable": False,
                "color": "slate",
            }
            for room in rooms
        ]
        objects.append({
            "id": "agent",
            "label": "agent",
            "draggable": True,
            "color": "cyan",
        })
        return {
            "layout": "grid",
            "objects": objects,
            "actions": [
                {
                    "type": "click",
                    "target_id": "agent",
                    "update_predicate": "(agentinroom {destination})",
                }
            ],
        }

    def _default_grid_domain(self) -> str:
        return """(define (domain gridworld)
  (:requirements :strips :typing)
  (:types room)
  (:predicates
    (agentinroom ?r - room)
  )
)
"""

    def _default_grid_problem(self) -> str:
        return """(define (problem gridworld-problem)
  (:domain gridworld)
  (:objects room1 room2 room3 - room)
  (:init (agentinroom room1))
  (:goal (agentinroom room3))
)
"""
