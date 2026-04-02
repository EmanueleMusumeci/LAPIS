import os
import sys
import argparse
from pathlib import Path
import json
import copy

#from lapis.planner.high.Planner.trace_generator import trace_generation

# Add workspace root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent.parent))

from openai import OpenAI
from formula_generator import ltl_formula_generation, FormulaGenerationAgent
from constraint_order_selector import constraint_order_selection, ConstraintOrderSelector
from plan_generator import plan_generation, PlanGenerationAgent
from constraint_analyzer import constraint_analysis, ConstraintAnalyzerAgent
from contraint_trace_check import constraint_check, ConstraintCheckSelector
from trace_generator import trace_generation, TraceGenerationAgent

#from trace_generator import trace_generation, init_trace
#from trace_check import trace_check, print_trace_check_result
from nl_description_generator import nl_description_generation, NLDescriptionAgent
#from feedback_translator import translate_feedback_to_natural_language
#from results_utils import save_plan_to_file, append_result_to_summary, append_to_csv_log, append_to_excel_log
from dotenv import load_dotenv
from src.lapis.agents.gpt import GPTAgent

load_dotenv()  # loads variables from .env into environment


def update_global_summary(domain_path):
    """
    Update the global summary across all constraint levels for a domain.
    Includes violated constraints aggregation with types and suggestions.
    This generates FINAL_SUMMARY.md with ALL constraint levels.
    """
    try:
        import re
        # Save as FINAL_SUMMARY.md (main report with ALL constraints)
        final_summary_path = domain_path / 'FINAL_SUMMARY.md'
        # Also keep a copy as GLOBAL_SUMMARY.md for backwards compatibility
        global_summary_path = domain_path / 'GLOBAL_SUMMARY.md'
        
        # Collect results from all data_* folders
        all_results = {}
        all_violated_constraints = {"Normal": [], "Conditional": [], "Global": []}
        
        data_folders = sorted([d for d in domain_path.iterdir() if d.is_dir() and d.name.startswith('data_')],
                             key=lambda x: int(x.name.split('_')[1]) if x.name.split('_')[1].isdigit() else 0)
        
        for data_folder in data_folders:
            constraints_num = data_folder.name.replace('data_', '')
            
            # Try to load results from problem folders
            results = []
            problem_folders = sorted([d for d in data_folder.iterdir() if d.is_dir() and d.name.isdigit()],
                                   key=lambda x: int(x.name))
            
            for problem_folder in problem_folders:
                problem_id = problem_folder.name
                md_file = problem_folder / f"{problem_id}_detailed_report.md"
                
                if md_file.exists():
                    # Extract info from the detailed report
                    try:
                        with open(md_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            success = '✓ SUCCESS' in content.split('**Status**:')[1].split('\n')[0] if '**Status**:' in content else False
                            
                            # Extract attempts
                            attempts_match = re.search(r'\*\*Attempts\*\*: (\d+)', content)
                            attempts = int(attempts_match.group(1)) if attempts_match else 0
                            
                            # Extract unsatisfied constraints with types
                            unsatisfied_constraints = []
                            
                            # Parse constraint verification section
                            if '## Constraint Verification' in content:
                                verification_section = content.split('## Constraint Verification')[1].split('## Summary')[0]
                                constraint_blocks = verification_section.split('### ✗')
                                
                                for block in constraint_blocks[1:]:  # Skip first empty element
                                    try:
                                        # Extract constraint text
                                        constraint_match = re.search(r'\*\*Constraint:\*\* (.+?)(?:\n\n|\*\*)', block, re.DOTALL)
                                        if constraint_match:
                                            constraint_text = constraint_match.group(1).strip()
                                            
                                            # Determine type
                                            if constraint_text.startswith("True in at least one state:"):
                                                constraint_type = "Normal"
                                            elif constraint_text.startswith("Conditional constraint:"):
                                                constraint_type = "Conditional"
                                            elif constraint_text.startswith("True in every state:"):
                                                constraint_type = "Global"
                                            else:
                                                constraint_type = "Unknown"
                                            
                                            # Extract reasoning and solution
                                            reasoning_match = re.search(r'\*\*Reasoning:\*\*\n```\n(.+?)\n```', block, re.DOTALL)
                                            reasoning = reasoning_match.group(1).strip() if reasoning_match else "N/A"
                                            
                                            solve_match = re.search(r'\*\*How to Solve:\*\*\n```\n(.+?)\n```', block, re.DOTALL)
                                            how_to_solve = solve_match.group(1).strip() if solve_match else "N/A"
                                            
                                            unsatisfied_constraints.append({
                                                'constraint': constraint_text,
                                                'type': constraint_type,
                                                'reasoning': reasoning,
                                                'how_to_solve': how_to_solve
                                            })
                                            
                                            # Add to global violated constraints tracker
                                            all_violated_constraints[constraint_type].append({
                                                'constraint': constraint_text,
                                                'problem_id': f"{constraints_num}_{problem_id}",
                                                'reasoning': reasoning,
                                                'how_to_solve': how_to_solve
                                            })
                                    except Exception as parse_err:
                                        print(f"Error parsing constraint block: {parse_err}")
                            
                            results.append({
                                'problem_id': problem_id,
                                'success': success,
                                'attempts': attempts,
                                'unsatisfied_constraints': unsatisfied_constraints
                            })
                    except Exception as e:
                        print(f"Warning: Error parsing {md_file}: {e}")
            
            if results:
                all_results[constraints_num] = results
        
        if not all_results:
            return
        
        # Generate global summary
        md_lines = []
        md_lines.append(f"# Final Summary Report - {domain_path.name.title()}\n\n")
        md_lines.append(f"## Complete Results Across ALL Constraint Levels\n\n")
        md_lines.append(f"**Domain**: {domain_path.name}\n")
        md_lines.append(f"**Total Constraint Levels Processed**: {len(all_results)}\n")
        md_lines.append(f"**Constraint Levels**: {', '.join(sorted(all_results.keys(), key=lambda x: int(x) if x.isdigit() else 0))}\n\n")
        md_lines.append("---\n\n")
        
        # Overall statistics across all constraint levels
        md_lines.append("## Overall Statistics Across All Constraint Levels\n\n")
        md_lines.append("| Constraint Level | Total Problems | Successful | Failed | Success Rate | Avg Attempts |\n")
        md_lines.append("|------------------|----------------|------------|--------|--------------|--------------|\n")
        
        total_problems_all = 0
        total_successful_all = 0
        
        for constraints_num in sorted(all_results.keys(), key=lambda x: int(x) if x.isdigit() else 0):
            results = all_results[constraints_num]
            total = len(results)
            successful = sum(1 for r in results if r.get('success', False))
            failed = total - successful
            success_rate = (successful / total * 100) if total > 0 else 0
            
            successful_attempts = [r.get('attempts', 0) for r in results if r.get('success', False) and r.get('attempts')]
            avg_attempts = sum(successful_attempts) / len(successful_attempts) if successful_attempts else 0
            
            md_lines.append(f"| {constraints_num} constraint{'s' if int(constraints_num) > 1 else ''} | {total} | {successful} | {failed} | {success_rate:.1f}% | {avg_attempts:.2f} |\n")
            
            total_problems_all += total
            total_successful_all += successful
        
        overall_success_rate = (total_successful_all / total_problems_all * 100) if total_problems_all > 0 else 0
        md_lines.append(f"| **TOTAL** | **{total_problems_all}** | **{total_successful_all}** | **{total_problems_all - total_successful_all}** | **{overall_success_rate:.1f}%** | - |\n\n")
        
        # Constraint violation statistics by type
        md_lines.append("## Constraint Violation Statistics by Type\n\n")
        total_violations = sum(len(v) for v in all_violated_constraints.values())
        
        if total_violations > 0:
            md_lines.append(f"**Total Violated Constraints**: {total_violations}\n\n")
            md_lines.append("| Constraint Type | Count | Percentage |\n")
            md_lines.append("|-----------------|-------|------------|\n")
            
            for constraint_type in ["Normal", "Conditional", "Global"]:
                count = len(all_violated_constraints.get(constraint_type, []))
                percentage = (count / total_violations * 100) if total_violations > 0 else 0
                md_lines.append(f"| {constraint_type} | {count} | {percentage:.1f}% |\n")
            
            md_lines.append("\n")
        else:
            md_lines.append("*No violated constraints!*\n\n")
        
        # Detailed breakdown by constraint level
        md_lines.append("## Detailed Breakdown by Constraint Level\n\n")
        
        for constraints_num in sorted(all_results.keys(), key=lambda x: int(x) if x.isdigit() else 0):
            results = all_results[constraints_num]
            md_lines.append(f"### {constraints_num} Constraint{'s' if int(constraints_num) > 1 else ''}\n\n")
            
            successful = sum(1 for r in results if r.get('success', False))
            failed = len(results) - successful
            
            md_lines.append(f"- **Total Problems**: {len(results)}\n")
            md_lines.append(f"- **Successful**: {successful} ({successful/len(results)*100:.1f}%)\n")
            md_lines.append(f"- **Failed**: {failed} ({failed/len(results)*100:.1f}%)\n\n")
        
        # Most Common Violated Constraints
        if total_violations > 0:
            md_lines.append("## Most Common Violated Constraints\n\n")
            
            for constraint_type in ["Normal", "Conditional", "Global"]:
                violations = all_violated_constraints.get(constraint_type, [])
                if violations:
                    md_lines.append(f"### {constraint_type} Constraints ({len(violations)} violations)\n\n")
                    
                    # Group by constraint text (first 200 chars to handle variations)
                    constraint_freq = {}
                    for v in violations:
                        c_text = v['constraint']
                        c_key = c_text[:200]  # Use first 200 chars as key
                        if c_key not in constraint_freq:
                            constraint_freq[c_key] = {
                                'full_text': c_text,
                                'count': 0,
                                'problems': [],
                                'reasoning': v['reasoning'],
                                'how_to_solve': v['how_to_solve']
                            }
                        constraint_freq[c_key]['count'] += 1
                        constraint_freq[c_key]['problems'].append(v['problem_id'])
                    
                    # Sort by frequency
                    sorted_constraints = sorted(constraint_freq.items(), key=lambda x: x[1]['count'], reverse=True)
                    
                    for idx, (_, info) in enumerate(sorted_constraints[:5], 1):  # Top 5
                        md_lines.append(f"#### {idx}. Violated in {info['count']} problem(s)\n\n")
                        md_lines.append(f"**Constraint:**\n```\n{info['full_text']}\n```\n\n")
                        md_lines.append(f"**Problems**: {', '.join(info['problems'])}\n\n")
                        md_lines.append(f"**Typical Reasoning:**\n```\n{info['reasoning'][:400]}...\n```\n\n")
                        md_lines.append(f"**How to Solve:**\n```\n{info['how_to_solve'][:400]}...\n```\n\n")
                        md_lines.append("---\n\n")
        
        md_lines.append("\n---\n\n")
        md_lines.append(f"*Report generated for domain: {domain_path.name} - Includes ALL constraint levels*\n")
        
        # Save as FINAL_SUMMARY.md (main comprehensive report)
        with open(final_summary_path, 'w', encoding='utf-8') as f:
            f.writelines(md_lines)
        
        # Also save as GLOBAL_SUMMARY.md for backwards compatibility
        with open(global_summary_path, 'w', encoding='utf-8') as f:
            f.writelines(md_lines)
        
        print(f"Updated comprehensive summary (ALL constraints): {final_summary_path}")
    
    except Exception as e:
        print(f"Warning: couldn't update final summary: {e}")
        import traceback
        traceback.print_exc()


def load_previous_results(data_folder, problem_folders, start_from):
    """
    Load results from previously completed problems by reading existing detailed report files.
    
    Args:
        data_folder: Path to the data_* folder
        problem_folders: List of all problem folders
        start_from: Problem number to start from (problems before this are considered already done)
    
    Returns:
        list: Results loaded from existing files
    """
    import re
    
    results = []
    
    if not start_from:
        # If no start_from specified, don't load previous results
        return results
    
    print(f"\n{'=' * 80}")
    print("LOADING PREVIOUS RESULTS")
    print(f"{'=' * 80}")
    
    for problem_folder in problem_folders:
        problem_id = problem_folder.name
        problem_num = int(problem_id)
        
        # Only load results for problems before start_from
        if problem_num >= start_from:
            continue
        
        # Check if detailed report exists
        md_file = problem_folder / f"{problem_id}_detailed_report.md"
        
        if not md_file.exists():
            print(f"Warning: No report found for Problem {problem_id}, skipping...")
            continue
        
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract status
            success = '✓ SUCCESS' in content.split('**Status**:')[1].split('\n')[0] if '**Status**:' in content else False
            
            # Extract attempts
            attempts_match = re.search(r'\*\*Attempts\*\*: (\d+)', content)
            attempts = int(attempts_match.group(1)) if attempts_match else 0
            
            # Extract unsatisfied constraints
            unsatisfied_constraints = []
            
            if '## Constraint Verification' in content:
                verification_section = content.split('## Constraint Verification')[1].split('## Summary')[0] if '## Summary' in content else content.split('## Constraint Verification')[1]
                constraint_blocks = verification_section.split('### ✗')
                
                for block in constraint_blocks[1:]:  # Skip first empty element
                    try:
                        # Extract constraint text
                        constraint_match = re.search(r'\*\*Constraint:\*\* (.+?)(?:\n\n|\*\*)', block, re.DOTALL)
                        if constraint_match:
                            constraint_text = constraint_match.group(1).strip()
                            
                            # Determine type
                            if constraint_text.startswith("True in at least one state:"):
                                constraint_type = "Normal"
                            elif constraint_text.startswith("Conditional constraint:"):
                                constraint_type = "Conditional"
                            elif constraint_text.startswith("True in every state:"):
                                constraint_type = "Global"
                            else:
                                constraint_type = "Unknown"
                            
                            # Extract reasoning
                            reasoning_match = re.search(r'\*\*Reasoning:\*\*\n```\n(.+?)\n```', block, re.DOTALL)
                            reasoning = reasoning_match.group(1).strip() if reasoning_match else "N/A"
                            
                            # Extract solution
                            solve_match = re.search(r'\*\*How to Solve:\*\*\n```\n(.+?)\n```', block, re.DOTALL)
                            how_to_solve = solve_match.group(1).strip() if solve_match else "N/A"
                            
                            unsatisfied_constraints.append({
                                'type': constraint_type,
                                'constraint': constraint_text,
                                'reasoning': reasoning,
                                'how_to_solve': how_to_solve
                            })
                    except Exception as e:
                        print(f"Warning: Error parsing constraint in Problem {problem_id}: {e}")
                        continue
            
            result = {
                'problem_id': problem_id,
                'success': success,
                'attempts': attempts,
                'unsatisfied_constraints': unsatisfied_constraints,
                'md_path': str(md_file)
            }
            
            results.append(result)
            status_text = "✓ SUCCESS" if success else "✗ FAILED"
            print(f"Loaded Problem {problem_id}: {status_text} - Attempts: {attempts}")
            
        except Exception as e:
            print(f"Error loading result for Problem {problem_id}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"{'=' * 80}")
    print(f"Loaded {len(results)} previous results")
    print(f"{'=' * 80}\n")
    
    return results


def update_final_summary(results, domain_name, num_constraints, abstraction_level, data_folder):
    """
    Update the final summary markdown file with current results.
    """
    try:
        summary_folder = data_folder / 'results'
        summary_folder.mkdir(parents=True, exist_ok=True)
        summary_md_path = summary_folder / 'FINAL_SUMMARY.md'
        
        successful = sum(1 for r in results if r.get('success', False))
        failed = len(results) - successful
        success_rate = (successful / len(results) * 100) if results else 0
        
        # Calculate average attempts for successful problems
        successful_attempts = [r.get('attempts', 0) for r in results if r.get('success', False) and r.get('attempts') is not None]
        avg_attempts = sum(successful_attempts) / len(successful_attempts) if successful_attempts else 0
        max_attempts_used = max(successful_attempts) if successful_attempts else 0
        min_attempts_used = min(successful_attempts) if successful_attempts else 0
        
        md_lines = []
        md_lines.append(f"# Final Summary Report\n\n")
        md_lines.append(f"**Last Updated**: Problem {results[-1]['problem_id']}\n")
        md_lines.append(f"**Domain**: {domain_name}\n")
        md_lines.append(f"**Number of Constraints**: {num_constraints}\n")
        md_lines.append(f"**Abstraction Level**: {abstraction_level}\n\n")
        md_lines.append("---\n\n")
        
        md_lines.append("## Overall Statistics\n\n")
        md_lines.append(f"| Metric | Value |\n")
        md_lines.append(f"|--------|-------|\n")
        md_lines.append(f"| Total Problems Processed | {len(results)} |\n")
        md_lines.append(f"| Successful | {successful} ({success_rate:.1f}%) |\n")
        md_lines.append(f"| Failed | {failed} ({100-success_rate:.1f}%) |\n")
        md_lines.append(f"| Success Rate | {success_rate:.1f}% |\n\n")
        
        md_lines.append("## Attempts Statistics (Successful Problems)\n\n")
        md_lines.append(f"| Statistic | Value |\n")
        md_lines.append(f"|-----------|-------|\n")
        md_lines.append(f"| Average Attempts | {avg_attempts:.2f} |\n")
        md_lines.append(f"| Min Attempts | {min_attempts_used} |\n")
        md_lines.append(f"| Max Attempts | {max_attempts_used} |\n")
        md_lines.append(f"| Total Successful Problems | {len(successful_attempts)} |\n\n")
        
        md_lines.append("## Problem-by-Problem Results\n\n")
        md_lines.append("| Problem ID | Status | Attempts | Unsatisfied | Report |\n")
        md_lines.append("|------------|--------|----------|-------------|--------|\n")
        
        for result in sorted(results, key=lambda x: int(x['problem_id']) if x['problem_id'].isdigit() else 0):
            status_icon = "✓" if result.get('success', False) else "✗"
            status_text = "SUCCESS" if result.get('success', False) else "FAILED"
            attempts = result.get('attempts', 'N/A')
            unsatisfied_count = len(result.get('unsatisfied_constraints', []))
            md_file = result.get('md_path', 'N/A')
            
            # Make the path relative to the summary file
            if md_file != 'N/A':
                md_file_path = Path(md_file)
                try:
                    relative_path = md_file_path.relative_to(summary_folder)
                    md_file_link = f"[View Report](../{relative_path})"
                except:
                    md_file_link = f"[View Report]({md_file})"
            else:
                md_file_link = "N/A"
            
            md_lines.append(f"| {result['problem_id']} | {status_icon} {status_text} | {attempts} | {unsatisfied_count} | {md_file_link} |\n")
        
        md_lines.append("\n## Successful Problems\n\n")
        successful_problems = [r for r in results if r.get('success', False)]
        if successful_problems:
            for result in sorted(successful_problems, key=lambda x: int(x['problem_id']) if x['problem_id'].isdigit() else 0):
                md_lines.append(f"- **Problem {result['problem_id']}**: {result.get('attempts', 'N/A')} attempts\n")
        else:
            md_lines.append("*No successful problems yet*\n")
        
        md_lines.append("\n## Failed Problems\n\n")
        failed_problems = [r for r in results if not r.get('success', False)]
        if failed_problems:
            for result in sorted(failed_problems, key=lambda x: int(x['problem_id']) if x['problem_id'].isdigit() else 0):
                error_msg = f": {result['error']}" if 'error' in result else ""
                md_lines.append(f"- **Problem {result['problem_id']}**: {result.get('attempts', 'N/A')} attempts{error_msg}\n")
        else:
            md_lines.append("*All problems successful so far!*\n")
        
        # Detailed Failed Constraints Section
        md_lines.append("\n## Detailed Failed Constraints\n\n")
        has_failed_constraints = False
        for result in sorted(results, key=lambda x: int(x['problem_id']) if x['problem_id'].isdigit() else 0):
            unsatisfied_constraints = result.get('unsatisfied_constraints', [])
            if unsatisfied_constraints:
                has_failed_constraints = True
                md_lines.append(f"### Problem {result['problem_id']}\n\n")
                md_lines.append(f"**Status**: {'✓ SUCCESS' if result.get('success', False) else '✗ FAILED'}\n")
                md_lines.append(f"**Attempts**: {result.get('attempts', 'N/A')}\n")
                md_lines.append(f"**Unsatisfied Constraints**: {len(unsatisfied_constraints)}\n\n")
                
                for idx, uc in enumerate(unsatisfied_constraints, 1):
                    md_lines.append(f"#### Unsatisfied Constraint {idx}\n\n")
                    md_lines.append(f"**Type**: {uc.get('type', 'Unknown')}\n\n")
                    md_lines.append(f"**Constraint:**\n```\n{uc['constraint']}\n```\n\n")
                    md_lines.append(f"**Reasoning:**\n```\n{uc['reasoning']}\n```\n\n")
                    md_lines.append(f"**How to Solve:**\n```\n{uc['how_to_solve']}\n```\n\n")
                    md_lines.append("---\n\n")
        
        if not has_failed_constraints:
            md_lines.append("*No failed constraints across all problems!*\n\n")
        
        md_lines.append("\n---\n\n")
        md_lines.append(f"*Report generated for domain: {domain_name}, constraints: {num_constraints}, abstraction: {abstraction_level}*\n")
        
        with open(summary_md_path, "w", encoding="utf-8") as f:
            f.writelines(md_lines)
        
        print(f"Updated final summary: {summary_md_path}")
    except Exception as e:
        print(f"Warning: couldn't update final summary markdown: {e}")
        import traceback
        traceback.print_exc()


def process_problem(max_attempts, nl_file_path, problem_id, domain_name, num_constraints, data_folder, abstraction_level):
    """
    Process a single problem instance.
    
    Args:
        nl_file_path: Path to the nl file
        problem_id: ID of the problem (folder name)
        domain_name: Name of the domain
        num_constraints: Number of constraints
        data_folder: Path to the data_* folder for saving results
        abstraction_level: Level of abstraction for planning
    
    Returns:
        dict: Results of the plan generation process
    """

    model = "gpt-4o-mini"
    #Agents definition
    nl_description_generation_agent = NLDescriptionAgent(model=model)
    formula_generation_agent = FormulaGenerationAgent(model=model)
    constraint_order_agent = ConstraintOrderSelector(model=model)
    plan_generation_agent = PlanGenerationAgent(model=model)
    constraint_analyzer_agent = ConstraintAnalyzerAgent(model=model)
    constraint_trace_check_agent = ConstraintCheckSelector(model=model)
    trace_generation_agent = TraceGenerationAgent(model=model)

    print("\n" + "=" * 80)
    print(f"Processing Problem: {problem_id}")
    print(f"Domain: {domain_name}, Constraints: {num_constraints}")
    print("=" * 80)
    
    # Read natural language description
    nl = open(nl_file_path).read()
    print(f"\nNatural Language Description:\n{nl}")
    
    ###############NATURAL LANGUAGE DOMAIN GENERATION###############
    domain, problem, actions, initial_state, goal, constraints, object_list, predicates_list, predicates_meaning = nl_description_generation(nl,nl_description_generation_agent)
    
    print('DOMAIN: ', domain)
    print('PROBLEM: ', problem)
    print('ACTIONS: ', actions)
    print('INITIAL STATE: ', initial_state)
    print('GOAL: ', goal)
    print('CONSTRAINTS: ', constraints)
    print('OBJECTS: ', object_list)
    print('PREDICATES: ', predicates_list)
    print('PREDICATES MEANING: ', predicates_meaning)
    #input('press to continue to formula generation...')

    ###############LTL FORMULA GENERATION###############
    reasoning, formula, fluent_syntax, goal, constraint_formulas = ltl_formula_generation(domain, problem, goal, constraints, formula_generation_agent, object_list, predicates_list, predicates_meaning)

    print('REASONING: ', reasoning)
    print('LTL FORMULA: ', formula)
    print('FLUENT SYNTAX: ', fluent_syntax)
    print('CONSTRAINT FORMULAS: ', constraint_formulas)
    #input('\nPRESS ENTER TO CONTINUE...')

    reasoning, ordered_constraints, conditional_constraints, global_constraints =constraint_order_selection(domain, problem, initial_state, goal, constraints, constraint_order_agent, object_list, predicates_list, predicates_meaning)
    
    # Keep deep copies of the original constraints for final verification
    ordered_constraints_original = copy.deepcopy(ordered_constraints)
    conditional_constraints_original = copy.deepcopy(conditional_constraints)
    global_constraints_original = copy.deepcopy(global_constraints)

    


    print('REASONING: ', reasoning)
    print('CONSTRAINT ORDER: ', ordered_constraints)
    print('CONDITIONAL CONSTRAINTS: ', conditional_constraints)
    print('GLOBAL CONSTRAINTS: ', global_constraints)
    #input('\nPRESS ENTER TO CONTINUE...')

    ############### PLANNING ###############
    success = False
    feedback = None
    count = 0
    while (success == False):
        current_state = initial_state
        plan = []
        states = []
        states.append(current_state)
        solved_constraints = []
        new_subgoals = []
        
        # Use an index-based while loop so we can append new subgoals
        # to `ordered_constraints` on the fly and have them processed
        # in the same run.
        idx = 0
        while idx < len(ordered_constraints):
            subgoal = ordered_constraints[idx]
            print('SOLVING CONSTRAINT/SUBGOAL:' , subgoal)

            # future_constraints are the ordered_constraints after the current one
            future_constraints = ordered_constraints[idx+1:]

            # Find feedback specific to this subgoal
            specific_feedback = None
            if feedback:
                for fb in feedback:
                    # Remove prefix from constraint to match with subgoal
                    constraint_text = fb['constraint']
                    # Extract the constraint without the prefix
                    if ':' in constraint_text:
                        constraint_without_prefix = constraint_text.split(':', 1)[1].strip()
                    else:
                        constraint_without_prefix = constraint_text
                    
                    # Check if this feedback is for the current subgoal
                    if (str(subgoal).lower() in constraint_without_prefix.lower() or 
                        constraint_without_prefix.lower() in str(subgoal).lower()):
                        specific_feedback = fb['how_to_solve']
                        print(f"Found specific feedback for this constraint: {specific_feedback}")
                        break

            reasoning, subgoal_description, subplan, new_state, solved_subgoals = plan_generation(
                domain,
                problem,
                initial_state=current_state,
                goal=goal,
                current_subgoal=subgoal,
                future_subgoals=future_constraints,
                conditional_constraints=conditional_constraints,
                global_constraints=global_constraints,
                agent=plan_generation_agent,
                feedback = specific_feedback
            )
            print('REASONING: ', reasoning)
            print('SUBGOAL DESCRIPTION: ', subgoal_description)
            print('GENERATED SUBPLAN: ', subplan)
            print('NEW STATE: ', new_state)
            print('SOLVED SUBGOALS: ', solved_subgoals)
            #input('\nPRESS ENTER TO CONTINUE...')


            current_state = new_state
            plan.append(subplan)
            states.append(current_state)
            solved_constraints.append(subgoal_description)

            idx += 1

            if conditional_constraints:
                reasoning, new_subgoals = constraint_analysis(domain, problem, states, plan, goal, conditional_constraints, global_constraints, constraint_analyzer_agent)
                print('REASONING: ', reasoning)
                print('NEW POST-CONDITIONS (if any): ', new_subgoals)
                #input('\nPRESS ENTER TO CONTINUE...')
                
                # Check if new_subgoals appear in conditional_constraints
                # If they do, remove them from conditional_constraints and add to ordered_constraints
                if new_subgoals:
                    constraints_to_remove = []
                    subgoals_to_add = []
                    
                    for new_subgoal in new_subgoals:
                        matched = False
                        for conditional_constraint in conditional_constraints:
                            # Check if new_subgoal appears partially in conditional_constraint or vice versa
                            if (str(new_subgoal).lower() in str(conditional_constraint).lower() or 
                                str(conditional_constraint).lower() in str(new_subgoal).lower()):
                                if conditional_constraint not in constraints_to_remove:
                                    constraints_to_remove.append(conditional_constraint)
                                    print(f"Found matching constraint: '{conditional_constraint}' matches '{new_subgoal}'")
                                matched = True
                        
                        # Add the new_subgoal only if it matched
                        if matched:
                            subgoals_to_add.append(new_subgoal)
                    
                    # Remove matched constraints from conditional_constraints
                    for constraint in constraints_to_remove:
                        conditional_constraints.remove(constraint)
                        print(f"Removed from conditional_constraints: {constraint}")
                    
                    # Add matching subgoals to ordered_constraints (at the end)
                    for subgoal in subgoals_to_add:
                        ordered_constraints.append(subgoal)
                        print(f"Added to ordered_constraints: {subgoal}")
            
            # If some subgoals were marked as solved by the planner,
            # remove them from the remaining (not-yet-analyzed) part
            # of ordered_constraints so we don't process them again.
            if solved_subgoals:
                solved_set = set(solved_subgoals)
                before_len = len(ordered_constraints)
                # Keep everything up to and including current idx,
                # then filter out any future constraints that are solved.
                ordered_constraints = ordered_constraints[:idx+1] + [s for s in ordered_constraints[idx+1:] if s not in solved_set]
                removed = before_len - len(ordered_constraints)
                if removed:
                    print(f"Removed {removed} already-solved subgoal(s) from future ordered_constraints: {solved_subgoals}")

        #Finally solving the goal
        reasoning, subgoal_description, subplan, new_state, solved_subgoals = plan_generation(
                domain,
                problem,
                initial_state=current_state,
                goal=goal,
                current_subgoal=goal,
                future_subgoals=future_constraints,
                conditional_constraints=conditional_constraints,
                global_constraints=global_constraints,
                agent=plan_generation_agent,
            )
        print('REASONING: ', reasoning)
        print('SUBGOAL DESCRIPTION: ', subgoal_description)
        print('GENERATED SUBPLAN: ', subplan)
        print('NEW STATE: ', new_state)
        print('SOLVED SUBGOALS: ', solved_subgoals)
        #input('\nPRESS ENTER TO CONTINUE...')


        current_state = new_state
        plan.append(subplan)
        states.append(current_state)
        solved_constraints.append(subgoal_description)

        flattened_plan = [item for sublist in plan for item in sublist]


        ##############TRACE GENERATION ##############
        trace_states = []
        trace_states.append(initial_state)
        for step in flattened_plan:
            reasoning, new_state = trace_generation(domain, problem, trace_states[-1], step, goal, trace_generation_agent)
            trace_states.append(new_state)
            print('REASONING: ', reasoning)
            print('NEW STATE: ', new_state)
            #input('\nPRESS ENTER TO CONTINUE...')



            
        print('\nCONSTRAINT LEVEL PLAN:')
        for step in solved_constraints:
            print('STEP: ', step)
        
        print('\nHIGH-LEVEL PLAN:')
        for step in flattened_plan:
            print('STEP: ', step)    

        print('\nSTATES')
        for state in trace_states:
            print('STATE: ', state)

        #input('\nPRESS ENTER TO CONSTRAINT CHECK...')

        satisfied_list = []
        reasoning_list = []
        how_to_solve_list = []
        feedback = []

        # Merge all constraint types into a single flat list with prefixes
        # Handle both flat lists and nested lists
        def flatten_with_prefix(constraint_list, prefix):
            """Flatten a list and add prefix to each constraint."""
            flattened = []
            for item in constraint_list:
                if isinstance(item, list):
                    for sub_item in item:
                        flattened.append(f"{prefix} {sub_item}")
                else:
                    flattened.append(f"{prefix} {item}")
            return flattened
        
        constraints_merged = (
            flatten_with_prefix(ordered_constraints_original, "True in at least one state:") +
            flatten_with_prefix(conditional_constraints_original, "Conditional constraint:") +
            flatten_with_prefix(global_constraints_original, "True in every state:")
        )
        
        for constraint in constraints_merged:
            print(f'\nCHECKING CONSTRAINT: {constraint}')
            reasoning, satisfied, how_to_solve = constraint_check(domain, problem, trace_states, constraint, constraint_trace_check_agent)
            print('REASONING: ', reasoning)
            print('SATISFIED: ', satisfied)
            print('HOW TO SOLVE: ', how_to_solve)
            satisfied_list.append(satisfied)
            reasoning_list.append(reasoning)
            how_to_solve_list.append(how_to_solve)
            #input('\nPRESS ENTER TO CONTINUE...')

        if all(satisfied_list):
            success = True
            print('\n' + '='*80)
            print('PLAN COMPLETED')
            print('='*80)
        else:
            success = False
            count += 1
            if count >= max_attempts:
                print('\n' + '='*80)
                print('MAX ATTEMPTS REACHED. PLANNING FAILED.')
                print('='*80)
                break
            print('\n' + '='*80)
            print('UNSATISFIED CONSTRAINTS:')
            feedback = []  # Reset feedback for this iteration
            for i, is_satisfied in enumerate(satisfied_list):
                if not is_satisfied:
                    print(f'Constraint: {constraints_merged[i]}')
                    print(f'HOW TO SOLVE: {how_to_solve_list[i]}')
                    # Associate the failed constraint with its solution
                    feedback.append({
                        'constraint': constraints_merged[i],
                        'how_to_solve': how_to_solve_list[i]
                    })
            print('='*80)

        
        #input('\nPRESS ENTER TO CONTINUE...')
        
    # Create a detailed markdown file for this problem
    try:
        problem_folder = Path(nl_file_path).parent
        md_path = problem_folder / f"{problem_id}_detailed_report.md"

        md_lines = []
        md_lines.append(f"# Problem {problem_id} - Detailed Report\n\n")
        md_lines.append(f"**Status**: {'✓ SUCCESS' if success else '✗ FAILED'}\n")
        md_lines.append(f"**Attempts**: {count}\n")
        md_lines.append(f"**Domain**: {domain_name}\n")
        md_lines.append(f"**Number of Constraints**: {num_constraints}\n\n")
        md_lines.append("---\n\n")
        
        # Natural Language Description
        md_lines.append("## Natural Language Description\n\n")
        md_lines.append("```\n")
        md_lines.append(nl + "\n")
        md_lines.append("```\n\n")
        
        # Domain Information
        md_lines.append("## Domain Information\n\n")
        md_lines.append("### Domain\n```\n")
        md_lines.append(str(domain) + "\n")
        md_lines.append("```\n\n")
        
        md_lines.append("### Problem\n```\n")
        md_lines.append(str(problem) + "\n")
        md_lines.append("```\n\n")
        
        md_lines.append("### Actions\n```\n")
        md_lines.append(str(actions) + "\n")
        md_lines.append("```\n\n")
        
        md_lines.append("### Objects\n```\n")
        md_lines.append(str(object_list) + "\n")
        md_lines.append("```\n\n")
        
        md_lines.append("### Predicates\n```\n")
        md_lines.append(str(predicates_list) + "\n")
        md_lines.append("```\n\n")
        
        md_lines.append("### Predicates Meaning\n```\n")
        md_lines.append(str(predicates_meaning) + "\n")
        md_lines.append("```\n\n")
        
        # Initial State and Goal
        md_lines.append("## Planning Problem\n\n")
        md_lines.append("### Initial State\n```\n")
        md_lines.append(str(initial_state) + "\n")
        md_lines.append("```\n\n")
        
        md_lines.append("### Goal\n```\n")
        md_lines.append(str(goal) + "\n")
        md_lines.append("```\n\n")
        
        md_lines.append("### Constraints\n```\n")
        md_lines.append(str(constraints) + "\n")
        md_lines.append("```\n\n")
        
        # LTL Formula
        md_lines.append("## LTL Formula Generation\n\n")
        md_lines.append("### Reasoning\n```\n")
        md_lines.append(str(reasoning) + "\n")
        md_lines.append("```\n\n")
        
        md_lines.append("### LTL Formula\n```\n")
        md_lines.append(str(formula) + "\n")
        md_lines.append("```\n\n")
        
        md_lines.append("### Fluent Syntax\n```\n")
        md_lines.append(str(fluent_syntax) + "\n")
        md_lines.append("```\n\n")
        
        md_lines.append("### Constraint Formulas\n```\n")
        md_lines.append(str(constraint_formulas) + "\n")
        md_lines.append("```\n\n")
        
        # Constraint Ordering
        md_lines.append("## Constraint Ordering\n\n")
        md_lines.append("### Ordered Constraints\n```\n")
        md_lines.append(str(ordered_constraints_original) + "\n")
        md_lines.append("```\n\n")
        
        md_lines.append("### Conditional Constraints\n```\n")
        md_lines.append(str(conditional_constraints_original) + "\n")
        md_lines.append("```\n\n")
        
        md_lines.append("### Global Constraints\n```\n")
        md_lines.append(str(global_constraints_original) + "\n")
        md_lines.append("```\n\n")
        
        # Generated Plan (always show, regardless of success/failure)
        md_lines.append("## Generated Plan\n\n")
        
        if solved_constraints and len(solved_constraints) > 0:
            md_lines.append("### Constraint-Level Plan\n```\n")
            for i, step in enumerate(solved_constraints, 1):
                md_lines.append(f"{i}. {step}\n")
            md_lines.append("```\n\n")
        else:
            md_lines.append("### Constraint-Level Plan\n```\n")
            md_lines.append("No constraint-level plan generated.\n")
            md_lines.append("```\n\n")
        
        if flattened_plan and len(flattened_plan) > 0:
            md_lines.append("### High-Level Plan\n```\n")
            for i, step in enumerate(flattened_plan, 1):
                md_lines.append(f"{i}. {step}\n")
            md_lines.append("```\n\n")
        else:
            md_lines.append("### High-Level Plan\n```\n")
            md_lines.append("No high-level plan generated.\n")
            md_lines.append("```\n\n")
        
        # State Trace (always show, regardless of success/failure)
        md_lines.append("## State Trace\n\n")
        if trace_states and len(trace_states) > 0:
            for i, state in enumerate(trace_states):
                md_lines.append(f"### State {i}\n```\n")
                md_lines.append(str(state) + "\n")
                md_lines.append("```\n\n")
        else:
            md_lines.append("```\n")
            md_lines.append("No states generated.\n")
            md_lines.append("```\n\n")
        
        # Constraint Verification Results
        md_lines.append("\n## Constraint Verification\n\n")
        for i, constraint in enumerate(constraints_merged):
            status_icon = "✓" if satisfied_list[i] else "✗"
            md_lines.append(f"### {status_icon} Constraint {i+1}\n\n")
            md_lines.append(f"**Constraint:** {constraint}\n\n")
            md_lines.append(f"**Status:** {'SATISFIED' if satisfied_list[i] else 'UNSATISFIED'}\n\n")
            md_lines.append(f"**Reasoning:**\n```\n{reasoning_list[i]}\n```\n\n")
            if not satisfied_list[i]:
                md_lines.append(f"**How to Solve:**\n```\n{how_to_solve_list[i]}\n```\n\n")
            md_lines.append("---\n\n")
        
        # Summary
        md_lines.append("## Summary\n\n")
        satisfied_count = sum(satisfied_list)
        total_count = len(satisfied_list)
        md_lines.append(f"- **Total Constraints:** {total_count}\n")
        md_lines.append(f"- **Satisfied:** {satisfied_count}/{total_count}\n")
        md_lines.append(f"- **Unsatisfied:** {total_count - satisfied_count}/{total_count}\n")
        md_lines.append(f"- **Final Status:** {'SUCCESS ✓' if success else 'FAILED ✗'}\n")
        md_lines.append(f"- **Total Attempts:** {count}\n")

        md_path.parent.mkdir(parents=True, exist_ok=True)
        with open(md_path, "w", encoding="utf-8") as f:
            f.writelines(md_lines)

        print(f"\n{'='*80}")
        print(f"Detailed report saved: {md_path}")
        print(f"{'='*80}\n")
    except Exception as e:
        print(f"Warning: couldn't write markdown for problem {problem_id}: {e}")
        import traceback
        traceback.print_exc()

    # Collect unsatisfied constraints with their details
    unsatisfied_constraints = []
    for i, is_satisfied in enumerate(satisfied_list):
        if not is_satisfied:
            constraint_text = constraints_merged[i]
            # Determine constraint type from prefix
            if constraint_text.startswith("True in at least one state:"):
                constraint_type = "Normal"
            elif constraint_text.startswith("Conditional constraint:"):
                constraint_type = "Conditional"
            elif constraint_text.startswith("True in every state:"):
                constraint_type = "Global"
            else:
                constraint_type = "Unknown"
            
            unsatisfied_constraints.append({
                'constraint': constraint_text,
                'type': constraint_type,
                'reasoning': reasoning_list[i],
                'how_to_solve': how_to_solve_list[i]
            })

    return {
        'problem_id': problem_id,
        'success': success,
        'attempts': count,
        'md_path': str(md_path) if 'md_path' in locals() else None,
        'unsatisfied_constraints': unsatisfied_constraints,
        'ltl_formula': formula if 'formula' in locals() else None,
        'ltl_syntax_meaning': fluent_syntax if 'fluent_syntax' in locals() else None,
        'constraint_driven_plan': solved_constraints if 'solved_constraints' in locals() else None,
        'extended_plan': flattened_plan if 'flattened_plan' in locals() else None,
        'trace': trace_states if 'trace_states' in locals() else None
    }



def main():
    """
    Main function to run the planner on all problems in a domain with specified constraints.
    """
    parser = argparse.ArgumentParser(description='Run High-Level Planner on a domain with specified constraints')
    parser.add_argument('domain', type=str, help='Domain name (e.g., blocksworld, logistics, sokoban)')
    parser.add_argument('num_constraints', type=int, help='Number of constraints (e.g., 1, 5)')
    parser.add_argument('abstraction_level', type=str, help='Abstraction level for planning (e.g., low, medium, high)')
    parser.add_argument('--interactive', action='store_true', help='Enable interactive mode with pauses')
    parser.add_argument('--start-from', type=int, default=None, help='Start from a specific problem number (useful for resuming)')
    
    args = parser.parse_args()

    max_attempts = 5
    
    domain_name = args.domain
    num_constraints = args.num_constraints
    abstraction_level = args.abstraction_level
    
    # Construct path to data folder
    # Path from workspace root: /workspace/data/{domain}/data/data_{num_constraints}
    # File is at: /workspace/src/lapis/planner/high/Planner/main.py
    domains_path = Path(__file__).parent.parent.parent.parent.parent.parent / 'data'
    domain_path = domains_path / domain_name / 'data'
    data_folder = domain_path / f'data_{num_constraints}'
    
    # Check if domain exists
    if not domain_path.exists():
        print(f"Error: Domain '{domain_name}' not found at {domain_path}")
        print(f"Available domains: {', '.join([d.name for d in domains_path.iterdir() if d.is_dir()])}")
        sys.exit(1)
    
    # Check if data folder exists
    if not data_folder.exists():
        print(f"Error: Data folder 'data_{num_constraints}' not found for domain '{domain_name}'")
        available_data = [d.name for d in domain_path.iterdir() if d.is_dir() and d.name.startswith('data_')]
        print(f"Available data folders: {', '.join(available_data)}")
        sys.exit(1)
    
    print("=" * 80)
    print(f"HIGH-LEVEL PLANNER")
    print("=" * 80)
    print(f"Domain: {domain_name}")
    print(f"Number of Constraints: {num_constraints}")
    print(f"Abstraction Level: {abstraction_level}")
    print(f"Data Folder: {data_folder}")
    print(f"Interactive Mode: {'Enabled' if args.interactive else 'Disabled'}")
    if args.start_from:
        print(f"Starting from Problem: {args.start_from}")
    print("=" * 80)
    
    # Get all problem folders (numeric directories)
    problem_folders = sorted([d for d in data_folder.iterdir() if d.is_dir() and d.name.isdigit()], 
                            key=lambda x: int(x.name))
    
    if not problem_folders:
        print(f"Error: No problem folders found in {data_folder}")
        sys.exit(1)
    
    print(f"\nFound {len(problem_folders)} problems to process")
    print(f"Problem IDs: {', '.join([p.name for p in problem_folders])}")
    print("\n" + "=" * 80)
    
    # Create GPT agent
    #agent = GPTAgent(model="gpt-4o-mini")
    
    # Load results from previously completed problems
    results = load_previous_results(data_folder, problem_folders, args.start_from)
    
    for problem_folder in problem_folders:
        problem_id = problem_folder.name
        problem_num = int(problem_id)
        
        # Skip problems before start_from if specified
        if args.start_from and problem_num < args.start_from:
            print(f"\nSkipping Problem {problem_id} (already completed in previous run)")
            continue
        
        nl_file = problem_folder / 'nl'
        
        # Check if nl file exists
        if not nl_file.exists():
            print(f"\nWarning: 'nl' file not found in {problem_folder}, skipping...")
            continue
        
        try:
            result = process_problem(max_attempts, nl_file, problem_id, domain_name, num_constraints, data_folder, abstraction_level)
            results.append(result)
            
            # Update final summary after each problem
            update_final_summary(results, domain_name, num_constraints, abstraction_level, data_folder)
            
            # Update global summary across all constraint levels
            update_global_summary(domain_path)
            
            if args.interactive:
                input('\nPRESS ENTER TO CONTINUE TO NEXT PROBLEM...')
        except Exception as e:
            print(f"\nError processing problem {problem_id}: {str(e)}")
            import traceback
            traceback.print_exc()
            
            results.append({
                'problem_id': problem_id,
                'success': False,
                'attempts': 0,
                'error': str(e),
                'unsatisfied_constraints': []
            })
            
            # Update final summary even after errors
            update_final_summary(results, domain_name, num_constraints, abstraction_level, data_folder)
            
            # Update global summary even after errors
            update_global_summary(domain_path)
    
    # Ensure final summary is generated even if all problems were loaded from previous runs
    if results:
        update_final_summary(results, domain_name, num_constraints, abstraction_level, data_folder)
        update_global_summary(domain_path)
    
    # Print final summary to console
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print(f"Domain: {domain_name}")
    print(f"Constraints: {num_constraints}")
    print(f"Abstraction Level: {abstraction_level}")
    print(f"Total Problems: {len(results)}")
    
    successful = sum(1 for r in results if r.get('success', False))
    failed = len(results) - successful
    success_rate = (successful / len(results) * 100) if results else 0
    
    print(f"Successful: {successful}/{len(results)} ({success_rate:.1f}%)")
    print(f"Failed: {failed}/{len(results)} ({100-success_rate:.1f}%)")
    
    # Calculate average attempts for successful problems
    successful_attempts = [r.get('attempts', 0) for r in results if r.get('success', False) and r.get('attempts')]
    avg_attempts = sum(successful_attempts) / len(successful_attempts) if successful_attempts else 0
    max_attempts_used = max(successful_attempts) if successful_attempts else 0
    min_attempts_used = min(successful_attempts) if successful_attempts else 0
    
    print(f"\nAttempts Statistics (successful problems):")
    print(f"  Average: {avg_attempts:.2f}")
    print(f"  Min: {min_attempts_used}")
    print(f"  Max: {max_attempts_used}")
    
    print("\nDetailed Results:")
    for result in results:
        status = "✓" if result.get('success', False) else "✗"
        attempts = result.get('attempts', 'N/A')
        error = f" (Error: {result['error']})" if 'error' in result else ""
        result_line = f"  {status} Problem {result['problem_id']}: {'Success' if result.get('success', False) else 'Failed'} - Attempts: {attempts}{error}"
        print(result_line)
    
    summary_file = data_folder / 'results' / 'FINAL_SUMMARY.md'
    final_summary_file = domain_path / 'FINAL_SUMMARY.md'
    print("=" * 80)
    print(f"FINAL SUMMARY REPORT (ALL CONSTRAINT LEVELS) available at:")
    print(f"  {final_summary_file}")
    print(f"\nCurrent constraint level ({num_constraints}) summary also at:")
    print(f"  {summary_file}")
    print("=" * 80)

if __name__ == "__main__":
    main()