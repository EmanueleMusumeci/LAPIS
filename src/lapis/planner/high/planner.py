import os
import sys
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Import helper modules from the same directory (assuming they are in src/lapis/planner/high/Planner)
# We need to ensure sys.path includes the directory where these modules are located
current_dir = Path(__file__).parent
planner_modules_dir = current_dir / "Planner"
sys.path.append(str(planner_modules_dir))

from formula_generator import ltl_formula_generation
from plan_generator import plan_generation, generate_plan_step
from trace_generator import trace_generation, init_trace
from trace_check import trace_check, print_trace_check_result
from nl_description_generator import nl_description_generation
from feedback_translator import translate_feedback_to_natural_language
from results_utils import save_plan_to_file, append_result_to_summary

class HighLevelPlanner:
    def __init__(self, agent):
        self.agent = agent

    def plan(self, nl_file_path, problem_id, domain_name, num_constraints, data_folder, max_attempts=5):
        """
        Process a single problem instance to generate a high-level plan.
        
        Args:
            nl_file_path: Path to the nl file
            problem_id: ID of the problem (folder name)
            domain_name: Name of the domain
            num_constraints: Number of constraints
            data_folder: Path to the data_* folder for saving results
            max_attempts: Maximum number of planning attempts
        
        Returns:
            dict: Results of the plan generation process
        """
        print("\n" + "=" * 80)
        print(f"Processing Problem: {problem_id}")
        print(f"Domain: {domain_name}, Constraints: {num_constraints}")
        print("=" * 80)
        
        # Read natural language description
        with open(nl_file_path, 'r') as f:
            nl = f.read()
        print(f"\nNatural Language Description:\n{nl[:200]}...")
        
        ###############NATURAL LANGUAGE DOMAIN GENERATION###############
        domain, problem, actions, goal, constraints = nl_description_generation(nl, self.agent)
        
        ###############LTL FORMULA GENERATION###############
        reasoning, formula, fluent_syntax = ltl_formula_generation(domain, goal, constraints, self.agent)
        print('\nREASONING:', reasoning)
        print('\nFORMULA: ', formula)
        print('\nFLUENT SYNTAX: ', fluent_syntax)
        
        is_valid = False
        count_attempts = 0
        previous_attempts = []
        feedback = None
        attempt_history = []  # Track all attempts for saving to file
        
        print("\n" + "=" * 80)
        print("STARTING ITERATIVE PLAN GENERATION WITH FEEDBACK")
        print("=" * 80)
        
        final_plan = None
        
        while count_attempts < max_attempts:
            count_attempts += 1
            print(f"\n{'='*80}")
            print(f"ATTEMPT {count_attempts}/{max_attempts}")
            print(f"{'='*80}")

            ###############PLAN GENERATION###############
            plan_reasoning, plan = plan_generation(domain, problem, actions, goal, "high", constraints, self.agent, feedback=feedback, previous_attempts=previous_attempts)
            print(f'\n[Attempt {count_attempts}] PLAN GENERATED')

            print('\nREASONING: ', plan_reasoning)
            print('\nPLAN:', plan)

            ###############TRACE GENERATION###############
            reasoning, trace = trace_generation(plan, formula, fluent_syntax, self.agent)

            print(f'[Attempt {count_attempts}] TRACE REASONING: {reasoning}')
            print(f'[Attempt {count_attempts}] TRACE: {trace}')

            print(f"\n[Attempt {count_attempts}] STATE SEQUENCE:")
            for i, state in enumerate(trace):
                print(f"State {i}:")
                for fact in sorted(state):
                    print(f"  - {fact}")
                print()

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
                reasoning, explanation, how_to_fix = translate_feedback_to_natural_language(
                    technical_feedback=nl_explanation,
                    domain=domain,
                    problem=problem,
                    actions=actions,
                    goal=goal,
                    constraints=constraints,
                    failed_plan=plan,
                    agent=self.agent
                )

                natural_feedback = 'WHAT WENT WRONG: ' + explanation + '\n HOW TO FIX: ' + how_to_fix
                
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
                final_plan = plan
                break
        
        print('\n\n' + '='*80)
        if is_valid:
            print('SUCCESS: Plan generation completed!')
            print('='*80)
            print(f'\n✓ The generated plan respects all constraints!')
            print(f'\nFinal Plan:\n{final_plan}')
            print(f'\nLTL Formula: {formula}')
            print(f'Total Attempts: {count_attempts}')
            print(f'\n✓ Plan successfully generated and verified!')
        else:
            print('FAILURE: Could not generate valid plan')
            print('='*80)
            print(f'\n✗ Failed to generate a valid plan after {max_attempts} attempts')
            print(f'\nLast feedback: {feedback}')

        print('='*80)
        
        # Save the plan with full history to file
        save_plan_to_file(data_folder, problem_id, final_plan if is_valid else "", is_valid, attempt_history, formula)
        
        # Append result to summary file immediately
        append_result_to_summary(data_folder, problem_id, is_valid, count_attempts)
        
        return {
            'problem_id': problem_id,
            'success': is_valid,
            'attempts': count_attempts,
            'plan': final_plan if is_valid else None,
            'formula': formula,
            'fluent_syntax': fluent_syntax,
            # Harmonized data for Low-Level Planner
            'domain': domain,
            'problem': problem,
            'actions': actions,
            'goal': goal,
            'constraints': constraints
        }
