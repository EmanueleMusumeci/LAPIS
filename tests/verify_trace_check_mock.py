
import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Set path to allow imports
sys.path.insert(0, "/DATA/LAPIS")

import logging
# Configure logger to see output in console
logger = logging.getLogger("my_logger")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('[%(levelname)s] - %(message)s'))
    logger.addHandler(handler)

from src.lapis.pipelines.multi_level_planning import MultiLevelPlanningPipeline

from pathlib import Path

class TestTraceCheckFlow(unittest.TestCase):
    def test_trace_check_only_at_end(self):
        print("Starting mock test...")
        
        # Mock agent
        agent_mock = MagicMock()
        
        # Initialize pipeline
        pipeline = MultiLevelPlanningPipeline(
            agent=agent_mock, 
            high_level_domain_name="test_domain",
            high_level_constraints_num=1,
            base_dir=Path("/tmp"),
            data_dir=Path("/tmp"),
            results_dir=Path("/tmp/results"),
            splits="test"
        )
        
        # Mock components to avoid real work
        pipeline.high_level_planner = MagicMock()
        pipeline.low_level_planner = MagicMock()
        
        # Mock plan methods
        pipeline._extract_plan_from_file = MagicMock(return_value=["step1", "step2"])
        pipeline.high_level_planner.plan.return_value = {
            'success': True,
            'plan': 'step1\nstep2',
            'domain': 'd', 'problem': 'p', 'actions': [], 'goal': 'g', 'constraints': 'c',
            'formula': 'F(a)' # Global formula
        }
        
        # Mock internal helpers
        pipeline._generate_fluent_assignment = MagicMock(return_value={'a': 'a'})
        pipeline._convert_states_to_sets = MagicMock(return_value=[{'a'}]) # Mock conversion to return valid trace
        pipeline._associate_fluents_to_step = MagicMock(return_value=([], []))
        pipeline._generate_summary = MagicMock(return_value="Summary")
        pipeline._get_pddl_init_from_simulator = MagicMock(return_value=None)
        
        # Mock logic utils
        pipeline._apply_assignment_substitution = MagicMock(side_effect=lambda x, y: x)
        import src.lapis.utils.logic_utils as logic_utils
        logic_utils.convert_trace_to_strings = MagicMock(return_value=[{'a'}])
        
        # Mock file operations to strict minimum
        with patch('builtins.open', unittest.mock.mock_open(read_data="description")):
            with patch('pathlib.Path.exists', return_value=True):
                with patch('os.makedirs'):
                    with patch('shutil.copy'):
                        with patch('json.dump'): # Don't write real json
                            with patch('src.lapis.pipelines.multi_level_planning.nl_description_generation', return_value=("d", "p", [], "g", "c")):
                                import src.lapis.pipelines.multi_level_planning as mlp_mod
                                MockSim = MagicMock()
                                # Setup mock simulator
                                mock_sim_instance = MockSim.return_value
                                mock_sim_instance.setup.return_value = True
                                mock_sim_instance.problem.all_objects = []
                                mock_sim_instance.current_state = "state1"
                                mock_sim_instance.get_image.return_value = None
                                
                                # Mock get_current_state_string to return a valid state string
                                mock_sim_instance.get_current_state_string.return_value = "state1"

                                # step returns observation with state
                                mock_sim_instance.step.return_value = ({'state': 'state2'}, 0, False, False, {})
                                
                                # Directly set it in the module
                                mlp_mod.BlocksworldSimulator = MockSim
                                
                                # Set generate_high_level_plan to True so we use hl_result
                                pipeline.generate_high_level_plan = True
                                
                                # Set domain to blocksworld to trigger simulator setup
                                pipeline.high_level_domain_name = "blocksworld"
                         
                            # Mock Low Level Planner to succeed immediately
                            # Returns (success, plan_path, refinement_history)
                            pipeline.low_level_planner.plan.return_value = (True, "dummy_path", [])
                            
                            # Mock _parse_plan_to_actions to return non-empty list actions
                            pipeline._parse_plan_to_actions = MagicMock(return_value=['action1'])
                            
                            # CRITICAL: Mock check_trace
                            # We want to count how many times it's called
                            with patch('src.lapis.pipelines.multi_level_planning.check_trace') as mock_check:
                                mock_check.return_value = (True, {})
                                
                                # Run the attempt
                                pipeline._process_task_attempt("test_task", "/tmp/results", 0)
                                
                                # Verification
                                # It should be called ONCE at the end for the global formula
                                # And potentially for other things if configured, but definitely NOT inside the loop per subgoal
                                # for global formula maintenance.
                                
                                # With 2 subgoals:
                                # If old code: called inside loop (so at least 2 times) + maybe end
                                # If new code: called ONLY at end (1 time) + maybe per constraint if we kept constraint checking?
                                
                                # Wait, I kept:
                                # "verified_constraints.append..."
                                # inside the loop?
                                
                                # Let's check my code change.
                                # I removed the "if ltl_formula:" block inside the loop.
                                # That block contained the global check.
                                # There was NO constraint checking inside the loop in the original code I removed?
                                # Let's recall the diff.
                                
                                # Original code had:
                                # if ltl_formula:
                                #    check_trace(global info)
                                #    AND it iterated over constraints and checked them?
                                #    "for constr in current_ll_entry.get("constraints", []): ... check_trace ..."
                                
                                # My replacement removed ALL of that.
                                # So now, there should be ZERO calls to check_trace inside the loop.
                                
                                # And ONE call at the end.
                                
                                print(f"check_trace call count: {mock_check.call_count}")
                                
                                if mock_check.call_count == 1:
                                    print("SUCCESS: check_trace called exactly once.")
                                else:
                                    print(f"FAILURE: check_trace called {mock_check.call_count} times.")
                                    # Print calls to debug
                                    # for call in mock_check.call_args_list:
                                    #     print(call)

if __name__ == '__main__':
    unittest.main()
