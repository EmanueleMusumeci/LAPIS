import os
import sys
import re
from pathlib import Path
from typing import List, Optional

from src.lapis.pipelines.low_level_planning import LowLevelPlanningPipeline
from src.lapis.logger_cfg import logger

class MultiLevelPlanningPipeline(LowLevelPlanningPipeline):
    def __init__(self, 
                 high_level_domain_name: str,
                 high_level_constraints_num: int,
                 **kwargs):
        super().__init__(**kwargs)
        self.high_level_domain_name = high_level_domain_name
        self.high_level_constraints_num = high_level_constraints_num
        
        # Setup paths for High-Level Planner data
        # Assuming the structure matches what I explored: src/lapis/planner/high/Domains/...
        self.planner_root = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "../planner/high")))
        self.domains_path = self.planner_root / 'Domains'
        self.domain_path = self.domains_path / self.high_level_domain_name
        self.data_folder = self.domain_path / f'data_{self.high_level_constraints_num}'

        self.scenes_per_task: Dict = {
            "dining_setup": ["Allensville", "Parole", "Shelbiana"],
            "general": ["Klickitat", "Lakeville", "Leonardo", "Lindenwood", "Markleeville", "Marstons"],
            "house_cleaning": ["Allensville", "Parole", "Shelbiana"],
            "laundry": ["Kemblesville"],
            "office_setup": ["Allensville", "Parole", "Shelbiana"],
            "office_setup_one_slot": ["Allensville", "Parole", "Shelbiana"],
            "pc_assembly": ["Allensville", "Parole", "Shelbiana"],
        }
        self.problems_per_task: Dict = {
            "dining_setup": 6,
            "general": 11,
            "house_cleaning": 6,
            "laundry": 6,
            "office_setup": 8,
            "office_setup_one_slot": 8,
            "pc_assembly": 3,
        }

    def _process_task(self, task_name, results_dir):
        task_dir = os.path.join(self.data_dir, task_name)
        os.makedirs(task_dir, exist_ok=True)

        csv_filepath = os.path.join(results_dir, f"{task_name}.csv")
        self._initialize_csv(csv_filepath)

        task_file_path = os.path.join(self.data_dir, f"{task_name}.json")
        with open(task_file_path) as f:
            task_description = json.load(f)
        
        os.makedirs(os.path.join(results_dir, task_name), exist_ok=True)

        domain_file_path, domain_description = self._setup_domain(task_description, task_name, results_dir)

        for scene_name in self.scenes_per_task[task_name]:
            # Loop over the Gibson scenes of the task
            self._process_scene(
                task_name, scene_name, task_dir, results_dir,
                domain_file_path, domain_description, csv_filepath
            )

    def _setup_domain(self, task_description, task_name, results_dir):
        # Set up domain files based on the pipeline configuration
        if self.generate_domain:
            return None, task_description["domain"]
        else:
            domain_file_path = os.path.join(self.data_dir, task_name.replace("_","-")+"-domain.pddl")

            if not os.path.exists(domain_file_path):
                logger.warning(f"Could not find domain file at path {domain_file_path}")

            if domain_file_path:
                copy_file(domain_file_path, os.path.join(results_dir, task_name, "domain.pddl"))

            return domain_file_path, None

    def _process_scene(self, task_name, scene_name, task_dir, results_dir,
                domain_file_path, domain_description, csv_filepath):

        scene_dir = os.path.join(task_dir, scene_name)

        for problem_id in range(1, self.problems_per_task[task_name] + 1):
            # Loop over all the problems of the scene for that task
            problem_dir = os.path.join(scene_dir, f"problem_{problem_id}")
            results_problem_dir = os.path.join(results_dir, task_name, scene_name, f"problem_{problem_id}")
            os.makedirs(results_problem_dir, exist_ok=True)
            os.makedirs(os.path.join(results_problem_dir, "logs"), exist_ok=True)

            scene_graph_file_path = os.path.join(problem_dir, f"{scene_name}.npz")

            # Copy required files
            for file_name in ["task.txt", "init_loc.txt", "description.txt"]:
                copy_file(os.path.join(problem_dir, file_name), os.path.join(results_problem_dir, file_name))

            logger.info(f"------------ Task: {task_name}, Scene: {scene_name}, Problem {problem_id} ------------")

            self._run_and_log_pipeline(
                task_name, scene_name, f"problem_{problem_id}", results_problem_dir,
                domain_file_path, domain_description, scene_graph_file_path,
                csv_filepath
            )

