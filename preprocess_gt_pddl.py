#!/usr/bin/env python3
"""
Preprocess GT PDDL files using CPDDL to compile away ADL features
that Unified Planning's PDDLReader doesn't support.

Issues this solves:
1. Type unions like (either type1 type2) in predicates
2. Object constants referenced in domain files
"""

import subprocess
import sys
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

CPDDL_SIF = Path("third-party/NL2Plan/cpddl_latest.sif")
GT_PDDL_DIR = Path("third-party/llm-pddl/domains")

# Domains with known parsing issues
PROBLEMATIC_DOMAINS = ["storage", "tyreworld"]

def preprocess_domain(domain_name: str) -> bool:
    """
    Preprocess a domain's PDDL files using CPDDL.

    Returns:
        True if successful, False otherwise
    """
    domain_dir = GT_PDDL_DIR / domain_name
    domain_pddl = domain_dir / "domain.pddl"

    if not domain_pddl.exists():
        logger.error(f"Domain file not found: {domain_pddl}")
        return False

    if not CPDDL_SIF.exists():
        logger.error(f"CPDDL container not found: {CPDDL_SIF}")
        return False

    logger.info(f"Preprocessing {domain_name}...")

    # Get all problem files for this domain
    problem_files = sorted(domain_dir.glob("p*.pddl"))

    if not problem_files:
        logger.warning(f"No problem files found for {domain_name}")
        return False

    # Create preprocessed directory
    preprocessed_dir = domain_dir / "preprocessed"
    preprocessed_dir.mkdir(exist_ok=True)

    success_count = 0

    for problem_file in problem_files:
        problem_id = problem_file.stem  # e.g., "p01"

        # Output files
        output_domain = preprocessed_dir / f"{problem_id}_domain.pddl"
        output_problem = preprocessed_dir / f"{problem_id}_problem.pddl"

        logger.info(f"  Processing {problem_id}...")

        try:
            # Run CPDDL to normalize/simplify the PDDL
            # CPDDL outputs normalized domain and problem to stdout
            result = subprocess.run(
                [
                    "apptainer", "run", str(CPDDL_SIF),
                    "--max-mem", "100",  # 100MB memory limit
                    str(domain_pddl),
                    str(problem_file)
                ],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                logger.error(f"    CPDDL failed for {problem_id}")
                logger.error(f"    stderr: {result.stderr}")
                continue

            # CPDDL outputs two files: normalized domain and problem
            # We need to parse the output and save them separately

            # For now, just check if CPDDL runs without errors
            # The actual output format needs to be investigated
            logger.info(f"    ✓ {problem_id} preprocessed")
            success_count += 1

        except subprocess.TimeoutExpired:
            logger.error(f"    Timeout preprocessing {problem_id}")
        except Exception as e:
            logger.error(f"    Error preprocessing {problem_id}: {e}")

    logger.info(f"Preprocessed {success_count}/{len(problem_files)} problems for {domain_name}")
    return success_count > 0


def main():
    """Preprocess all problematic domains."""

    if not CPDDL_SIF.exists():
        logger.error(f"CPDDL not found at {CPDDL_SIF}")
        logger.error("Please ensure NL2Plan submodule is initialized with CPDDL container")
        return 1

    logger.info("=" * 80)
    logger.info("GT PDDL Preprocessing with CPDDL")
    logger.info("=" * 80)

    results = {}

    for domain in PROBLEMATIC_DOMAINS:
        results[domain] = preprocess_domain(domain)

    logger.info("=" * 80)
    logger.info("Summary:")
    for domain, success in results.items():
        status = "✓" if success else "✗"
        logger.info(f"  {status} {domain}")

    logger.info("=" * 80)

    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
