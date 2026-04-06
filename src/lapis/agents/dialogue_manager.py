from __future__ import annotations

import random
import re
from pathlib import Path
from typing import Any

import yaml


class DialogueManager:
    """Prompt-aware helper for clarification and blueprint suggestions."""

    def __init__(self):
        prompt_path = Path(__file__).resolve().parent / "prompts" / "editor.yaml"
        data = yaml.safe_load(prompt_path.read_text())
        self.system_prompt: str = data.get("system_prompt", "")
        self.clarify_templates: list[str] = list(data.get("clarify_templates", []))
        self.refine_templates: list[str] = list(data.get("refine_templates", []))

    def next_question(self, pddl: str, errors: list[str]) -> str:
        """Generate a concise clarifying follow-up.

        If verification errors exist, ask a focused question tied to the first
        error. Otherwise choose a generic architectural clarification.
        """
        if errors:
            err = errors[0]
            token = re.search(r"[a-zA-Z0-9_-]+", err)
            if token:
                return f"Should I revise `{token.group(0)}` directly in :init, :goal, or action schemas?"
            return "I found a verification issue. Do you want me to fix it minimally or refactor related actions?"

        if not self.clarify_templates:
            return "Do you want me to apply a minimal change or a broader refactor?"
        return random.choice(self.clarify_templates)

    def refinement_message(self) -> str:
        if not self.refine_templates:
            return "Applied a local refinement."
        return random.choice(self.refine_templates)

    def generate_blueprint(self, domain: str, problem: str) -> dict[str, Any]:
        """Provide a compact fallback blueprint for custom domains."""
        facts = re.findall(r"\(([a-zA-Z0-9_-]+)\s+([^\)]*)\)", problem)
        objects = [
            {
                "id": f"fact-{idx}",
                "label": f"{name} {args}".strip(),
                "draggable": False,
            }
            for idx, (name, args) in enumerate(facts[:6])
        ]
        return {
            "layout": "form",
            "objects": objects,
            "actions": [],
        }
