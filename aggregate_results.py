#!/usr/bin/env python3
"""
Unified result aggregator for LAPIS experiments.

Aggregates benchmark results and generates paper-ready tables.

Usage:
    # Aggregate semantic verification results (Table 1 in paper)
    python aggregate_results.py --type semantic

    # Aggregate IPC baseline comparisons (direct LLM vs LAPIS)
    python aggregate_results.py --type ipc_baseline

    # Aggregate Lexicon benchmark results (Table 2 in paper)
    python aggregate_results.py --type lexicon

    # Custom input/output paths
    python aggregate_results.py --type semantic --input results_icaps2026 --output PAPER_TABLE_1.md
"""

import argparse
import json
import csv
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Optional

# Domain definitions
IPC_DOMAINS = ["blocksworld", "barman", "storage", "floortile", "grippers", "termes", "tyreworld"]
LEXICON_DOMAINS = ["blocksworld", "logistics", "sokoban", "babyai"]


class ResultAggregator:
    """Base class for result aggregation"""

    def __init__(self, input_dir: Path, output_path: Path):
        self.input_dir = Path(input_dir)
        self.output_path = Path(output_path)

    def aggregate(self):
        """Override in subclasses"""
        raise NotImplementedError

    def format_table(self, data: Dict) -> str:
        """Override in subclasses"""
        raise NotImplementedError


class SemanticResultAggregator(ResultAggregator):
    """Aggregates semantic verification benchmark results (ICAPS 2026 Table 1)"""

    def aggregate(self):
        """Load results from results_icaps2026/ or results_llmpp/"""
        results = {}

        for domain in IPC_DOMAINS:
            # Look for semantic verification runs
            pattern = f"benchmark_llmpp_{domain}_lapis_domgen_full_adequacy_*"
            matching_dirs = list(self.input_dir.glob(pattern))

            if not matching_dirs:
                print(f"Warning: No semantic results found for {domain}")
                continue

            # Take the most recent run
            latest_dir = max(matching_dirs, key=lambda p: p.stat().st_mtime)

            # Find timestamp subdirectory
            timestamp_dirs = [d for d in latest_dir.iterdir() if d.is_dir()]
            if not timestamp_dirs:
                continue

            timestamp_dir = timestamp_dirs[0]
            csv_path = timestamp_dir / "results.csv"

            if csv_path.exists():
                success_count = 0
                total_count = 0

                with open(csv_path, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        total_count += 1
                        if row.get('val_valid') == 'True' or row.get('planning_successful') == 'True':
                            success_count += 1

                results[domain] = {
                    'success': success_count,
                    'total': total_count,
                    'rate': (success_count / total_count * 100) if total_count > 0 else 0
                }

        return results

    def format_table(self, results: Dict) -> str:
        """Format as markdown table for paper"""
        lines = [
            "# LAPIS Semantic Verification Results (ICAPS 2026 Table 1)",
            "",
            "| Domain | Success Rate | Problems |",
            "|--------|:------------:|:--------:|"
        ]

        for domain in IPC_DOMAINS:
            if domain in results:
                r = results[domain]
                lines.append(f"| **{domain.capitalize()}** | {r['rate']:.0f}% ({r['success']}/{r['total']}) | {r['total']} |")
            else:
                lines.append(f"| **{domain.capitalize()}** | — | — |")

        # Calculate average
        total_success = sum(r['success'] for r in results.values())
        total_problems = sum(r['total'] for r in results.values())
        avg_rate = (total_success / total_problems * 100) if total_problems > 0 else 0

        lines.append(f"| **Average** | **{avg_rate:.1f}%** | **{total_problems}** |")
        lines.append("")
        lines.append(f"*Generated from: {self.input_dir}*")

        return "\n".join(lines)


class IPCBaselineAggregator(ResultAggregator):
    """Aggregates IPC baseline results (Direct LLM vs LAPIS comparison)"""

    def aggregate(self):
        """Load baseline results and compare with LAPIS"""
        results = {}

        # Load LAPIS results (hardcoded from paper Table 1 as ground truth)
        lapis_results = {
            "blocksworld": {"val_success_rate": 100.0, "total": 20},
            "storage": {"val_success_rate": 55.0, "total": 20},
            "tyreworld": {"val_success_rate": 55.0, "total": 20},
            "floortile": {"val_success_rate": 65.0, "total": 20}
        }

        # Load baseline results from results_ipc_baselines/
        baseline_dir = self.input_dir / "baselines"
        if not baseline_dir.exists():
            print(f"Warning: Baseline directory not found: {baseline_dir}")
            return {}

        for model_dir in baseline_dir.iterdir():
            if not model_dir.is_dir():
                continue

            model_name = model_dir.name
            summary_file = model_dir / "summary.json"

            if not summary_file.exists():
                continue

            with open(summary_file, 'r') as f:
                data = json.load(f)

            for domain in data.get("results", {}).keys():
                if domain not in results:
                    results[domain] = {
                        "lapis": lapis_results.get(domain, {}),
                        "baselines": {}
                    }
                results[domain]["baselines"][model_name] = data["results"][domain]

        return results

    def format_table(self, results: Dict) -> str:
        """Format comparison table"""
        lines = [
            "# IPC Baseline Comparison (Direct LLM vs LAPIS)",
            "",
            "| Domain | LAPIS | GPT-5.4 | Claude Opus 4.6 | Gemini 3.1 Pro |",
            "|--------|:-----:|:-------:|:---------------:|:--------------:|"
        ]

        for domain in ["blocksworld", "storage", "tyreworld", "floortile"]:
            if domain not in results:
                continue

            lapis_rate = results[domain]["lapis"].get("val_success_rate", 0)
            row = [f"| **{domain.capitalize()}**", f"{lapis_rate:.0f}%"]

            for model in ["gpt-5.4", "claude-opus-4.6", "gemini-3.1-pro"]:
                baseline = results[domain]["baselines"].get(model, {})
                val_rate = baseline.get("val_valid_rate", 0)
                row.append(f"{val_rate:.0f}%")

            lines.append(" | ".join(row) + " |")

        lines.append("")
        lines.append("*LAPIS uses PDDL synthesis + classical planner. Baselines use direct LLM planning (no PDDL).*")
        lines.append(f"*Generated from: {self.input_dir}*")

        return "\n".join(lines)


class LexiconAggregator(ResultAggregator):
    """Aggregates Lexicon benchmark results (Table 2 in paper)"""

    def aggregate(self):
        """Load Lexicon results"""
        results = {}

        # Load LAPIS results
        lapis_dir = self.input_dir / "lapis_gt"
        if lapis_dir.exists():
            for domain_dir in lapis_dir.iterdir():
                if not domain_dir.is_dir():
                    continue

                domain = domain_dir.name
                csv_path = domain_dir / "results.csv"

                if csv_path.exists():
                    success_count = 0
                    total_count = 0

                    with open(csv_path, 'r') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            total_count += 1
                            if row.get('val_valid') == 'True':
                                success_count += 1

                    if domain not in results:
                        results[domain] = {}
                    results[domain]["lapis"] = (success_count / total_count * 100) if total_count > 0 else 0

        # Load baseline results
        baseline_dir = self.input_dir / "baselines"
        if baseline_dir.exists():
            for model_dir in baseline_dir.iterdir():
                if not model_dir.is_dir():
                    continue

                model_name = model_dir.name
                summary_file = model_dir / "summary.json"

                if summary_file.exists():
                    with open(summary_file, 'r') as f:
                        data = json.load(f)

                    for domain, metrics in data.get("results", {}).items():
                        if domain not in results:
                            results[domain] = {}
                        results[domain][model_name] = metrics.get("val_valid_rate", 0)

        return results

    def format_table(self, results: Dict) -> str:
        """Format as markdown table"""
        lines = [
            "# Lexicon Benchmark Results (Table 2)",
            "",
            "| Model | Blocksworld | Logistics | Sokoban | BabyAI |",
            "|-------|:-----------:|:---------:|:-------:|:------:|"
        ]

        models = ["o3", "gemini-2.5", "deepseek-r1", "claude-3.7", "lapis"]

        for model in models:
            row = [f"| **{model.upper() if model != 'lapis' else 'LAPIS/GT'}**"]
            for domain in LEXICON_DOMAINS:
                if domain in results and model in results[domain]:
                    rate = results[domain][model]
                    row.append(f"{rate:.0f}")
                else:
                    row.append("—")
            lines.append(" | ".join(row) + " |")

        lines.append("")
        lines.append(f"*Generated from: {self.input_dir}*")

        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Aggregate LAPIS benchmark results")
    parser.add_argument("--type", required=True,
                        choices=["semantic", "ipc_baseline", "lexicon"],
                        help="Type of results to aggregate")
    parser.add_argument("--input", default=None,
                        help="Input directory (default depends on type)")
    parser.add_argument("--output", default=None,
                        help="Output file (default: RESULTS_{TYPE}.md)")

    args = parser.parse_args()

    # Set defaults based on type
    if args.input is None:
        defaults = {
            "semantic": "results_icaps2026",
            "ipc_baseline": "results_ipc_baselines",
            "lexicon": "results_lexicon_standardized"
        }
        args.input = defaults[args.type]

    if args.output is None:
        args.output = f"RESULTS_{args.type.upper()}.md"

    # Select aggregator
    aggregators = {
        "semantic": SemanticResultAggregator,
        "ipc_baseline": IPCBaselineAggregator,
        "lexicon": LexiconAggregator
    }

    aggregator_class = aggregators[args.type]
    aggregator = aggregator_class(input_dir=args.input, output_path=args.output)

    print(f"Aggregating {args.type} results from {args.input}...")
    results = aggregator.aggregate()

    if not results:
        print("ERROR: No results found")
        return

    print(f"Found results for {len(results)} domains")

    table = aggregator.format_table(results)

    # Write output
    with open(args.output, 'w') as f:
        f.write(table)

    print(f"\n✓ Results written to: {args.output}")
    print("\nPreview:")
    print(table)


if __name__ == "__main__":
    main()
