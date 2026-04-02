# Copied from ContextMatters (repository link (https://github.com/Lab-RoCoCo-Sapienza/context-matters))
import os

# Add third-party/symk_wrapper to path if not present
import sys
symk_wrapper_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))), "third-party", "symk_wrapper")
if symk_wrapper_path not in sys.path:
    sys.path.append(symk_wrapper_path)
    
try:
    from symk_wrapper.symk import SymK
except ImportError:
    print(f"Warning: Could not import SymK from {symk_wrapper_path}")
    SymK = None

import traceback
import unified_planning as up
from unified_planning.shortcuts import OneshotPlanner
from unified_planning.io import PDDLReader

import re

def _preprocess_pddl(pddl_str):
    """
    Last-resort cleanup of non-standard PDDL constructs that break the UP parser.
    
    UP does not support `(either type1 type2)` union types anywhere.
    If the LLM still generates them despite prompt instructions, we replace
    with the first listed type as a safe fallback.
    
    NOTE: We do NOT strip `?var - type` from :parameters as that breaks PDDL.
    """
    def replace_either(m):
        inner = m.group(1)
        first_type = inner.strip().split()[0]
        return f'- {first_type}'
    pddl_str = re.sub(r'-\s*\(\s*either\s+([^)]+)\)', replace_either, pddl_str)
    
    # Strip (:objects ...) from domain files if the LLM hallucinated it
    if '(define (domain' in pddl_str:
        pddl_str = re.sub(r'\(\s*:objects[^)]+\)', '', pddl_str, flags=re.IGNORECASE)
        
    return pddl_str



def run_planner_UP(domain_file_path, problem_dir, planner_name="up_fd", timeout=180):
    """
    Robust planning using Unified Planning (UP).
    Handles non-standard PDDL and provides clear error logs.
    """
    try:
        reader = PDDLReader()
        problem_file_path = os.path.join(problem_dir, "problem.pddl")
        
        # Parse PDDL using UP's robust reader
        # Preprocess both domain and problem to remove problematic '(either ...)' syntax
        with open(domain_file_path, 'r') as f:
            domain_str = f.read()
        with open(problem_file_path, 'r') as f:
            problem_str = f.read()
            
        domain_str = _preprocess_pddl(domain_str)
        problem_str = _preprocess_pddl(problem_str)
        
        # Log preprocessed versions for debugging if reader fails
        try:
            problem = reader.parse_problem_string(domain_str, problem_str)
        except Exception as parse_e:
            print(f"DEBUG: PDDL PREPROCESS FAILED. Domain snippet:\n{domain_str[:500]}")
            print(f"DEBUG: Problem snippet:\n{problem_str[:500]}")
            raise parse_e
        
        # Use specifying planner if provided (e.g. 'up_fast_downward')
        # Map common names to UP names
        up_planner_name = "fast-downward" if "fd" in planner_name.lower() else "pyperplan"
        
        with OneshotPlanner(name=up_planner_name) as planner:
            result = planner.solve(problem)
            
            from unified_planning.engines import PlanGenerationResultStatus
            if result.status in [PlanGenerationResultStatus.SOLVED_SATISFICING, PlanGenerationResultStatus.SOLVED_OPTIMALLY]:
                # Convert UP plan to string representation for compatibility with pipeline logic
                # The pipeline expects a list of actions as strings
                plan = [str(action) for action in result.plan.actions]
                return plan, None, None, None
            else:
                return None, None, f"UP Planner failed with status: {result.status}", None
                
    except Exception as e:
        error_msg = f"Exception in UP parsing/planning: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return None, error_msg, None, None


def plan_with_output(domain_file_path, problem_dir, plan_file_path, env=None, planner_name="fd", search_flag=None, timeout=180):

    # PLANNING #
    
    print("\n\n\tPerforming planning...")
    print(domain_file_path)
    print(os.path.join(problem_dir, "problem.pddl"))
    
    if planner_name.lower().startswith("up") or planner_name.lower() in ["fd", "symk", "pyperplan"]:
        # Use Unified Planning for everything now as requested
        plan, pddlenv_error_log, planner_error_log, statistics = run_planner_UP(domain_file_path, problem_dir, planner_name, timeout)

    # Save planner output
    with open(plan_file_path, "w") as file:
        if plan is not None:    
            if isinstance(plan, list):
                file.write("\n".join(plan) + "\n")
            else:
                file.write(str(plan) + "\n")
        elif pddlenv_error_log is not None:
            file.write(pddlenv_error_log)
        elif planner_error_log is not None:
            file.write(planner_error_log)

    return plan, pddlenv_error_log, planner_error_log, statistics