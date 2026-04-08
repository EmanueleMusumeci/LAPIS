from __future__ import annotations

import asyncio
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Ensure the repo root (parent of lapis-web/) is importable as src.*
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.lapis.agents.editor_agent import EditorAgent
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


class EditorOrchestrator:
    """State machine for editor synchronization and verification."""

    def __init__(self):
        self._lock = asyncio.Lock()
        self._state = SessionState()
        self._verifier = VerificationService()
        self._agent = EditorAgent()

    @property
    def state(self) -> SessionState:
        return self._state

    async def init_session(
        self,
        domain_name: str | None = None,
        domain_pddl: str | None = None,
        problem_pddl: str | None = None,
    ) -> dict[str, Any]:
        async with self._lock:
            if domain_pddl and problem_pddl:
                self._state.domain = domain_pddl
                self._state.problem = problem_pddl
            elif domain_name and domain_name.lower() in {"babyai", "minigrid", "gridworld"}:
                self._state.domain = self._default_grid_domain()
                self._state.problem = self._default_grid_problem()
            else:
                self._state.domain = DEFAULT_DOMAIN
                self._state.problem = DEFAULT_PROBLEM

            self._state.chat = []
            verification = self._run_verification_locked()
            return {
                "domain": self._state.domain,
                "problem": self._state.problem,
                "verification": verification,
            }

    async def process_user_message(self, text: str, api_key: str | None = None) -> dict[str, Any]:
        async with self._lock:
            user_text = text.strip()
            if user_text:
                self._state.chat.append({"role": "user", "text": user_text})

            response = self._agent.process(user_text, self._state.domain, self._state.problem, api_key=api_key)
            self._state.domain = response.domain
            self._state.problem = response.problem
            self._state.chat.append({"role": "agent", "text": response.reply})

            verification = self._run_verification_locked()
            return {
                "response": response.reply,
                "domain": self._state.domain,
                "problem": self._state.problem,
                "verification": verification,
            }

    async def sync_pddl(self, domain: str, problem: str, source: str = "text") -> dict[str, Any]:
        async with self._lock:
            self._state.domain = domain
            self._state.problem = problem
            verification = self._run_verification_locked()
            return {
                "domain": domain,
                "problem": problem,
                "source": source,
                "verification": verification,
            }

    async def run_verification(self) -> dict[str, Any]:
        async with self._lock:
            return self._run_verification_locked()

    def _run_verification_locked(self) -> dict[str, Any]:
        result = self._verifier.verify(self._state.domain, self._state.problem, run_asp=False)
        payload = {
            "valid": result.valid,
            "errors": result.errors,
            "warnings": result.warnings,
        }
        self._state.verification = payload
        return payload

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
