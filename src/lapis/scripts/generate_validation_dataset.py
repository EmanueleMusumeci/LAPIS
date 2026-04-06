from __future__ import annotations

import argparse
from pathlib import Path
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
)

from src.lapis.agents.perturbation_agent import PerturbationAgent


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate positive/negative PDDL validation dataset")
    parser.add_argument("--source-root", default="data/llmpp", help="Path containing domain/problem folders")
    parser.add_argument("--output-root", default="data/pddl_validation", help="Dataset output path")
    parser.add_argument("--domains", nargs="*", default=None, help="Optional domain subset")
    parser.add_argument("--max-per-domain", type=int, default=1, help="How many source problems to use per domain")
    args = parser.parse_args()

    agent = PerturbationAgent()
    summary = agent.build_validation_dataset(
        source_root=Path(args.source_root),
        output_root=Path(args.output_root),
        domains=args.domains,
        max_per_domain=args.max_per_domain,
    )

    print("Validation dataset generated")
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
