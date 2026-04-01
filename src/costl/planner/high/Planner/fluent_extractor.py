"""
Extract all fluents from an LTL formula to ensure they are tracked in the trace.
"""

import re
from typing import Set


def extract_fluents_from_ltl(ltl_formula: str) -> Set[str]:
    """
    Extract all unique fluent predicates from an LTL formula.
    
    Args:
        ltl_formula: LTL formula string (e.g., "F(on(X,Y)) & G(holding(Z))")
    
    Returns:
        Set of fluent names (e.g., {"on", "holding", "clear", "exists_on_top"})
    
    Examples:
        "F(on_table(first_black))" -> {"on_table"}
        "F(holding(X) & !on_table(Y))" -> {"holding", "on_table"}
        "F(exists_on_top(purple))" -> {"exists_on_top"}
    """
    fluents = set()
    
    # Remove temporal operators (F, G, U, X, etc.) and logical operators
    # Pattern: find predicates of form predicate_name(args)
    
    # First, remove temporal operators and parentheses around them
    cleaned = ltl_formula
    cleaned = re.sub(r'\b[FGUXfgux]\s*\(', '(', cleaned)  # Remove temporal ops before (
    
    # Pattern to match predicate(args) - captures predicate name
    # Matches: word_characters followed by (
    pattern = r'(\w+)\s*\('
    
    matches = re.findall(pattern, cleaned)
    
    for match in matches:
        # Filter out logical operators and temporal operators
        if match.lower() not in ['f', 'g', 'u', 'x', 'and', 'or', 'not', 'implies']:
            fluents.add(match)
    
    # Also check for simple predicates without parentheses (less common but possible)
    # Pattern: standalone words that aren't operators
    simple_pattern = r'\b([a-z_][a-z0-9_]*)\b'
    simple_matches = re.findall(simple_pattern, cleaned.lower())
    
    operators = {'f', 'g', 'u', 'x', 'and', 'or', 'not', 'implies', 'true', 'false'}
    for match in simple_matches:
        if match not in operators and '(' not in match:
            # This might be a simple fluent (no args)
            # We'll be conservative and only add if it looks like a fluent
            if '_' in match or match in ['clear', 'holding', 'empty']:
                fluents.add(match)
    
    return fluents


def get_fluent_pattern_examples(ltl_formula: str) -> dict:
    """
    Extract example fluent instances from the formula.
    
    Returns a dict mapping fluent names to example instances.
    Example: {"on": ["on(purple, red)", "on(X, Y)"], "holding": ["holding(first_black)"]}
    """
    fluent_examples = {}
    
    # Pattern to match full predicate with arguments
    pattern = r'(\w+)\s*\(([^)]+)\)'
    
    matches = re.findall(pattern, ltl_formula)
    
    for predicate, args in matches:
        if predicate.lower() not in ['f', 'g', 'u', 'x', 'and', 'or', 'not', 'implies']:
            full_fluent = f"{predicate}({args})"
            if predicate not in fluent_examples:
                fluent_examples[predicate] = []
            if full_fluent not in fluent_examples[predicate]:
                fluent_examples[predicate].append(full_fluent)
    
    return fluent_examples


def verify_trace_completeness(trace: list, ltl_formula: str) -> dict:
    """
    Verify that a trace includes all necessary fluents from the LTL formula.
    
    Args:
        trace: List of states, where each state is a list of fluent strings
        ltl_formula: The LTL formula
    
    Returns:
        Dict with 'missing_fluents' (fluents in formula but never in trace)
        and 'fluents_found' (fluents that appear at least once)
    """
    required_fluents = extract_fluents_from_ltl(ltl_formula)
    
    # Check which fluents appear in the trace
    fluents_in_trace = set()
    for state in trace:
        for fluent_str in state:
            # Extract predicate name from fluent string
            match = re.match(r'(\w+)\s*\(', fluent_str)
            if match:
                fluents_in_trace.add(match.group(1))
            else:
                # Simple fluent without args
                fluents_in_trace.add(fluent_str.strip())
    
    missing = required_fluents - fluents_in_trace
    found = required_fluents & fluents_in_trace
    
    return {
        'required_fluents': required_fluents,
        'fluents_found': found,
        'missing_fluents': missing,
        'completeness_ratio': len(found) / len(required_fluents) if required_fluents else 1.0
    }


if __name__ == "__main__":
    # Test the extractor
    test_formulas = [
        "F(on_table(first_black)) & F(holding(first_green) & !on_table(purple))",
        "F(on(second_yellow, purple)) & F(exists_on_top(purple)) & G(exists_on_top(purple) -> F(holding(red)))",
        "F(on_white_brown) & F(on_grey_white) & F(on_white_table)"
    ]
    
    for formula in test_formulas:
        print(f"\nFormula: {formula}")
        fluents = extract_fluents_from_ltl(formula)
        print(f"Extracted fluents: {fluents}")
        examples = get_fluent_pattern_examples(formula)
        print(f"Examples: {examples}")
