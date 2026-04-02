# trace_check.py
# Formal LTL checker for PDDL traces
# Uses the LTL parser and evaluator from the parent directory

import re
from functools import lru_cache

# ------------------ Lexer ------------------
token_spec = [
    ("SKIP", r"[ \t\n]+"),
    ("ARROW", r"->|→"),
    ("AND", r"&|∧"),
    ("OR", r"\||∨"),
    ("NOT", r"!|¬"),
    ("U", r"U"),
    ("R", r"R"),
    ("G", r"G"),
    ("F", r"F"),
    ("X", r"X"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    # Updated ATOM to match both predicate format AND natural language phrases
    # Natural language can contain spaces, commas, underscores, letters, numbers
    ("ATOM", r"[a-zA-Z_][a-zA-Z0-9_\-]*(?: [a-zA-Z0-9_\-]+)*(?:\([a-zA-Z0-9_, \-]*\))?"),
]

tok_regex = "|".join("(?P<%s>%s)" % pair for pair in token_spec)

def tokenize(s):
    for mo in re.finditer(tok_regex, s):
        kind = mo.lastgroup
        if kind == "SKIP":
            continue
        yield kind, mo.group(0)
    yield "EOF", ""

# ------------------ Parser (recursive descent) ------------------
# ------------------ Parser (recursive descent) ------------------
# [COMMMENTED OUT - REPLACED BY ltl_verifier SUBMODULE]
# class Parser:
# ...

# ------------------ Evaluator with diagnostics ------------------
# [COMMMENTED OUT - REPLACED BY ltl_verifier SUBMODULE]
# def make_evaluator(trace):
# ...

# ------------------ Main checking function ------------------
def normalize_formula_syntax(formula_str):
    """
    Normalize LTL formula syntax to use parser-compatible operators.
    Converts:
      - not(X) -> !(X)
      - NOT(X) -> !(X)
    This ensures formulas from different sources are parsed correctly.
    """
    import re
    # Replace 'not(' with '!(' (case insensitive)
    normalized = re.sub(r'\bnot\s*\(', '!(', formula_str, flags=re.IGNORECASE)
    return normalized

# def parse_formula(s):
#     # Normalize syntax before parsing
#     s = normalize_formula_syntax(s)
#     p = Parser(s)
#     return p.parse()
# 
# def normalize_ast(node):
# ...

def infer_negative_fluents(state):
    """
    Infer negative fluents from positive fluents in a state.
    For example, if 'X_is_on_the_table' is NOT in state, then 'X_is_not_on_the_table' is true.
    This allows formulas to reference negative fluents even though traces only contain positive ones.
    """
    expanded_state = set(state)  # Start with original positive fluents
    
    # Extract all block names from the state
    blocks = set()
    for fluent in state:
        # Extract block names from common patterns
        if '_is_on_the_table' in fluent:
            block = fluent.replace('_is_on_the_table', '')
            blocks.add(block)
        elif '_is_on_top_of_' in fluent:
            parts = fluent.split('_is_on_top_of_')
            blocks.add(parts[0])
            if len(parts) > 1:
                blocks.add(parts[1])
        elif 'you_are_holding_' in fluent:
            block = fluent.replace('you_are_holding_', '')
            blocks.add(block)
        elif '_is_clear' in fluent:
            block = fluent.replace('_is_clear', '')
            blocks.add(block)
    
    # For each block, infer negative fluents
    for block in blocks:
        # If "X is on the table" is NOT present, add "X is not on the table"
        if f'{block}_is_on_the_table' not in state:
            expanded_state.add(f'{block}_is_not_on_the_table')
        
        # If "X is clear" is NOT present, could add "X is not clear" but this is less common
        # We'll keep it simple for now
    
    # Handle "you are holding" vs "you are not holding any block"
    has_holding = any('you_are_holding_' in f for f in state)
    if not has_holding and 'you_are_not_holding_any_block' not in state:
        expanded_state.add('you_are_not_holding_any_block')
    
    return expanded_state

def normalize_predicate(pred):
    """
    Normalize predicate format for consistent comparison.
    Converts spaces, parentheses, and commas to underscores.
    Example: "holding(brown_block_2)" -> "holding_brown_block_2"
    """
    pred = pred.strip()
    
    # Replace spaces, parentheses, and commas with underscores
    pred = re.sub(r'[\s\(\),]+', '_', pred)
    
    # Remove trailing/leading underscores and double underscores
    pred = re.sub(r'_+', '_', pred).strip('_')
    
    return pred

def trace_check(trace, formula_str, constraint_evaluation_mode="spot"):
    """
    Check if a trace satisfies an LTL formula using formal methods (via ltl_verifier submodule).
    
    Args:
        trace: List of sets, where each set contains predicates (strings)
        formula_str: LTL formula as a string
        constraint_evaluation_mode: "spot" or "up" configuring the mathematical backend.
        
    Returns:
        tuple: (is_satisfied: bool, details: dict)
    """
    import os
    import sys
    
    # Ensure LTL_Verifier submodule is in the Python Path so we can use it as a library
    # Submodule registered at: third-party/LTL_Verifier (see .gitmodules)
    current_dir = os.path.abspath(os.path.dirname(__file__))
    # Trace back to LAPIS/ (6 levels up from src/lapis/planner/high/Planner/)
    # Or just find the root dynamically
    lapis_root = current_dir
    while os.path.basename(lapis_root) != "LAPIS" and lapis_root != "/":
        lapis_root = os.path.dirname(lapis_root)
        
    verifier_path = os.path.join(lapis_root, "third-party", "LTL_Verifier")
    
    # Fallback/Development path
    if not os.path.isdir(verifier_path):
        verifier_path = "/DATA/LTL_Verifier"
    
    if verifier_path not in sys.path:
        sys.path.insert(0, verifier_path)
        
    try:
        from ltl_verifier import evaluate_trace
    except ImportError as e:
        return False, {"error": f"Failed to import ltl_verifier ({e}). Searched: {verifier_path}", "message": "Failed to run LTL verification."}

    # Normalize the trace and expand with inferred negative fluents (useful for standard formulas)
    normalized_trace = []
    for state in trace:
        if isinstance(state, str):
            normalized_state = {normalize_predicate(state)}
        else:
            normalized_state = {normalize_predicate(p) for p in state}
        
        # Expand state with inferred negative fluents
        expanded_state = infer_negative_fluents(normalized_state)
        normalized_trace.append(expanded_state)
    
    # Normalize the formula atoms for the external evaluators
    # This prevents syntax errors with parentheses (e.g., Spot parser)
    atom_regex = r'[a-zA-Z_][a-zA-Z0-9_\-]*(?:\([a-zA-Z0-9_, \-]*\))?'
    def atom_replace(match):
        atom_full = match.group(0)
        # Skip LTL operators
        if atom_full in ('F', 'G', 'X', 'U', 'R'): return atom_full
        return normalize_predicate(atom_full)
    
    normalized_formula = re.sub(atom_regex, atom_replace, formula_str)
    # Also normalize formula syntax (F, G, !, etc.)
    normalized_formula = normalize_formula_syntax(normalized_formula)
    
    # Delegate to the standalone module
    try:
        result, details = evaluate_trace(normalized_trace, normalized_formula, mode=constraint_evaluation_mode)
    except Exception as e:
         return False, {"error": str(e), "message": "Exception during LTL verification."}
    
    # Add trace summary for better understanding
    trace_summary = "TRACE SUMMARY (what actually happened in your plan):\n"
    for i, state in enumerate(normalized_trace):
        trace_summary += f"  State {i}: {len(state)} fluents\n"
        # Show ALL fluents
        for fluent in sorted(state):
            trace_summary += f"    • {fluent}\n"
    details["trace_summary"] = trace_summary
    
    if result:
        if "message" not in details:
            details["message"] = "✓ The trace SATISFIES the LTL formula"
    else:
        if "message" not in details:
            details["message"] = "✗ The trace VIOLATES the LTL formula"
        
        # The details dict is returned by evaluate_trace; populate fallback fields if missing
        if "violation_report" not in details:
            details["violation_report"] = details.get("error", "No detailed violation report available.")
        if "plain_english_explanation" not in details:
            details["plain_english_explanation"] = details.get("message", "The trace violates the formula.")
    
    return result, details

def suggest_actions_for_fluent(fluent, trace):
    """Suggest specific actions that could create a fluent based on pattern analysis"""
    suggestions = []
    
    # Parse the fluent to understand what it requires
    if "_is_not_on_the_table" in fluent:
        block = fluent.split("_is_not_on_the_table")[0]
        suggestions.append(f"pickup {block}")
        suggestions.append(f"stack {block} <target_block>")
    elif "_is_on_the_table" in fluent:
        block = fluent.split("_is_on_the_table")[0]
        suggestions.append(f"putdown {block}")
    elif "you_are_holding_" in fluent:
        block = fluent.replace("you_are_holding_", "")
        suggestions.append(f"pickup {block}")
        suggestions.append(f"unstack {block} <other_block>")
    elif "_is_on_top_of_" in fluent:
        parts = fluent.split("_is_on_top_of_")
        if len(parts) == 2:
            block1, block2 = parts
            suggestions.append(f"stack {block1} {block2}")
    elif "_is_clear" in fluent:
        block = fluent.replace("_is_clear", "")
        suggestions.append(f"unstack <block_on_top> {block}")
        suggestions.append(f"pickup <block_on_top> (if {block} is on table)")
    elif "you_are_not_holding_any_block" in fluent:
        suggestions.append("putdown <held_block>")
        suggestions.append("stack <held_block> <target_block>")
    
    return suggestions

def find_action_that_removed_fluent(fluent, trace, violation_state):
    """Identify which action likely removed a fluent by analyzing state transitions"""
    if violation_state == 0:
        return "The fluent was not present in the initial state"
    
    prev_state = trace[violation_state - 1]
    curr_state = trace[violation_state]
    
    # Check if fluent was present before and absent now
    if fluent in prev_state and fluent not in curr_state:
        # Try to infer the action based on state changes
        if "you_are_holding_" in fluent:
            # Holding was removed - likely putdown or stack
            return "Action between states likely: 'putdown' or 'stack' (these release the held block)"
        elif "_is_on_the_table" in fluent:
            # Block removed from table - likely pickup
            block = fluent.split("_is_on_the_table")[0]
            return f"Action between states likely: 'pickup {block}' or 'stack {block} <other_block>'"
        elif "_is_clear" in fluent:
            # Block no longer clear - something was placed on it
            block = fluent.replace("_is_clear", "")
            return f"Action between states likely: 'stack <some_block> {block}'"
    
    return "Check the action that transitions from the previous state to this state"

def is_simple_predicate(s):
    """Check if a string is a simple predicate (no operators)"""
    return not any(op in s for op in ["→", "&", "|", "F(", "G(", "X(", "U", "R", "!"])

def format_formula(node):
    """Pretty print a formula AST node"""
    if isinstance(node, tuple):
        kind = node[0]
        if kind == "atom":
            return node[1]
        elif kind in ("G", "F", "X", "not"):
            return f"{kind}({format_formula(node[1])})"
        elif kind in ("and", "or", "imp", "U", "R"):
            op_map = {"and": "&", "or": "|", "imp": "→", "U": "U", "R": "R"}
            return f"({format_formula(node[1])} {op_map[kind]} {format_formula(node[2])})"
    return str(node)

def print_trace_check_result(result, details):
    """Pretty print the trace checking result"""
    print("\n" + "=" * 80)
    print("LTL TRACE CHECK RESULT (FORMAL VERIFICATION)")
    print("=" * 80)
    print(f"Formula: {details.get('formula', 'Unknown LTL Formula')}")
    print(f"Trace length: {details.get('trace_length', 'N/A')} states")
    print("-" * 80)
    print(details.get('message', 'No message available'))
    
    if not result:
        print("\nVIOLATIONS DETECTED (Technical):")
        print(details.get('violation_report', 'No detailed report available'))
        
        print("\n" + "-" * 80)
        print("EXPLANATION IN PLAIN ENGLISH:")
        print("-" * 80)
        print(details.get('plain_english_explanation', 'No explanation available'))
        
        explanation = '\nVIOLATIONS DETECTED:\n'
        explanation += (details.get('violation_report', 'No detailed report available'))+'\n'
        explanation += "\n" + "-" * 80 + "\n"

        nl_explaination = "NATURAL LANGUAGE EXPLANATION:\n"
        nl_explaination += details.get('plain_english_explanation', 'No explanation available') + "\n"
        nl_explaination += "\n" + "-" * 80 + "\n"
        
        # Add trace summary to help understand what actually happened
        if 'trace_summary' in details:
            nl_explaination += "\n" + details['trace_summary'] + "\n"
            nl_explaination += "\n" + "-" * 80 + "\n"
        
        nl_explaination += "The plan does NOT satisfy the constraints specified in the problem file. "
        nl_explaination += "You need to generate a different plan that respects the LTL formula."
    else:
        explanation = '\nThe plan successfully satisfies all constraints!'
        nl_explaination = explanation
    
    print("\n" + "=" * 80 + "\n")
    return explanation, nl_explaination

# ------------------ Example usage ------------------
if __name__ == "__main__":
    # Example trace with PDDL predicates
    trace = [
        {"ontable(a)", "ontable(b)", "clear(a)", "clear(b)", "handempty"},
        {"ontable(b)", "clear(b)", "holding(a)"},
        {"ontable(b)", "on(a,b)", "clear(a)", "handempty"}
    ]
    
    # Example formula: eventually a is on b
    formula = "F(on(a,b))"
    
    result, details = trace_check(trace, formula)
    print_trace_check_result(result, details)
