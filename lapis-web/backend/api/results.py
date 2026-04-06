"""
results.py — Results API for Model Race dashboard.

Provides access to benchmark results for visualization.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["results"])

# Path configuration
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_RESULTS_ROOT = _REPO_ROOT / "results"


class BenchmarkResult(BaseModel):
    """Single benchmark run result."""
    domain: str
    problem_id: str
    method: str
    model: str
    success: bool
    plan_length: int = 0
    refinements: int = 0
    total_time: float = 0.0
    error_msg: str = ""


class BenchmarkSummary(BaseModel):
    """Aggregated benchmark summary."""
    domain: str
    method: str
    model: str
    total_runs: int
    successful_runs: int
    success_rate: float
    avg_plan_length: float
    avg_refinements: float
    avg_time: float


class ModelRaceData(BaseModel):
    """Full model race comparison data."""
    summaries: list[BenchmarkSummary]
    results: list[BenchmarkResult]
    domains: list[str]
    methods: list[str]
    models: list[str]


def _load_results_file(path: Path) -> list[dict]:
    """Load results from a JSON file."""
    if not path.exists():
        return []
    try:
        with open(path) as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return [data]
    except Exception:
        return []


def _scan_results_directory() -> list[BenchmarkResult]:
    """Scan results directory for benchmark results."""
    results: list[BenchmarkResult] = []

    if not _RESULTS_ROOT.exists():
        return results

    # Look for manifold.json files in result directories
    for result_dir in _RESULTS_ROOT.rglob("manifold.json"):
        try:
            data = json.loads(result_dir.read_text())
            # Extract result info
            results.append(BenchmarkResult(
                domain=data.get("domain", "unknown"),
                problem_id=data.get("problem_id", "unknown"),
                method=data.get("method", "unknown"),
                model=data.get("model", "unknown"),
                success=data.get("success", False),
                plan_length=data.get("plan_length", 0),
                refinements=data.get("refinements", 0),
                total_time=data.get("total_time", 0.0),
                error_msg=data.get("error_msg", ""),
            ))
        except Exception:
            continue

    # Also try loading full_comparison.json if it exists
    comparison_path = _RESULTS_ROOT / "full_comparison.json"
    if comparison_path.exists():
        try:
            data = json.loads(comparison_path.read_text())
            if isinstance(data, list):
                for item in data:
                    results.append(BenchmarkResult(
                        domain=item.get("domain", "unknown"),
                        problem_id=item.get("problem_id", "unknown"),
                        method=item.get("method", "unknown"),
                        model=item.get("model", "unknown"),
                        success=item.get("success", False),
                        plan_length=item.get("plan_length", 0),
                        refinements=item.get("refinements", 0),
                        total_time=item.get("total_time", 0.0),
                        error_msg=item.get("error_msg", ""),
                    ))
        except Exception:
            pass

    return results


def _aggregate_results(results: list[BenchmarkResult]) -> list[BenchmarkSummary]:
    """Aggregate results into summaries by domain/method/model."""
    from collections import defaultdict

    groups: dict[tuple, list[BenchmarkResult]] = defaultdict(list)

    for r in results:
        key = (r.domain, r.method, r.model)
        groups[key].append(r)

    summaries = []
    for (domain, method, model), group in groups.items():
        successful = [r for r in group if r.success]
        total = len(group)
        success_count = len(successful)

        summaries.append(BenchmarkSummary(
            domain=domain,
            method=method,
            model=model,
            total_runs=total,
            successful_runs=success_count,
            success_rate=success_count / total if total > 0 else 0.0,
            avg_plan_length=sum(r.plan_length for r in successful) / success_count if success_count > 0 else 0.0,
            avg_refinements=sum(r.refinements for r in successful) / success_count if success_count > 0 else 0.0,
            avg_time=sum(r.total_time for r in group) / total if total > 0 else 0.0,
        ))

    return summaries


@router.get("/results", response_model=ModelRaceData)
async def get_results(
    domain: Optional[str] = Query(None, description="Filter by domain"),
    method: Optional[str] = Query(None, description="Filter by method (lapis/llmpp)"),
    model: Optional[str] = Query(None, description="Filter by model"),
) -> ModelRaceData:
    """
    Get benchmark results for the Model Race dashboard.

    Optionally filter by domain, method, or model.
    """
    results = _scan_results_directory()

    # Apply filters
    if domain:
        results = [r for r in results if r.domain == domain]
    if method:
        results = [r for r in results if r.method == method]
    if model:
        results = [r for r in results if r.model == model]

    summaries = _aggregate_results(results)

    # Extract unique values
    domains = sorted(set(r.domain for r in results))
    methods = sorted(set(r.method for r in results))
    models = sorted(set(r.model for r in results))

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
    """
    Get aggregated benchmark summaries.
    """
    results = _scan_results_directory()

    if domain:
        results = [r for r in results if r.domain == domain]
    if method:
        results = [r for r in results if r.method == method]

    return _aggregate_results(results)


@router.get("/results/{domain}/{problem_id}", response_model=list[BenchmarkResult])
async def get_problem_results(domain: str, problem_id: str) -> list[BenchmarkResult]:
    """
    Get all results for a specific domain/problem combination.
    """
    results = _scan_results_directory()
    filtered = [r for r in results if r.domain == domain and r.problem_id == problem_id]

    if not filtered:
        raise HTTPException(
            status_code=404,
            detail=f"No results found for {domain}/{problem_id}"
        )

    return filtered


@router.get("/results/domains", response_model=list[str])
async def get_result_domains() -> list[str]:
    """
    Get list of domains that have benchmark results.
    """
    results = _scan_results_directory()
    return sorted(set(r.domain for r in results))


@router.get("/results/models", response_model=list[str])
async def get_result_models() -> list[str]:
    """
    Get list of models that have benchmark results.
    """
    results = _scan_results_directory()
    return sorted(set(r.model for r in results))
