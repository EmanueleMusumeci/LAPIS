import os
import sys
import json
import csv
import time
import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# Add lexicon to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../third-party/lexicon_neurips")))

try:
    from lexicon import (
        evaluate_llms, 
        evaluate_unconstrained_llms, 
        get_metrics_from_stored_llm_answers, 
        decision_making_llms,
        run_lexicon
    )
    from utils.utils import setup_logger, close_logger
except ImportError:
    print("Warning: Could not import lexicon. Make sure third-party/lexicon_neurips is in PYTHONPATH or correctly located.")

from src.costl.utils.log import copy_file
from src.costl.agents.agent import Agent
from src.costl.logger_cfg import logger
from src.costl.pipelines.base import BasePipeline

class LexiconPipeline(BasePipeline):
    def __init__(self, cfg, mode="evaluate", env_class=None, **base_init_kwargs):
        """Initialize LexiconPipeline.
        
        Args:
            cfg: Lexicon configuration object
            mode: Evaluation mode ("generation", "evaluation", "evaluate_unconstrained", "metrics", "decision_making")
            env_class: The domain class (e.g., Blocksworld) to use for the environment
            **base_init_kwargs: Arguments for BasePipeline
        """
        super().__init__(**base_init_kwargs, generate_domain=False, ground_in_sg=False)
        self.cfg = cfg
        self.mode = mode
        self.env_class = env_class
        
        # Validate mode
        valid_modes = ["generation", "evaluation", "evaluate_unconstrained", "metrics", "decision_making"]
        if self.mode not in valid_modes:
            raise ValueError(f"Invalid mode: {self.mode}. Must be one of {valid_modes}")

    def _construct_experiment_name(self):
        agent_name = self.agent.name if self.agent else "no_agent"
        name = f"{self.name}_{agent_name}"
        if self.generate_domain:
            name += "_gendomain"
        if self.ground_in_sg:
            name += "_ground"
        return name

    def _process_task(self, task_name, results_dir):
        # Lexicon handles its own task processing via the cfg object and env_class
        # This method is required by BasePipeline but we delegate to _run_and_log_pipeline
        # or directly call lexicon functions depending on how we want to structure it.
        # Since BasePipeline calls _process_task for each split, we can use it to run the evaluation.
        
        # For Lexicon, the 'task' concept maps to domains/problems defined in cfg
        # We'll assume the cfg is already set up for the correct task/domain
        
        logger.info(f"Processing task {task_name} in mode {self.mode}")
        
        # We need to pass the environment class to lexicon functions
        if self.env_class is None:
            # Try to import LexiCon as fallback, though specific domain class is usually needed
            try:
                from lexicon import LexiCon
                env_class = LexiCon
                logger.warning("No env_class provided, using base LexiCon class. This may fail for specific domains.")
            except ImportError:
                logger.error("Could not import LexiCon class and no env_class provided")
                return
        else:
            env_class = self.env_class

        if self.mode == "generation":
            # run_lexicon handles generation if mode in cfg is 'generation'
            # But run_lexicon also dispatches based on cfg.mode.
            # We can call run_lexicon directly if we trust cfg.mode matches self.mode
            # Or we can call generate_dataset directly if we import it.
            # run_lexicon is a wrapper that calls the right function.
            run_lexicon(self.cfg, env_class)
        elif self.mode == "evaluation":
            evaluate_llms(self.cfg, env_class)
        elif self.mode == "evaluate_unconstrained":
            evaluate_unconstrained_llms(self.cfg, env_class)
        elif self.mode == "metrics":
            get_metrics_from_stored_llm_answers(self.cfg, env_class)
        elif self.mode == "decision_making":
            decision_making_llms(self.cfg, env_class)

    def _initialize_csv(self, csv_filepath):
        # Initialize CSV for results
        # The columns depend on what we want to track
        header = ["Task", "Mode", "Model", "Problem", "Status", "Cost", "OptimalCost", "Time", "Tokens"]
        with open(csv_filepath, mode="w", newline='') as f:
            writer = csv.writer(f, delimiter='|')
            writer.writerow(header)

    def _run_and_log_pipeline(self, task_name, scene_name, problem_id, results_problem_dir,
                            domain_file_path, domain_description, scene_graph_file_path,
                            csv_filepath):
        # This method is typically called by _process_task in BasePipeline subclasses
        # that iterate over problems. Since Lexicon handles its own iteration,
        # we might not use this method directly, or we might adapt Lexicon to use it.
        # For now, we'll leave it as a placeholder or use it if we refactor Lexicon iteration.
        pass
