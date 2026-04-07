"""
results.py — Results API for Model Race dashboard.

Loads two data sources:
1. Live benchmark results from manifold.json files in the results directory.
2. Paper Table 1 pre-aggregated baselines from paper_table1.json.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["results"])

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_RESULTS_ROOT = _REPO_ROOT / "results"
_PAPER_TABLE = _RESULTS_ROOT / "paper_table1.json"


# ── Pydantic models ───────────────────────────────────────────────────────────

class BenchmarkResult(BaseModel):
    domain: str
    problem_id: str
    method: str
    method_label: str
    model: str
    success: bool
    val_valid: bool
    plan_length: int = 0
    refinements: int = 0
    total_time: float = 0.0
    error_msg: str = ""


class BenchmarkSummary(BaseModel):
    domain: str
    method: str
    method_label: str
    model: str
    total_runs: int
    successful_runs: int
    success_rate: float
    val_rate: float
    gt_executability: Optional[float] = None
    avg_plan_length: float
    avg_refinements: float
    avg_time: float


class ModelRaceData(BaseModel):
    summaries: list[BenchmarkSummary]
    results: list[BenchmarkResult]
    domains: list[str]
    methods: list[str]
    models: list[str]


# ── Directory name → (method, method_label, model) ───────────────────────────

_METHOD_LABEL = {
    "lapis":          "LAPIS² (Adq.)",
    "lapis_adq":      "LAPIS² (Adq.)",
    "lapis_dom":      "LAPIS² (Dom.)",
    "gt_lapis_gt":    "GT-LAPIS² (GT*)",
    "gt_lapis_zero":  "GT-LAPIS² (Zero)",
    "sim_lapis":      "Sim-LAPIS²",
    "llmpp_few":      "LLM+P (Few-shot)",
    "llmpp_zero":     "LLM+P (Zero-shot)",
    "nl2plan":        "NL2Plan",
}

_MODEL_DISPLAY = {
    "claude_sonnet_4_6": "claude-sonnet-4-6",
    "gpt_4o":            "gpt-4o",
    "paper_baseline":    "paper_baseline",
}

# Regex: benchmark_{domain}_data_{N}_{model_slug}
_DIR_RE = re.compile(r"^benchmark_(.+?)_data_\d+_(.+)$")


def _parse_benchmark_dir(dir_name: str) -> tuple[str, str, str, str]:
    """Return (domain, method, method_label, model) from a benchmark directory name."""
    m = _DIR_RE.match(dir_name)
    if not m:
        return "unknown", "lapis", "LAPIS²", "unknown"
    domain = m.group(1)
    model_slug = m.group(2)
    model = _MODEL_DISPLAY.get(model_slug, model_slug.replace("_", "-"))
    method = "lapis"
    label = _METHOD_LABEL[method]
    return domain, method, label, model


# ── Scan live results ─────────────────────────────────────────────────────────

def _scan_results_directory() -> list[BenchmarkResult]:
    """Scan results directory for manifold.json files using the correct field names."""
    results: list[BenchmarkResult] = []

    if not _RESULTS_ROOT.exists():
        return results

    for manifold_path in _RESULTS_ROOT.rglob("manifold.json"):
        try:
            data = json.loads(manifold_path.read_text())

            # Infer method/model from the top-level benchmark directory name
            parts = manifold_path.relative_to(_RESULTS_ROOT).parts
            bench_dir = parts[0] if parts else ""
            domain, method, label, model = _parse_benchmark_dir(bench_dir)

            # Prefer domain from file if present
            domain = data.get("domain", domain)

            results.append(BenchmarkResult(
                domain=domain,
                problem_id=str(data.get("problem_id", "unknown")),
                method=method,
                method_label=label,
                model=model,
                # planning_successful = plan was found; val_valid = VAL accepted it
                success=data.get("planning_successful", False),
                val_valid=data.get("val_valid", False),
                plan_length=data.get("plan_length", 0),
                refinements=data.get("pddl_refinements", 0),
                total_time=data.get("timing", {}).get("total_llm_s", 0.0),
                error_msg=data.get("failure_stage", ""),
            ))
        except Exception:
            continue

    return results


# ── Load paper Table 1 ────────────────────────────────────────────────────────

def _load_paper_summaries() -> list[BenchmarkSummary]:
    """Load pre-aggregated paper Table 1 baselines."""
    if not _PAPER_TABLE.exists():
        return []
    try:
        rows = json.loads(_PAPER_TABLE.read_text())
        summaries = []
        for row in rows:
            summaries.append(BenchmarkSummary(
                domain=row["domain"],
                method=row["method"],
                method_label=row.get("method_label", row["method"]),
                model=row.get("model", "paper_baseline"),
                total_runs=row.get("total_runs", 20),
                successful_runs=row.get("successful_runs", 0),
                success_rate=row.get("success_rate", 0.0),
                val_rate=row.get("success_rate", 0.0),   # VAL rate = success_rate for paper data
                gt_executability=row.get("gt_executability"),
                avg_plan_length=row.get("avg_plan_length", 0.0),
                avg_refinements=row.get("avg_refinements", 0.0),
                avg_time=row.get("avg_time", 0.0),
            ))
        return summaries
    except Exception:
        return []


# ── Aggregate live results ────────────────────────────────────────────────────

def _aggregate_results(results: list[BenchmarkResult]) -> list[BenchmarkSummary]:
    """Aggregate live manifold.json results into per-domain/method/model summaries."""
    from collections import defaultdict

    groups: dict[tuple, list[BenchmarkResult]] = defaultdict(list)
    for r in results:
        groups[(r.domain, r.method, r.model)].append(r)

    summaries = []
    for (domain, method, model), group in groups.items():
        planned = [r for r in group if r.success]
        val_ok  = [r for r in group if r.val_valid]
        total   = len(group)

        summaries.append(BenchmarkSummary(
            domain=domain,
            method=method,
            method_label=group[0].method_label,
            model=model,
            total_runs=total,
            successful_runs=len(planned),
            success_rate=len(planned) / total if total > 0 else 0.0,
            val_rate=len(val_ok) / total if total > 0 else 0.0,
            gt_executability=None,
            avg_plan_length=sum(r.plan_length for r in planned) / len(planned) if planned else 0.0,
            avg_refinements=sum(r.refinements for r in group) / total if total > 0 else 0.0,
            avg_time=sum(r.total_time for r in group) / total if total > 0 else 0.0,
        ))

    return summaries


# ── API endpoints ─────────────────────────────────────────────────────────────

@router.get("/results", response_model=ModelRaceData)
async def get_results(
    domain: Optional[str] = Query(None),
    method: Optional[str] = Query(None),
    model:  Optional[str] = Query(None),
    source: Optional[str] = Query(None, description="'paper', 'live', or None for both"),
) -> ModelRaceData:
    """
    Get benchmark results for the Model Race dashboard.

    Merges paper Table 1 baselines with live manifold.json results.
    Use ?source=paper or ?source=live to filter by data origin.
    """
    live_results = _scan_results_directory()
    paper_summaries = _load_paper_summaries()

    # Apply filters to live results
    if domain:
        live_results = [r for r in live_results if r.domain == domain]
    if method:
        live_results = [r for r in live_results if r.method == method]
    if model:
        live_results = [r for r in live_results if r.model == model]

    live_summaries = _aggregate_results(live_results)

    # Apply filters to paper summaries
    if domain:
        paper_summaries = [s for s in paper_summaries if s.domain == domain]
    if method:
        paper_summaries = [s for s in paper_summaries if s.method == method]
    if model:
        paper_summaries = [s for s in paper_summaries if s.model == model]

    # Merge based on source filter
    if source == "paper":
        summaries = paper_summaries
        results = []
    elif source == "live":
        summaries = live_summaries
        results = live_results
    else:
        # Both: paper baselines first, then live results (live may override paper for same domain/method/model)
        live_keys = {(s.domain, s.method, s.model) for s in live_summaries}
        merged_paper = [s for s in paper_summaries if (s.domain, s.method, s.model) not in live_keys]
        summaries = merged_paper + live_summaries
        results = live_results

    domains = sorted(set(s.domain for s in summaries))
    methods = sorted(set(s.method for s in summaries))
    models  = sorted(set(s.model  for s in summaries))

    return ModelRaceData(
        summaries=summaries,
        results=results,
        domains=domains,
        methods=methods,
        models=models,
    )


@router.get("/results/summary", response_model=list[BenchmarkSummary])
async def get_results_summary(
    domain: Optional[str] = Query(None),
    method: Optional[str] = Query(None),
) -> list[BenchmarkSummary]:
    live_results = _scan_results_directory()
    paper_summaries = _load_paper_summaries()

    if domain:
        live_results = [r for r in live_results if r.domain == domain]
        paper_summaries = [s for s in paper_summaries if s.domain == domain]
    if method:
        live_results = [r for r in live_results if r.method == method]
        paper_summaries = [s for s in paper_summaries if s.method == method]

    live_summaries = _aggregate_results(live_results)
    live_keys = {(s.domain, s.method, s.model) for s in live_summaries}
    return [s for s in paper_summaries if (s.domain, s.method, s.model) not in live_keys] + live_summaries


@router.get("/results/{domain}/{problem_id}", response_model=list[BenchmarkResult])
async def get_problem_results(domain: str, problem_id: str) -> list[BenchmarkResult]:
    results = _scan_results_directory()
    filtered = [r for r in results if r.domain == domain and r.problem_id == problem_id]
    if not filtered:
        raise HTTPException(status_code=404, detail=f"No results found for {domain}/{problem_id}")
    return filtered


@router.get("/results/domains", response_model=list[str])
async def get_result_domains() -> list[str]:
    live = {r.domain for r in _scan_results_directory()}
    paper = {s.domain for s in _load_paper_summaries()}
    return sorted(live | paper)


@router.get("/results/models", response_model=list[str])
async def get_result_models() -> list[str]:
    live = {r.model for r in _scan_results_directory()}
    paper = {s.model for s in _load_paper_summaries()}
    return sorted(live | paper)
