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


def _extract_pddl_blocks(text: str) -> list[str]:
    """Return all fenced ```pddl (or plain ```) code blocks from *text*."""
    blocks = re.findall(r"```(?:pddl)?\s*([\s\S]*?)```", text)
    return [b.strip() for b in blocks if b.strip()]


def _pick_pddl(blocks: list[str], kind: str) -> Optional[str]:
    """Return the first block that contains ``(define (<kind>``."""
    pattern = rf"\(\s*define\s+\(\s*{re.escape(kind)}"
    for block in blocks:
        if re.search(pattern, block, re.IGNORECASE):
            return block
    return None


class EditorAgent:
    """Editor agent that uses an LLM (when a key is supplied) or falls back
    to a small set of deterministic transformations.

    Parameters
    ----------
    model_id : optional model name; defaults to ``claude-sonnet-4-6`` when an
               Anthropic key is detected, or ``gpt-4o`` for OpenAI.
    """

    def __init__(self, model_id: Optional[str] = None):
        self.model_id = model_id
        self.dialogue = DialogueManager()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process(
        self,
        text: str,
        domain: str,
        problem: str,
        api_key: Optional[str] = None,
    ) -> EditorAgentResponse:
        """Process *text* and return a response with (possibly) updated PDDL.

        If *api_key* is provided the request is forwarded to the appropriate
        LLM (Anthropic when key starts with ``sk-ant``, OpenAI otherwise).
        Otherwise a rule-based fallback is used.
        """
        if api_key:
            try:
                return self._llm_process(text, domain, problem, api_key)
            except Exception as exc:
                return EditorAgentResponse(
                    reply=f"LLM call failed: {exc}",
                    domain=domain,
                    problem=problem,
                )
        return self._rule_based_process(text, domain, problem)

    # ------------------------------------------------------------------
    # LLM path
    # ------------------------------------------------------------------

    def _llm_process(
        self, text: str, domain: str, problem: str, api_key: str
    ) -> EditorAgentResponse:
        user_msg = (
            "Current domain PDDL:\n```pddl\n"
            + domain
            + "\n```\n\nCurrent problem PDDL:\n```pddl\n"
            + problem
            + "\n```\n\nRequest: "
            + text
        )
        if api_key.startswith("sk-ant"):
            reply = self._call_anthropic(api_key, user_msg)
        else:
            reply = self._call_openai(api_key, user_msg)

        blocks = _extract_pddl_blocks(reply)
        new_domain = _pick_pddl(blocks, "domain") or domain
        new_problem = _pick_pddl(blocks, "problem") or problem

        # Strip code blocks from the prose reply shown in chat
        prose = re.sub(r"```[\s\S]*?```", "", reply).strip()
        if not prose:
            prose = self.dialogue.refinement_message()

        return EditorAgentResponse(reply=prose, domain=new_domain, problem=new_problem)

    def _call_anthropic(self, api_key: str, user_msg: str) -> str:
        from anthropic import Anthropic

        model = self.model_id or "claude-sonnet-4-6"
        client = Anthropic(api_key=api_key)
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=self.dialogue.system_prompt,
            messages=[{"role": "user", "content": user_msg}],
        )
        return response.content[0].text

    def _call_openai(self, api_key: str, user_msg: str) -> str:
        from openai import OpenAI

        model = self.model_id or "gpt-4o"
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": self.dialogue.system_prompt},
                {"role": "user", "content": user_msg},
            ],
            temperature=0,
        )
        return response.choices[0].message.content

    # ------------------------------------------------------------------
    # Rule-based fallback
    # ------------------------------------------------------------------

    def _rule_based_process(
        self, text: str, domain: str, problem: str
    ) -> EditorAgentResponse:
        normalized = text.strip().lower()
        if not normalized:
            return EditorAgentResponse(
                reply=self.dialogue.next_question(problem, []),
                domain=domain,
                problem=problem,
            )

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
