import os
import sys
from pathlib import Path
from typing import List, Optional

# Add High_Level_Planner to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../planner/high/Planner")))

try:
    from main import process_problem
except ImportError:
    print("Warning: Could not import High_Level_Planner. Make sure src/lapis/planner/high/Planner is in PYTHONPATH.")

from src.lapis.pipelines.base import BasePipeline
from src.lapis.logger_cfg import logger

class HighLevelPlanningPipeline(BasePipeline):
    def __init__(self, domain_name, num_constraints, max_attempts=5, **base_init_kwargs):
        self.domain_name = domain_name
        self.num_constraints = num_constraints
        self.max_attempts = max_attempts

        # Handle agent being None or not provided
        if 'agent' not in base_init_kwargs or base_init_kwargs['agent'] is None:
            # Create a dummy agent-like object if needed, or just handle it in _construct_experiment_name
            class DummyAgent:
                name = "HighLevelPlanner"
            base_init_kwargs['agent'] = DummyAgent()

        super().__init__(**base_init_kwargs, generate_domain=False, ground_in_sg=False)
        
        # Setup paths based on High_Level_Planner structure
        # High_Level_Planner is now at src/lapis/planner/high
        self.planner_root = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "../planner/high")))
        self.domains_path = self.planner_root / 'Domains'
        self.domain_path = self.domains_path / self.domain_name
        self.data_folder = self.domain_path / f'data_{self.num_constraints}'

    def _construct_experiment_name(self):
        return f"HighLevelPlanner_{self.domain_name}_{self.num_constraints}constr"

    def _process_task(self, task_name, results_dir):
        # task_name corresponds to problem_id in High_Level_Planner
        problem_id = task_name
        
        logger.info(f"Processing problem {problem_id} for domain {self.domain_name} with {self.num_constraints} constraints")
        
        problem_folder = self.data_folder / problem_id
        nl_file = problem_folder / 'nl'
        
        if not nl_file.exists():
            logger.warning(f"NL file not found for problem {problem_id} at {nl_file}")
            return

        try:
            # process_problem saves results to data_folder directly.
            # We pass data_folder as the destination.
            
            result = process_problem(
                self.max_attempts, 
                str(nl_file), 
                problem_id, 
                self.domain_name, 
                self.num_constraints, 
                self.data_folder 
            )
            
            if result['success']:
                logger.info(f"Successfully generated plan for problem {problem_id}")
            else:
                logger.warning(f"Failed to generate plan for problem {problem_id}")
                
        except Exception as e:
            logger.error(f"Error processing problem {problem_id}: {e}")
            import traceback
            traceback.print_exc()

    def _initialize_csv(self, csv_filepath):
        pass
