import os
import sys
import argparse
from pathlib import Path

# Add workspace root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent.parent))

from openai import OpenAI
from formula_generator import ltl_formula_generation
from plan_generator import plan_generation,generate_plan_step
from trace_generator import trace_generation, init_trace
from trace_check import trace_check, print_trace_check_result
from nl_description_generator import nl_description_generation
from feedback_translator import translate_feedback_to_natural_language
from results_utils import save_plan_to_file, append_result_to_summary, append_to_csv_log, append_to_excel_log
from dotenv import load_dotenv
from src.lapis.agents.gpt import GPTAgent

load_dotenv()  # loads variables from .env into environment


def process_problem(max_attempts, nl_file_path, problem_id, domain_name, num_constraints, data_folder, agent, abstraction_level):
    """
    Process a single problem instance.
    
    Args:
        nl_file_path: Path to the nl file
        problem_id: ID of the problem (folder name)
        domain_name: Name of the domain
        num_constraints: Number of constraints
        data_folder: Path to the data_* folder for saving results
        agent: GPTAgent instance for LLM calls
        abstraction_level: Level of abstraction for planning
    
    Returns:
        dict: Results of the plan generation process
    """
    print("\n" + "=" * 80)
    print(f"Processing Problem: {problem_id}")
    print(f"Domain: {domain_name}, Constraints: {num_constraints}")
    print("=" * 80)
    
    # Read natural language description
    nl = open(nl_file_path).read()
    print(f"\nNatural Language Description:\n{nl[:200]}...")
    
    ###############NATURAL LANGUAGE DOMAIN GENERATION###############
    domain, problem, actions, goal, constraints = nl_description_generation(nl, agent)
    
    ###############LTL FORMULA GENERATION###############
    formula_reasoning, formula, fluent_syntax = ltl_formula_generation(domain, goal, constraints, agent)
    print('\nREASONING:', formula_reasoning)
    print('\nFORMULA: ', formula)
    print('\nFLUENT SYNTAX: ', fluent_syntax)

    #input('press to continue')
    
    is_valid = False
    count_attempts = 0
    previous_attempts = []
    feedback = None
    attempt_history = []  # Track all attempts for saving to file
    
    # Track last successful outputs for CSV logging
    last_plan = None
    last_plan_reasoning = None
    last_trace = None
    last_trace_reasoning = None
    
    print("\n" + "=" * 80)
    print("STARTING ITERATIVE PLAN GENERATION WITH FEEDBACK")
    print("=" * 80)
    
    while count_attempts < max_attempts:
        count_attempts += 1
        print(f"\n{'='*80}")
        print(f"ATTEMPT {count_attempts}/{max_attempts}")
        print(f"{'='*80}")


        '''
        ###############AUTOREGRESSIVE PLAN GENERATION###############
        #INITIAL TRACE GENERATION# 
        plan_end = False
        plan = ''
        reasoning,state = init_trace(domain,problem,formula, fluent_syntax)
        print('REASONING: ', reasoning)
        print('INIT STATE: ', state)
        #input('press to continue')
        while not plan_end:
            #Next step of the plan
            reasoning, plan_step = generate_plan_step(domain, problem, actions, goal, abstraction, constraints, plan, feedback=feedback, previous_attempts=previous_attempts)
            print('\nREASONING: ', reasoning)
            print('\nPLAN STEP:', plan_step)
            plan += f'\n{plan_step}'
            #input('press to continue')
            #Update the state 
            if "COMPLETE" in plan_step:
                plan_end = True
        '''


        ###############PLAN GENERATION###############
        plan_reasoning, plan = plan_generation(domain, problem, actions, goal, abstraction_level, constraints, agent, feedback=feedback, previous_attempts=previous_attempts)
        print(f'\n[Attempt {count_attempts}] PLAN GENERATED')

        print('\nREASONING: ', plan_reasoning)
        print('\nPLAN:', plan)
        #input('press to continue')

        ###############TRACE GENERATION###############
        trace_reasoning, trace = trace_generation(plan, formula, fluent_syntax, agent, problem=problem, domain=domain)

        print(f'[Attempt {count_attempts}] TRACE GENERATED ({len(trace)} states)')

        print(f"\n[Attempt {count_attempts}] STATE SEQUENCE:")
        for i, state in enumerate(trace):
            print(f"State {i}: ({len(state)} fluents)")
            for fact in sorted(state):
                print(f"  - {fact}")
            print()

        #print('REASONING:' ,trace_reasoning)
        #input('press to continue')
        
        # Store for CSV logging
        last_plan = plan
        last_plan_reasoning = plan_reasoning
        last_trace = trace
        last_trace_reasoning = trace_reasoning


    


        ###############TRACE CHECK (FORMAL VERIFICATION)###############
        is_valid, details = trace_check(trace, formula)
        explanation, nl_explanation = print_trace_check_result(is_valid, details)

        print(f'\n[Attempt {count_attempts}] VALID: {is_valid}')

        if not is_valid:
            print(f'\n[Attempt {count_attempts}] CONSTRAINT VIOLATION DETECTED')
            print(f'Technical Details: {details.get("violation_report", "N/A")}')
            print(f'\n{nl_explanation}')
            
            # Translate technical feedback to natural language for the planner
            print(f'\n[Attempt {count_attempts}] Translating feedback to natural language...')
            # Convert plan string to list of actions (remove numbering)
            plan_lines = [line.split('. ', 1)[1] if '. ' in line else line 
                         for line in plan.strip().split('\n') if line.strip()]
            reasoning, explanation, how_to_fix = translate_feedback_to_natural_language(
                technical_feedback=nl_explanation,
                domain=domain,
                problem=problem,
                actions=actions,
                goal=goal,
                constraints=constraints,
                failed_plan=plan_lines,
                agent=agent
            )

            natural_feedback = 'WHAT WENT WRONG: ' + explanation + '\n HOW TO FIX: ' + how_to_fix
            
            print('NATURAL LANGUAGE FEEDBACK REASONING: ', natural_feedback)
            #input('press to continue')
            # Store this failed attempt for history
            attempt_history.append({
                'plan': plan,
                'valid': False,
                'reasoning': plan_reasoning,
                'feedback': natural_feedback,
                'trace': trace,
                'violation_details': details
            })
            
            # Store this failed attempt for next iteration
            previous_attempts.append({
                'plan': plan,
                'issue': natural_feedback,
                'trace': trace
            })
            
            # Prepare feedback for next iteration in natural language
            feedback = natural_feedback
            
            print(f'\n[Attempt {count_attempts}] Natural language feedback prepared')
            print(f'Previous attempts stored: {len(previous_attempts)}')
        else:
            # Store successful attempt
            attempt_history.append({
                'plan': plan,
                'valid': True,
                'reasoning': plan_reasoning
            })
            print(f'\n[Attempt {count_attempts}] ✓ PLAN SATISFIES ALL CONSTRAINTS!')
            break
    
    print('\n\n' + '='*80)
    if is_valid:
        print('SUCCESS: Plan generation completed!')
        print('='*80)
        print(f'\n✓ The generated plan respects all constraints!')
        print(f'\nFinal Plan:\n{plan}')
        print(f'\nLTL Formula: {formula}')
        print(f'Total Attempts: {count_attempts}')
        print(f'\n✓ Plan successfully generated and verified!')
    else:
        print('FAILURE: Could not generate valid plan')
        print('='*80)
        print(f'\n✗ Failed to generate a valid plan after {max_attempts} attempts')
        print(f'\nLast feedback: {feedback}')

    print('='*80)
    
    # Determine status
    status = 'completed' if is_valid else 'failed'
    
    # Get final feedback (for failed plans)
    final_feedback = feedback if not is_valid else None
    
    # Save the plan with full history to file
    save_plan_to_file(data_folder, problem_id, plan, is_valid, attempt_history, formula)
    
    # Append result to summary file immediately
    append_result_to_summary(data_folder, problem_id, is_valid, count_attempts)
    
    # Append to CSV log with all pipeline outputs
    append_to_csv_log(
        data_folder=data_folder,
        problem_id=problem_id,
        domain_name=domain_name,
        num_constraints=num_constraints,
        domain=domain,
        problem=problem,
        actions=actions,
        goal=goal,
        constraints=constraints,
        formula=formula,
        formula_reasoning=formula_reasoning,
        fluent_syntax=fluent_syntax,
        plan=last_plan,
        plan_reasoning=last_plan_reasoning,
        trace=last_trace,
        trace_reasoning=last_trace_reasoning,
        is_valid=is_valid,
        num_loops=count_attempts,
        status=status,
        feedback=final_feedback
    )
    
    # Append to Excel log with colored rows (green=success, red=failure)
    append_to_excel_log(
        data_folder=data_folder,
        problem_id=problem_id,
        domain_name=domain_name,
        num_constraints=num_constraints,
        domain=domain,
        problem=problem,
        actions=actions,
        goal=goal,
        constraints=constraints,
        formula=formula,
        formula_reasoning=formula_reasoning,
        fluent_syntax=fluent_syntax,
        plan=last_plan,
        plan_reasoning=last_plan_reasoning,
        trace=last_trace,
        trace_reasoning=last_trace_reasoning,
        is_valid=is_valid,
        num_loops=count_attempts,
        status=status,
        feedback=final_feedback
    )
    
    return {
        'problem_id': problem_id,
        'success': is_valid,
        'attempts': count_attempts,
        'plan': plan if is_valid else None,
        'formula': formula
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
    agent = GPTAgent(model="gpt-4o-mini")
    
    results = []
    
    for problem_folder in problem_folders:
        problem_id = problem_folder.name
        nl_file = problem_folder / 'nl'
        
        # Check if nl file exists
        if not nl_file.exists():
            print(f"\nWarning: 'nl' file not found in {problem_folder}, skipping...")
            continue
        
        try:
            result = process_problem(max_attempts, nl_file, problem_id, domain_name, num_constraints, data_folder, agent, abstraction_level)
            results.append(result)
            
            if args.interactive:
                input('\nPRESS ENTER TO CONTINUE TO NEXT PROBLEM...')
        except Exception as e:
            print(f"\nError processing problem {problem_id}: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Append error result to summary immediately
            append_result_to_summary(data_folder, problem_id, False, 'N/A')
            
            results.append({
                'problem_id': problem_id,
                'success': False,
                'error': str(e)
            })
    
    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Domain: {domain_name}")
    print(f"Constraints: {num_constraints}")
    print(f"Total Problems: {len(results)}")
    successful = sum(1 for r in results if r.get('success', False))
    print(f"Successful: {successful}/{len(results)}")
    print(f"Failed: {len(results) - successful}/{len(results)}")
    print("\nDetailed Results:")
    
    # Print results (already saved to file incrementally)
    for result in results:
        status = "✓" if result.get('success', False) else "✗"
        attempts = result.get('attempts', 'N/A')
        result_line = f"  {status} Problem {result['problem_id']}: {'Success' if result.get('success', False) else 'Failed'} (Attempts: {attempts})"
        print(result_line)
    
    # Summary file location
    summary_file = data_folder / 'results' / 'summary.txt'
    
    print("=" * 80)
    print(f"\n[Summary available at: {summary_file}]")


if __name__ == "__main__":
    main()