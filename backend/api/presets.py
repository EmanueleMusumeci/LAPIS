"""
presets.py — Preset loading API endpoints.

Discovers and serves available domain/problem presets from data/llmpp/.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException

from ..models import Preset, PresetList

router = APIRouter(prefix="/api", tags=["presets"])

# Path configuration
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_NL_DATA_ROOT = _REPO_ROOT / "data"
_LLMPP_ROOT = _REPO_ROOT / "third-party" / "llm-pddl" / "domains"

# Domain list
DOMAINS = ["blocksworld", "barman", "floortile", "grippers", "storage", "termes", "tyreworld"]


def _split_nl(text: str) -> list[str]:
    """
    Split a combined nl file into [domain_part, problem_part].

    The convention is: domain NL describes actions (multi-paragraph intro),
    then a blank line, then the instance description (objects, state, goal).
    """
    lines = text.splitlines()
    seen_content = False
    split_idx = None

    for i, line in enumerate(lines):
        if line.strip():
            seen_content = True
        elif seen_content:
            split_idx = i
            break

    if split_idx is None:
        return [text, ""]

    domain_part = "\n".join(lines[:split_idx]).strip()
    problem_part = "\n".join(lines[split_idx:]).strip()
    return [domain_part, problem_part]


def _load_domain_nl(domain: str) -> str:
    """Load the domain-level NL description (action descriptions) for a domain."""
    # Try llm-pddl first (cleaner single-domain description)
    llmpp_path = _LLMPP_ROOT / domain / "domain.nl"
    if llmpp_path.exists():
        return llmpp_path.read_text().strip()

    # Fall back: first paragraph of p01/nl
    nl_path = _NL_DATA_ROOT / domain / "p01" / "nl"
    if nl_path.exists():
        text = nl_path.read_text().strip()
        parts = _split_nl(text)
        return parts[0]

    return ""


def _load_problem_nl(domain: str, problem_id: str) -> str:
    """Load the problem-instance NL (world state + goal)."""
    nl_path = _NL_DATA_ROOT / domain / problem_id / "nl"
    if nl_path.exists():
        text = nl_path.read_text().strip()
        parts = _split_nl(text)
        return parts[1] if len(parts) > 1 else parts[0]
    return ""


def _discover_presets() -> list[Preset]:
    """
    Auto-discover all domains and problems from data/llmpp/.

    Returns list of Preset objects.
    """
    presets: list[Preset] = []

    if _NL_DATA_ROOT.exists():
        for domain_dir in sorted(_NL_DATA_ROOT.iterdir()):
            if not domain_dir.is_dir():
                continue

            domain = domain_dir.name

            for pid_dir in sorted(domain_dir.iterdir()):
                if not pid_dir.is_dir():
                    continue

                pid = pid_dir.name
                nl_path = pid_dir / "nl"

                if nl_path.exists():
                    label = f"{domain} {pid}"
                    presets.append(Preset(
                        id=f"{domain}_{pid}",
                        label=label,
                        domain=domain,
                        problem_id=pid,
                        domain_nl=_load_domain_nl(domain),
                        problem_nl=_load_problem_nl(domain, pid),
                    ))

    return presets


def _discover_problems(domain: str) -> list[str]:
    """Auto-discover available problem IDs for a domain from data/llmpp/."""
    domain_dir = _NL_DATA_ROOT / domain
    if not domain_dir.exists():
        return []
    return sorted([
        d.name for d in domain_dir.iterdir()
        if d.is_dir() and (d / "nl").exists()
    ])


# Cache presets on first load
_cached_presets: Optional[list[Preset]] = None


def _get_presets() -> list[Preset]:
    """Get cached presets or discover them."""
    global _cached_presets
    if _cached_presets is None:
        _cached_presets = _discover_presets()
    return _cached_presets


@router.get("/presets", response_model=PresetList)
async def get_presets() -> PresetList:
    """
    Get all available presets.

    Returns a list of preset configurations with domain and problem NL descriptions.
    """
    presets = _get_presets()
    return PresetList(presets=presets, domains=DOMAINS)


@router.get("/presets/{domain}", response_model=list[Preset])
async def get_domain_presets(domain: str) -> list[Preset]:
    """
    Get presets for a specific domain.
    """
    presets = _get_presets()
    domain_presets = [p for p in presets if p.domain == domain]

    if not domain_presets:
        raise HTTPException(status_code=404, detail=f"No presets found for domain: {domain}")

    return domain_presets


@router.get("/presets/{domain}/{problem_id}", response_model=Preset)
async def get_preset(domain: str, problem_id: str) -> Preset:
    """
    Get a specific preset by domain and problem ID.
    """
    presets = _get_presets()
    preset = next(
        (p for p in presets if p.domain == domain and p.problem_id == problem_id),
        None
    )

    if preset is None:
        raise HTTPException(
            status_code=404,
            detail=f"Preset not found: {domain}/{problem_id}"
        )

    return preset


@router.get("/domains", response_model=list[str])
async def get_domains() -> list[str]:
    """
    Get list of available domains.
    """
    return DOMAINS


@router.get("/domains/{domain}/problems", response_model=list[str])
async def get_domain_problems(domain: str) -> list[str]:
    """
    Get list of available problem IDs for a domain.
    """
    problems = _discover_problems(domain)
    if not problems:
        raise HTTPException(status_code=404, detail=f"No problems found for domain: {domain}")
    return problems


@router.post("/presets/reload")
async def reload_presets() -> dict:
    """
    Force reload of presets from disk.

    Useful after adding new preset files.
    """
    global _cached_presets
    _cached_presets = None
    presets = _get_presets()
    return {"message": "Presets reloaded", "count": len(presets)}
