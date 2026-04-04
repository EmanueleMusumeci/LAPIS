"""
Unit tests for semantic verification module.

Tests cover:
1. Predicate coverage: detecting unreachable goal predicates
2. Action reachability: detecting actions that can never fire
3. Type grounding: detecting parameter types with no objects
4. Predicate definition: detecting undefined predicates in init/goal
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lapis.planner.low.semantic_verification import (
    check_predicate_coverage,
    check_action_reachability,
    check_type_grounding,
    check_init_predicates_defined,
    check_goal_predicates_defined,
    run_semantic_checks,
    format_semantic_report,
)


# ============================================================================
# Test: Predicate Coverage
# ============================================================================

class TestPredicateCoverage:
    """Tests for check_predicate_coverage function."""

    def test_unreachable_goal_predicate(self):
        """Goal predicate 'holding' not in any action effect."""
        domain = """
        (define (domain test)
          (:requirements :strips)
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
          (:goal (holding a)))
        """
        result = check_predicate_coverage(domain, problem)
        assert not result["passed"]
        assert "holding" in result["unreachable_goals"]

    def test_goal_achievable_via_effect(self):
        """Goal predicate 'on' is produced by move action."""
        domain = """
        (define (domain test)
          (:requirements :strips)
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
          (:goal (on a b)))
        """
        result = check_predicate_coverage(domain, problem)
        assert result["passed"]
        assert len(result["unreachable_goals"]) == 0

    def test_goal_already_in_init(self):
        """Goal predicate already true in init state."""
        domain = """
        (define (domain test)
          (:predicates (at ?x ?y))
          (:action dummy
            :parameters (?x)
            :precondition (at ?x ?x)
            :effect (at ?x ?x)))
        """
        problem = """
        (define (problem test-p)
          (:domain test)
          (:objects a b)
          (:init (at a b))
          (:goal (at a b)))
        """
        result = check_predicate_coverage(domain, problem)
        assert result["passed"]

    def test_multiple_unreachable_goals(self):
        """Multiple goal predicates not achievable."""
        domain = """
        (define (domain test)
          (:predicates (on ?x ?y))
          (:action stack
            :parameters (?x ?y)
            :precondition (on ?x ?x)
            :effect (on ?x ?y)))
        """
        problem = """
        (define (problem test-p)
          (:domain test)
          (:objects a b)
          (:init (on a a))
          (:goal (and (holding a) (grasping b))))
        """
        result = check_predicate_coverage(domain, problem)
        assert not result["passed"]
        assert "holding" in result["unreachable_goals"]
        assert "grasping" in result["unreachable_goals"]


# ============================================================================
# Test: Action Reachability
# ============================================================================

class TestActionReachability:
    """Tests for check_action_reachability function."""

    def test_unreachable_action(self):
        """Action precondition 'magic' can never be satisfied."""
        domain = """
        (define (domain test)
          (:predicates (on ?x ?y) (magic ?x))
          (:action move
            :parameters (?x ?y)
            :precondition (magic ?x)
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

    def test_reachable_action(self):
        """Action preconditions can be satisfied from init."""
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
          (:goal (on a b)))
        """
        result = check_action_reachability(domain, problem)
        assert result["passed"]
        assert "move" in result["reachable_actions"]

    def test_action_no_preconditions(self):
        """Action with no preconditions is always reachable."""
        domain = """
        (define (domain test)
          (:predicates (done))
          (:action finish
            :parameters ()
            :precondition ()
            :effect (done)))
        """
        problem = """
        (define (problem test-p)
          (:domain test)
          (:init)
          (:goal (done)))
        """
        result = check_action_reachability(domain, problem)
        assert result["passed"]

    def test_transitive_reachability(self):
        """Action reachable via chain of effects."""
        domain = """
        (define (domain test)
          (:predicates (a) (b) (c))
          (:action step1
            :parameters ()
            :precondition (a)
            :effect (b))
          (:action step2
            :parameters ()
            :precondition (b)
            :effect (c)))
        """
        problem = """
        (define (problem test-p)
          (:domain test)
          (:init (a))
          (:goal (c)))
        """
        result = check_action_reachability(domain, problem)
        assert result["passed"]
        assert "step1" in result["reachable_actions"]
        assert "step2" in result["reachable_actions"]


# ============================================================================
# Test: Type Grounding
# ============================================================================

class TestTypeGrounding:
    """Tests for check_type_grounding function."""

    def test_ungrounded_parameter(self):
        """Action parameter type has no objects."""
        domain = """
        (define (domain test)
          (:types block robot)
          (:predicates (holding ?r - robot ?b - block))
          (:action pickup
            :parameters (?r - robot ?b - block)
            :precondition ()
            :effect (holding ?r ?b)))
        """
        problem = """
        (define (problem test-p)
          (:domain test)
          (:objects b1 b2 - block)
          (:init)
          (:goal (holding r1 b1)))
        """
        result = check_type_grounding(domain, problem)
        assert not result["passed"]
        assert ("pickup", "robot") in result["ungrounded_params"]

    def test_grounded_parameters(self):
        """All parameter types have objects."""
        domain = """
        (define (domain test)
          (:types block robot)
          (:predicates (holding ?r - robot ?b - block))
          (:action pickup
            :parameters (?r - robot ?b - block)
            :precondition ()
            :effect (holding ?r ?b)))
        """
        problem = """
        (define (problem test-p)
          (:domain test)
          (:objects b1 b2 - block r1 - robot)
          (:init)
          (:goal (holding r1 b1)))
        """
        result = check_type_grounding(domain, problem)
        assert result["passed"]
        assert len(result["ungrounded_params"]) == 0

    def test_subtype_grounding(self):
        """Subtype objects satisfy supertype parameters."""
        domain = """
        (define (domain test)
          (:types movable - object
                  block - movable)
          (:predicates (moved ?x - movable))
          (:action move
            :parameters (?x - movable)
            :precondition ()
            :effect (moved ?x)))
        """
        problem = """
        (define (problem test-p)
          (:domain test)
          (:objects b1 - block)
          (:init)
          (:goal (moved b1)))
        """
        result = check_type_grounding(domain, problem)
        assert result["passed"]


# ============================================================================
# Test: Predicate Definition
# ============================================================================

class TestPredicateDefinition:
    """Tests for undefined predicate checks."""

    def test_undefined_init_predicate(self):
        """Init uses predicate not defined in domain."""
        domain = """
        (define (domain test)
          (:predicates (on ?x ?y))
          (:action move
            :parameters (?x ?y)
            :precondition (on ?x ?x)
            :effect (on ?x ?y)))
        """
        problem = """
        (define (problem test-p)
          (:domain test)
          (:objects a b)
          (:init (clear a) (ontable b))
          (:goal (on a b)))
        """
        result = check_init_predicates_defined(domain, problem)
        assert not result["passed"]
        assert "clear" in result["undefined_predicates"]
        assert "ontable" in result["undefined_predicates"]

    def test_undefined_goal_predicate(self):
        """Goal uses predicate not defined in domain."""
        domain = """
        (define (domain test)
          (:predicates (on ?x ?y))
          (:action stack
            :parameters (?x ?y)
            :precondition (on ?x ?x)
            :effect (on ?x ?y)))
        """
        problem = """
        (define (problem test-p)
          (:domain test)
          (:objects a b)
          (:init (on a a))
          (:goal (and (on a b) (holding a))))
        """
        result = check_goal_predicates_defined(domain, problem)
        assert not result["passed"]
        assert "holding" in result["undefined_predicates"]


# ============================================================================
# Test: Full Semantic Check
# ============================================================================

class TestRunSemanticChecks:
    """Tests for run_semantic_checks aggregator."""

    def test_all_checks_pass(self):
        """Valid domain and problem pass all checks."""
        domain = """
        (define (domain blocksworld)
          (:requirements :strips)
          (:types block)
          (:predicates
            (on ?x - block ?y - block)
            (ontable ?x - block)
            (clear ?x - block)
            (holding ?x - block)
            (arm-empty))
          (:action pick-up
            :parameters (?x - block)
            :precondition (and (clear ?x) (ontable ?x) (arm-empty))
            :effect (and (holding ?x) (not (ontable ?x)) (not (clear ?x)) (not (arm-empty))))
          (:action put-down
            :parameters (?x - block)
            :precondition (holding ?x)
            :effect (and (ontable ?x) (clear ?x) (arm-empty) (not (holding ?x))))
          (:action stack
            :parameters (?x - block ?y - block)
            :precondition (and (holding ?x) (clear ?y))
            :effect (and (on ?x ?y) (clear ?x) (arm-empty) (not (holding ?x)) (not (clear ?y))))
          (:action unstack
            :parameters (?x - block ?y - block)
            :precondition (and (on ?x ?y) (clear ?x) (arm-empty))
            :effect (and (holding ?x) (clear ?y) (not (on ?x ?y)) (not (clear ?x)) (not (arm-empty)))))
        """
        problem = """
        (define (problem blocks-4-1)
          (:domain blocksworld)
          (:objects b1 b2 b3 - block)
          (:init
            (clear b1) (clear b2) (clear b3)
            (ontable b1) (ontable b2) (ontable b3)
            (arm-empty))
          (:goal (and (on b1 b2) (on b2 b3))))
        """
        result = run_semantic_checks(domain, problem)
        assert result["passed"]
        assert "All semantic checks passed" in result["combined_diagnosis"]

    def test_multiple_failures(self):
        """Domain with multiple semantic issues."""
        domain = """
        (define (domain broken)
          (:predicates (on ?x ?y))
          (:action impossible
            :parameters (?x)
            :precondition (magic ?x)
            :effect (on ?x ?x)))
        """
        problem = """
        (define (problem broken-p)
          (:domain broken)
          (:objects a - thing)
          (:init (ready a))
          (:goal (holding a)))
        """
        result = run_semantic_checks(domain, problem)
        assert not result["passed"]
        # Should have multiple issues in diagnosis
        assert "SEMANTIC ERROR" in result["combined_diagnosis"]

    def test_format_report(self):
        """Report formatting works correctly."""
        domain = """
        (define (domain test)
          (:predicates (on ?x ?y))
          (:action move
            :parameters (?x ?y)
            :precondition ()
            :effect (on ?x ?y)))
        """
        problem = """
        (define (problem test-p)
          (:domain test)
          (:objects a b)
          (:init)
          (:goal (on a b)))
        """
        result = run_semantic_checks(domain, problem)
        report = format_semantic_report(result)
        assert "SEMANTIC VERIFICATION REPORT" in report
        assert "Overall Status:" in report


# ============================================================================
# Test: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and robustness."""

    def test_empty_domain(self):
        """Handle minimal/empty domain gracefully."""
        domain = "(define (domain empty))"
        problem = """
        (define (problem empty-p)
          (:domain empty)
          (:init)
          (:goal ()))
        """
        # Should not crash
        result = run_semantic_checks(domain, problem)
        assert isinstance(result, dict)
        assert "passed" in result

    def test_comments_ignored(self):
        """PDDL comments should not affect parsing."""
        domain = """
        ; This is a comment
        (define (domain test)
          ; Another comment
          (:predicates (on ?x ?y))  ; inline comment
          (:action move
            :parameters (?x ?y)
            :precondition ()
            :effect (on ?x ?y)))
        """
        problem = """
        ; Problem comment
        (define (problem test-p)
          (:domain test)
          (:objects a b)
          (:init)
          (:goal (on a b)))
        """
        result = run_semantic_checks(domain, problem)
        # Should parse correctly despite comments
        assert result["checks"]["predicate_coverage"]["passed"]

    def test_case_insensitive(self):
        """Predicates should match case-insensitively."""
        domain = """
        (define (domain test)
          (:predicates (OnTable ?x))
          (:action move
            :parameters (?x)
            :precondition ()
            :effect (ONTABLE ?x)))
        """
        problem = """
        (define (problem test-p)
          (:domain test)
          (:objects a)
          (:init (ontable a))
          (:goal (OnTable a)))
        """
        result = check_predicate_coverage(domain, problem)
        # Goal should be achievable since predicates match case-insensitively
        assert result["passed"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
