from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from .dialogue_manager import DialogueManager


@dataclass
class EditorAgentResponse:
    """Structured response from the editor agent."""

    reply: str
    domain: str
    problem: str


class EditorAgent:
    """Lightweight editor agent for PDDL refinement conversations.

    The class is deterministic by default and applies a small set of safe,
    local transformations. It can be replaced later by a real LLM-backed
    implementation without changing the orchestrator contract.
    """

    def __init__(self, model_id: Optional[str] = None):
        self.model_id = model_id or "rule-based-editor"
        self.dialogue = DialogueManager()

    def process(self, text: str, domain: str, problem: str) -> EditorAgentResponse:
        normalized = text.strip().lower()
        if not normalized:
            return EditorAgentResponse(
                reply=self.dialogue.next_question(problem, []),
                domain=domain,
                problem=problem,
            )

        # Minimal safe automation for common editing intents.
        if "make goal" in normalized and "on " in normalized:
            goal_match = re.search(r"on\s+([a-zA-Z0-9_-]+)\s+([a-zA-Z0-9_-]+)", normalized)
            if goal_match:
                a, b = goal_match.group(1), goal_match.group(2)
                updated_problem = re.sub(
                    r"\(:goal[\s\S]*?\)\s*\)$",
                    f"(:goal (on {a} {b}))\n)",
                    problem,
                    flags=re.IGNORECASE,
                )
                return EditorAgentResponse(
                    reply=f"Updated goal to (on {a} {b}). {self.dialogue.refinement_message()}",
                    domain=domain,
                    problem=updated_problem,
                )

        if "add clear predicate" in normalized and "(clear" not in domain:
            updated_domain = domain.replace(
                "(:predicates",
                "(:predicates\n    (clear ?x)",
                1,
            )
            return EditorAgentResponse(
                reply=f"Added a generic clear predicate declaration to the domain. {self.dialogue.refinement_message()}",
                domain=updated_domain,
                problem=problem,
            )

        return EditorAgentResponse(
            reply=self.dialogue.next_question(problem, []),
            domain=domain,
            problem=problem,
        )
