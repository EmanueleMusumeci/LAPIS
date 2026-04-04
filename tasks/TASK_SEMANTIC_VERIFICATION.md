# Task: Implement Lightweight Semantic Verification

**Priority**: Nice-to-have (implement after paper draft is complete)
**Estimated Time**: 4-6 hours implementation + 4-8 hours experiments
**Dependencies**: None (can run in parallel with paper writing)

---

## Objective

Implement a lightweight structural analyzer that catches semantically broken PDDL files that VAL approves. This differentiates LAPIS from ISR-LLM and adds genuine value to the demo.

---

## Background

VAL only checks syntactic correctness. Planetarium (NAACL 2025) showed that 96% of LLM-generated PDDL is syntactically valid but only 25% is semantically correct. A domain can pass VAL while modeling completely wrong physics.

The full semantic verification from the fairness analysis includes:
1. Structural analysis (predicate coverage, action reachability) - **IMPLEMENT THIS**
2. NL round-trip verification - **SKIP** (too complex for 3 days)

---

## Implementation Specification

### Location
Create: `src/lapis/planner/low/semantic_verification.py`

### Core Functions

```python
def check_predicate_coverage(domain_pddl: str, problem_pddl: str) -> dict:
    """
    Check if all goal predicates can potentially be achieved.

    Returns:
        {
            "passed": bool,
            "goal_predicates": list[str],
            "achievable_predicates": list[str],  # predicates in action effects
            "unreachable_goals": list[str],  # goal predicates not in any effect
            "diagnosis": str
        }
    """
    pass

def check_action_reachability(domain_pddl: str, problem_pddl: str) -> dict:
    """
    Check if actions can fire given init state.

    A simple check: for each action, check if at least one grounding
    of its preconditions could be satisfied given init predicates.

    Returns:
        {
            "passed": bool,
            "total_actions": int,
            "reachable_actions": list[str],
            "unreachable_actions": list[str],  # actions that can never fire
            "diagnosis": str
        }
    """
    pass

def check_type_grounding(domain_pddl: str, problem_pddl: str) -> dict:
    """
    Check if all action parameters have at least one valid object.

    Returns:
        {
            "passed": bool,
            "ungrounded_params": list[tuple[str, str]],  # (action, param_type)
            "diagnosis": str
        }
    """
    pass

def run_semantic_checks(domain_pddl: str, problem_pddl: str) -> dict:
    """
    Run all semantic checks and return aggregated result.

    Returns:
        {
            "passed": bool,  # all checks passed
            "checks": {
                "predicate_coverage": {...},
                "action_reachability": {...},
                "type_grounding": {...}
            },
            "combined_diagnosis": str  # for LLM refinement prompt
        }
    """
    pass
```

### Integration Points

1. **In refinement loop** (`src/lapis/pipelines/lapis_low_level.py`):
   - After VAL passes, run semantic checks
   - If semantic checks fail, include diagnosis in refinement prompt
   - This catches problems before wasting planner time

2. **In Streamlit demo** (`demo/app.py` or `demo/app_premium.py`):
   - Add "Semantic Analysis" panel showing check results
   - Color-code: green (passed), red (failed), yellow (warning)

### PDDL Parsing

Use existing parsing utilities or simple regex. Don't over-engineer:

```python
import re

def extract_predicates_from_effects(domain_pddl: str) -> set:
    """Extract predicate names that appear in action effects."""
    # Match (predicate-name ...) in :effect blocks
    effects = re.findall(r':effect\s*\(and(.*?)\)\s*\)', domain_pddl, re.DOTALL)
    predicates = set()
    for effect in effects:
        # Match positive effects (predicate ...)
        predicates.update(re.findall(r'\((\w+)\s', effect))
    return predicates

def extract_goal_predicates(problem_pddl: str) -> set:
    """Extract predicate names from goal."""
    goal_match = re.search(r':goal\s*\((.*)\)\s*\)', problem_pddl, re.DOTALL)
    if goal_match:
        return set(re.findall(r'\((\w+)\s', goal_match.group(1)))
    return set()
```

---

## Testing

### Unit Tests
Create: `tests/test_semantic_verification.py`

```python
def test_unreachable_goal():
    """Goal predicate not in any action effect."""
    domain = """
    (define (domain test)
      (:predicates (on ?x ?y) (clear ?x))
      (:action move
        :parameters (?x ?y)
        :precondition (clear ?x)
        :effect (on ?x ?y)))
    """
    problem = """
    (define (problem test-p)
      (:domain test)
      (:objects a b)
      (:init (clear a))
      (:goal (holding a)))  ; 'holding' never appears in effects
    """
    result = check_predicate_coverage(domain, problem)
    assert not result["passed"]
    assert "holding" in result["unreachable_goals"]

def test_unreachable_action():
    """Action preconditions can never be satisfied."""
    domain = """
    (define (domain test)
      (:predicates (on ?x ?y) (magic ?x))
      (:action move
        :parameters (?x ?y)
        :precondition (magic ?x)  ; 'magic' never in init or effects
        :effect (on ?x ?y)))
    """
    problem = """
    (define (problem test-p)
      (:domain test)
      (:objects a b)
      (:init (on a b))
      (:goal (on b a)))
    """
    result = check_action_reachability(domain, problem)
    assert not result["passed"]
    assert "move" in result["unreachable_actions"]
```

### Integration Test
Run on a known-bad generated domain from previous experiments (one that passed VAL but failed oracle).

---

## Experiment Protocol

After implementation, re-run experiments with semantic verification enabled:

```bash
# Run with semantic checks
python run_llmpp_benchmark.py \
    --domain storage \
    --method lapis \
    --generate_domain \
    --ablation full \
    --semantic_checks \
    --model claude-sonnet-4-6

# Compare success rates:
# 1. Without semantic checks (baseline)
# 2. With semantic checks (should improve or stay same)
```

Track metrics:
- How many problems fail semantic checks before planning?
- How many of those would have failed oracle anyway?
- Does early detection reduce total API calls?

---

## Success Criteria

1. Catches at least 50% of "VAL-valid but oracle-invalid" cases
2. No false positives (doesn't reject valid domains)
3. Adds <1 second to pipeline latency
4. Clean integration with Streamlit demo

---

## What NOT To Do

- Don't implement NL round-trip verification (too complex)
- Don't try to check full semantic correctness (impossible without simulation)
- Don't block paper submission on this feature
