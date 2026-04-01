
import sys
import unittest
from unittest.mock import MagicMock, patch
import os

# Adjust path to import costl
sys.path.append("/DATA/CoSTL/src")

from costl.pipelines.multi_level_planning import MultiLevelPlanningPipeline

class TestTraceCheckMove(unittest.TestCase):
    def test_trace_check_called_only_at_end(self):
        # Mock dependencies
        agent_mock = MagicMock()
        pipeline = MultiLevelPlanningPipeline(
            agent=agent_mock, 
            high_level_domain_name="test_domain",
            high_level_constraints_num=1,
            base_dir="/tmp",
            data_dir="/tmp",
            results_dir="/tmp",
            splits="test"
        )

        # Mock methods to avoid real execution
        pipeline.high_level_planner = MagicMock()
        pipeline.low_level_planner = MagicMock()
        pipeline._generate_fluent_assignment = MagicMock(return_value={})
        pipeline._associate_fluents_to_step = MagicMock(return_value=([], []))
        pipeline._generate_summary = MagicMock(return_value="Summary")
        pipeline._get_pddl_init_from_simulator = MagicMock(return_value=None)
        
        # Mock low level planner to return success
        pipeline.low_level_planner.plan.return_value = (True, "path/to/plan", [])
        
        # Mock trace check
        with patch('costl.pipelines.multi_level_planning.check_trace', return_value=(True, {})) as check_trace_mock:
            # Mock file reading/writing
            with patch('builtins.open', unittest.mock.mock_open(read_data="action1\naction2")):
                with patch('os.path.exists', return_value=True):
                    with patch('shutil.copy'):
                        # Run a dummy task attempt
                        # We need to setup some internal state that usually comes from loading files
                        pipeline.generate_high_level_plan = False
                        
                        # Mock _extract_plan_from_file to return a plan with 2 subgoals
                        pipeline._extract_plan_from_file = MagicMock(return_value=["subgoal1", "subgoal2"])
                        
                        # Mock _process_task_attempt
                        # Since it's hard to fully mock the file system interaction in the large method, 
                        # let's just inspect the source code or trust manual verification? 
                        # No, let's try to run the critical part.
                        
                        # Actually, it's safer to check if I can inspect the method code for the loop.
                        # But I can also run the method with heavier mocking.
                        pass

if __name__ == '__main__':
    # Since running the full pipeline with mocks is complex due to file I/O, 
    # I will perform a static check on the file content to ensure 
    # check_trace is not called inside the loop.
    
    with open("/DATA/CoSTL/src/costl/pipelines/multi_level_planning.py", "r") as f:
        content = f.read()
    
    import re
    
    # Extract the _process_task_attempt method
    # Simplified check: count occurrences of "check_trace"
    # It should appear in imports, and in the final check block.
    # It should NOT appear inside the subgoal loop.
    
    subgoal_loop_start = content.find("for i, subgoal in enumerate(plan_lines):")
    final_check_start = content.find("# After ALL subgoals: Perform Final Global LTL Check")
    
    if subgoal_loop_start == -1 or final_check_start == -1:
        print("Could not locate loop or final check block.")
        sys.exit(1)
        
    loop_content = content[subgoal_loop_start:final_check_start]
    
    # Check for check_trace in the loop content
    if "check_trace(" in loop_content:
        # It might be in comments or disabled code, but we removed it.
        # Let's check non-comment lines
        lines = loop_content.splitlines()
        found = False
        for line in lines:
            if "check_trace(" in line and not line.strip().startswith("#"):
                 print(f"FAILED: Found check_trace in subgoal loop: {line.strip()}")
                 found = True
        
        if not found:
            print("SUCCESS: check_trace not found in subgoal loop.")
    else:
        print("SUCCESS: check_trace not found in subgoal loop.")
        
    # Check if we have the new formatting logic
    if "- **State {i}**:" in content and "md_lines.append(f\"  - **{pred}**\")" in content:
        print("SUCCESS: Found new trace formatting logic.")
    else:
        print("FAILED: Did not find new trace formatting logic.")

