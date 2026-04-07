"""
CPDDL Preprocessor for ADL Features
Conditionally preprocesses PDDL files when Unified Planning cannot parse them.
"""

import subprocess
import tempfile
import logging
from pathlib import Path

logger = logging.getLogger("my_logger")

CPDDL_SIF = Path("third-party/NL2Plan/cpddl_latest.sif")


def is_adl_parsing_error(exception: Exception) -> bool:
    """
    Detect if an exception is due to unsupported ADL features in UP's PDDLReader.

    Known patterns:
    1. "Invalid literal for Fraction" - object constants in domain preconditions
    2. "Expected ')', found '('" - type unions or other ADL syntax
    3. ParseSyntaxException - general parsing errors
    4. "Name already defined" - can occur with object constants in domain
    """
    error_msg = str(exception).lower()

    # Pattern 1: Object constants parsed as numeric
    if "invalid literal" in error_msg and "fraction" in error_msg:
        return True

    # Pattern 2: Type union and ADL syntax errors
    if "expected ')'" in error_msg and "found '('" in error_msg:
        return True

    # Pattern 3: General parsing failures
    if "parsesyntaxexception" in error_msg or "parse error" in error_msg:
        return True

    # Pattern 4: Name conflicts (can happen with object constants)
    if "name" in error_msg and "already defined" in error_msg:
        return True

    # Pattern 5: Unsupported PDDL keywords
    if any(keyword in error_msg for keyword in ["either", "forall", "exists", "when"]):
        return True

    return False


def preprocess_pddl_with_cpddl(domain_path: str, problem_path: str) -> tuple[str, str] | None:
    """
    Preprocess PDDL files using CPDDL to compile away ADL features.

    Args:
        domain_path: Path to domain.pddl
        problem_path: Path to problem.pddl

    Returns:
        Tuple of (preprocessed_domain_path, preprocessed_problem_path) if successful
        None if preprocessing fails
    """
    if not CPDDL_SIF.exists():
        logger.warning(f"CPDDL container not found at {CPDDL_SIF}")
        logger.warning("Cannot preprocess ADL features. Install NL2Plan submodule with CPDDL.")
        return None

    logger.info("=" * 80)
    logger.info("CPDDL PREPROCESSING TRIGGERED")
    logger.info(f"Domain: {domain_path}")
    logger.info(f"Problem: {problem_path}")
    logger.info("=" * 80)

    try:
        # Run CPDDL to normalize the PDDL
        # CPDDL compiles ADL features (type unions, quantifiers, etc.) to simpler PDDL
        result = subprocess.run(
            [
                "apptainer", "run", str(CPDDL_SIF),
                "--max-mem", "200",  # 200MB memory limit
                str(domain_path),
                str(problem_path)
            ],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            logger.error("CPDDL preprocessing failed")
            logger.error(f"stdout: {result.stdout[:500]}")
            logger.error(f"stderr: {result.stderr[:500]}")
            return None

        # CPDDL outputs normalized PDDL to stdout
        output = result.stdout

        if not output or len(output) < 100:
            logger.error("CPDDL output too short or empty")
            return None

        # Parse CPDDL output to extract domain and problem
        # CPDDL outputs them separated, we need to split properly

        # Create temporary files for preprocessed PDDL
        temp_dir = Path(tempfile.mkdtemp(prefix="cpddl_preprocessed_"))

        preprocessed_domain = temp_dir / "preprocessed_domain.pddl"
        preprocessed_problem = temp_dir / "preprocessed_problem.pddl"

        # CPDDL outputs in a specific format - we need to parse it
        # For now, let's check what the output looks like
        logger.debug(f"CPDDL output (first 1000 chars):\n{output[:1000]}")

        # Strategy: Split output into domain and problem sections
        # Look for "(define (domain" and "(define (problem" markers

        import re

        # Find domain definition
        domain_match = re.search(r'(\(define \(domain .*?\)\s*\))', output, re.DOTALL | re.IGNORECASE)
        # Find problem definition
        problem_match = re.search(r'(\(define \(problem .*?\)\s*\))', output, re.DOTALL | re.IGNORECASE)

        if not domain_match or not problem_match:
            logger.error("Could not parse CPDDL output - domain or problem definition not found")
            logger.debug(f"Full CPDDL output:\n{output}")
            return None

        domain_content = domain_match.group(1)
        problem_content = problem_match.group(1)

        # Write preprocessed files
        preprocessed_domain.write_text(domain_content)
        preprocessed_problem.write_text(problem_content)

        logger.info(f"✓ CPDDL preprocessing successful")
        logger.info(f"  Preprocessed domain: {preprocessed_domain}")
        logger.info(f"  Preprocessed problem: {preprocessed_problem}")

        return str(preprocessed_domain), str(preprocessed_problem)

    except subprocess.TimeoutExpired:
        logger.error("CPDDL preprocessing timed out (60s limit)")
        return None
    except Exception as e:
        logger.error(f"CPDDL preprocessing error: {e}")
        import traceback
        traceback.print_exc()
        return None
