
import unittest
from unittest.mock import MagicMock, patch
import json
import os
import shutil
from pathlib import Path

# Mock dependencies before importing the pipeline
import sys
sys.modules['costl.planner.low'] = MagicMock()
sys.modules['costl.utils'] = MagicMock()

# Mock the specific classes we need
from costl.pipelines.multi_level_planning import MultiLevelPlanningPipeline
from costl.planner.low.low_level_planner import LowLevelPlanner

class TestStopOnFailure(unittest.TestCase):
    def setUp(self):
        # Setup mock paths
        self.base_dir = Path("/tmp/base")
        self.data_dir = Path("/tmp/data")
        self.results_dir = Path("/tmp/results")
        self.splits = {"train": [], "test": []}
        
        # Ensure clean slate
        if self.results_dir.exists():
            shutil.rmtree(self.results_dir)
        self.results_dir.mkdir(parents=True)
        
        # Create a dummy plan file to ensure the loop runs
        self.task_name = "test_failure_task"
        self.problem_dir = self.data_dir / self.task_name
        self.problem_dir.mkdir(parents=True)
        (self.problem_dir / "high").mkdir(parents=True)
        with open(self.problem_dir / "high" / "plan.txt", "w") as f:
            f.write("step1\nstep2\nstep3")
            
        with open(self.problem_dir / "nl", "w") as f:
            f.write("Description")
            
        # Create dummy pddl files
        with open(self.problem_dir / "domain.pddl", "w") as f:
            f.write("(define (domain test) (:requirements :strips))")
        with open(self.problem_dir / "problem.pddl", "w") as f:
            f.write("(define (problem test) (:domain test))")

    @patch('costl.pipelines.multi_level_planning.HighLevelPlanner')
    @patch('costl.pipelines.multi_level_planning.LowLevelPlanner')
    @patch('costl.pipelines.multi_level_planning.BlocksworldSimulator') # Mock simulator to avoid setup
    @patch('costl.pipelines.multi_level_planning.check_trace')
    @patch('costl.pipelines.multi_level_planning.logic_utils')
    def test_stop_on_failure(self, mock_logic_utils, mock_check_trace, mock_sim_class, MockLowPlanner, MockHighPlanner):
        # Setup mocks
        mock_agent = MagicMock()
        
        # Mock HighLevelPlanner
        mock_hl_planner = MockHighPlanner.return_value
        # We don't use it because we provide the plan file, but just in case
        
        # Mock LowLevelPlanner
        mock_ll_planner = MockLowPlanner.return_value
        # Configure plan to return False (failure) for the FIRST call
        # Return format: success, generated_plan_path, refinement_history
        mock_ll_planner.plan.side_effect = [
            (False, None, []),  # First step fails
            (True, "/tmp/plan.txt", []) # Second step (should not be called)
        ]
        
        # Mock Simulator
        mock_sim = mock_sim_class.return_value
        mock_sim.setup.return_value = True
        mock_sim.current_state = MagicMock()
        
        # Mock logic_utils
        mock_logic_utils.extract_ltl_info.return_value = ({}, [])
        
        # Initialize Pipeline
        pipeline = MultiLevelPlanningPipeline(
            agent=mock_agent,
            high_level_domain_name="blocksworld",
            high_level_constraints_num=0,
            base_dir=self.base_dir,
            data_dir=self.data_dir,
            results_dir=self.results_dir,
            splits=self.splits
        )
        
        # Run
        pipeline._process_task_attempt(self.task_name, self.results_dir)
        
        # Verify LowLevelPlanner was called EXACTLY ONCE
        print(f"LowLevelPlanner.plan call count: {mock_ll_planner.plan.call_count}")
        self.assertEqual(mock_ll_planner.plan.call_count, 1, "Should stop after first failure")
        
        # Verify full_plan.txt content
        full_plan_path = self.results_dir / self.task_name / "full_plan.txt"
        self.assertTrue(full_plan_path.exists())
        with open(full_plan_path, "r") as f:
            content = f.read()
        print("Full Plan Content:")
        print(content)
        
        self.assertIn("; SUBGOAL_0_NO_PLAN", content)
        self.assertIn("; SUBGOAL_1_NO_PLAN (File missing)", content)
        self.assertIn("; SUBGOAL_2_NO_PLAN (File missing)", content)

if __name__ == '__main__':
    # Configure logging to see output
    import logging
    logging.basicConfig(level=logging.INFO)
    unittest.main()
