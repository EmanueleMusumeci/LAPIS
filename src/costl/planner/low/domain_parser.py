"""
PDDL Domain Parser - Generic domain constraint extraction
Supports PDDL 1.2: hierarchical typing, derived predicates, quantifiers
"""

import re
from typing import Dict, List, Tuple, Set
import logging

logger = logging.getLogger(__name__)


def extract_domain_constraints(domain_pddl: str) -> Dict:
    """
    Extract ALL structural constraints from domain using PDDL-compliant parser.
    Works for PDDL 1.2 including hierarchical typing, derived predicates, quantifiers.
    
    Args:
        domain_pddl: String containing PDDL domain definition
        
    Returns:
        {
            'name': str,
            'predicates': [(name, arity, param_types)],
            'types': {type_name: parent_type},
            'requirements': [':strips', ':typing', ...],
            'constants': [const_name],
            'derived_predicates': [name]
        }
    """
    constraints = {
        'name': '',
        'predicates': [],
        'types': {},
        'requirements': [],
        'constants': [],
        'derived_predicates': []
    }
    
    # Extract domain name
    name_match = re.search(r'\(define\s+\(domain\s+([a-zA-Z0-9\-_]+)\)', domain_pddl)
    if name_match:
        constraints['name'] = name_match.group(1)
    
    # Extract requirements (always present in well-formed PDDL)
    req_match = re.search(r':requirements\s+(.*?)\)', domain_pddl, re.DOTALL)
    if req_match:
        constraints['requirements'] = req_match.group(1).split()
    
    # Extract types (support hierarchical: block - movable, movable - object)
    types_match = re.search(r':types\s+(.*?)\)', domain_pddl, re.DOTALL)
    if types_match:
        type_text = types_match.group(1).strip()
        # Parse hierarchical types: "a b c - parent_type"
        for line in type_text.split('\n'):
            line = line.strip()
            if '-' in line:
                parts = line.split('-')
                if len(parts) == 2:
                    children_str, parent = parts
                    parent = parent.strip()
                    for child in children_str.split():
                        child = child.strip()
                        if child:
                            constraints['types'][child] = parent
            else:
                # No parent specified, assume 'object'
                for t in line.split():
                    t = t.strip()
                    if t and t != '-':
                        constraints['types'][t] = 'object'
    
    # Extract predicates with arity and parameter types
    pred_block = re.search(
        r':predicates\s+(.*?)(?:\n\s*\)\s*\n\s*\(:action|\n\s*\)\s*\n\s*\(:derived|\n\s*\)\s*\Z)',
        domain_pddl,
        re.DOTALL
    )
    if pred_block:
        predicate_text = pred_block.group(1)
        # Match: (predicate-name ?param1 - type1 ?param2 - type2)
        for pred_match in re.finditer(r'\(([a-zA-Z0-9\-_]+)(.*?)\)', predicate_text, re.DOTALL):
            pred_name = pred_match.group(1)
            params_text = pred_match.group(2)
            
            # Extract parameter types
            param_types = []
            # Match patterns: ?var - type
            for param in re.finditer(r'\?[a-zA-Z0-9_]+ - ([a-zA-Z0-9\-_]+)', params_text):
                param_types.append(param.group(1))
            
            arity = len(param_types)
            constraints['predicates'].append((pred_name, arity, tuple(param_types)))
    
    # Extract derived predicates (if :derived-predicates requirement)
    if ':derived-predicates' in constraints['requirements']:
        # Match all :derived blocks
        for derived_match in re.finditer(r':derived\s+\(([a-zA-Z0-9\-_]+)', domain_pddl):
            derived_name = derived_match.group(1)
            constraints['derived_predicates'].append(derived_name)
    
    # Extract constants
    const_match = re.search(r':constants\s+(.*?)\)', domain_pddl, re.DOTALL)
    if const_match:
        constants_text = const_match.group(1)
        # Handle typed constants: const1 const2 - type
        current_consts = []
        for token in constants_text.split():
            if token == '-':
                continue  # Skip type separator
            elif token in constraints['types'].values():
                continue  # Skip type names
            else:
                constraints['constants'].append(token)
    
    logger.debug(f"Extracted constraints from domain '{constraints['name']}':")
    logger.debug(f"  Predicates: {len(constraints['predicates'])}")
    logger.debug(f"  Types: {len(constraints['types'])}")
    logger.debug(f"  Requirements: {constraints['requirements']}")
    
    return constraints


def format_predicate_guide(constraints: Dict) -> str:
    """
    Generate human-readable predicate usage guide.
    
    Returns formatted string showing available predicates with parameter types.
    """
    guide = "Available Predicates (use EXACTLY as shown):\n"
    
    for pred_name, arity, param_types in constraints['predicates']:
        if arity == 0:
            guide += f"  ({pred_name})\n"
        else:
            param_example = ' '.join([
                f'?{chr(97+i)} - {param_types[i]}' 
                for i in range(min(arity, len(param_types)))
            ])
            guide += f"  ({pred_name} {param_example})\n"
    
    return guide


def format_type_hierarchy(constraints: Dict) -> str:
    """
    Generate human-readable type hierarchy guide.
    
    Returns formatted string showing type inheritance.
    """
    if not constraints['types']:
        return "Type Hierarchy: (none defined)\n"
    
    guide = "Type Hierarchy:\n"
    for child, parent in sorted(constraints['types'].items()):
        guide += f"  {child} - {parent}\n"
    
    return guide


def validate_predicate_usage(
    pddl: str,
    constraints: Dict
) -> Tuple[bool, List[str]]:
    """
    Validate that all predicates used in PDDL match domain constraints.
    
    Args:
        pddl: PDDL problem/domain content to validate
        constraints: Domain constraints from extract_domain_constraints()
        
    Returns:
        (is_valid, error_messages)
    """
    errors = []
    valid_predicate_names = {p[0] for p in constraints['predicates']}
    
    # Extract all predicate uses
    used_predicates = set()
    for match in re.finditer(r'\(([a-zA-Z0-9\-_]+)\s', pddl):
        pred = match.group(1)
        # Filter out PDDL keywords
        if pred not in [
            'define', 'domain', 'problem', 'objects', 'init', 'goal',
            'and', 'or', 'not', 'exists', 'forall', 'when', 'imply'
        ]:
            used_predicates.add(pred)
    
    # Check each used predicate
    for pred in used_predicates:
        if pred not in valid_predicate_names:
            # Find similar valid predicates (typo detection)
            from difflib import SequenceMatcher
            similar = []
            for valid_pred in valid_predicate_names:
                similarity = SequenceMatcher(None, pred, valid_pred).ratio()
                if similarity > 0.6:
                    similar.append((valid_pred, similarity))
            
            if similar:
                similar.sort(key=lambda x: x[1], reverse=True)
                suggestion = similar[0][0]
                errors.append(
                    f"Invalid predicate '{pred}'. Did you mean '{suggestion}'?"
                )
            else:
                errors.append(
                    f"Invalid predicate '{pred}' (not defined in domain)"
                )
    
    return len(errors) == 0, errors
