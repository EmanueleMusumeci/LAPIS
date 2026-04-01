import os
import sys
import json
import csv
import time
import datetime
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

# Add lexicon to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../third-party/lexicon_neurips")))

try:
    from unified_planning.io import PDDLReader
except ImportError:
    pass

from src.costl.utils.log import copy_file
from src.costl.agents.agent import Agent
from src.costl.logger_cfg import logger
from src.costl.pipelines.base import BasePipeline

class LexiconPipeline(BasePipeline):
    def __init__(self, cfg, mode="evaluate", env_class=None, **base_init_kwargs):
        """Initialize LexiconPipeline."""
        # Extract custom kwargs required by this specialized pipeline
        self.high_level_domain_name = base_init_kwargs.pop("high_level_domain_name", "blocksworld")
        self.batch_id = base_init_kwargs.pop("batch_id", "data_2")
        
        super().__init__(**base_init_kwargs, generate_domain=False, ground_in_sg=False)
        self.cfg = cfg
        self.mode = mode
        self.env_class = env_class

    def _construct_experiment_name(self):
        agent_name = self.agent.name if self.agent else "no_agent"
        name = f"{self.name}_{agent_name}"
        return name

    def _process_task(self, task_name, results_dir):
        problem_id = task_name
        task_results_dir = Path(results_dir) / problem_id
        task_results_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Processing Lexicon pipeline for problem {problem_id}")

        domain_path = Path(self.data_dir) / self.high_level_domain_name
        data_folder = domain_path / 'data' / self.batch_id
        problem_folder = data_folder / problem_id
        
        domain_pddl_file = problem_folder / 'domain.pddl'
        problem_pddl_file = problem_folder / 'problem.pddl'
        
        if self.env_class is None:
            logger.error("No env_class provided for LexiconPipeline")
            return
            
        env = self.env_class(self.cfg)
        try:
            env.reset(seed=int(problem_id))
        except Exception as e:
            logger.warning(f"env.reset failed: {e}")
            
        reader_constrained = PDDLReader()
        try:
            problem_constrained = reader_constrained.parse_problem(
                str(domain_pddl_file), str(problem_pddl_file)
            )
        except Exception as e:
            logger.error(f"PDDLReader failed: {e}")
            return
            
        mapper = env.mapper_class(problem_constrained)
        system_set_prompt, domain_nl, problem_nl = mapper.get_problem_nl()

        prompt = domain_nl + problem_nl
        model_name = self.cfg.llm
        logger.info(f"Querying model {model_name}...")
        
        start_time = time.time()
        try:
            (response, prompt_tokens, completion_tokens, reasoning_content, reasoning_tokens) = env.prompt_llm(
                model_name, system_set_prompt, prompt
            )
        except Exception as e:
            logger.error(f"env.prompt_llm failed: {e}")
            messages = [
                {"role": "system", "content": system_set_prompt},
                {"role": "user", "content": prompt}
            ]
            response = self.agent.query(messages)
            completion_tokens, reasoning_tokens = 0, 0

        execution_time = time.time() - start_time
        
        try:
            llm_plan = env.parse_response(model_name, response)
        except Exception:
            llm_plan = response
            
        # Write Lexicon raw files
        with open(task_results_dir / f"{model_name}_response", "w") as f:
            f.write(str(response))
        with open(task_results_dir / f"{model_name}_plan", "w") as f:
            f.write(str(llm_plan))
            
        # Verify final plan against compiled constraint benchmarks
        ground_truth_success = False
        ground_truth_failure_reason = ""
        try:
            from src.costl.utils.compile_verifier import verify_plan_with_compiled_val
            compiled_domain = problem_folder / "compiled_domain.pddl"
            compiled_problem = problem_folder / "compiled_problem.pddl"
            plan_file = task_results_dir / f"{model_name}_plan"
            
            ground_truth_success, val_out = verify_plan_with_compiled_val(
                str(compiled_domain),
                str(compiled_problem),
                str(plan_file)
            )
            if not ground_truth_success:
                ground_truth_failure_reason = val_out
            logger.info(f"Compiled VAL Ground Truth Check: {'SUCCESS' if ground_truth_success else ('FAILED: ' + ground_truth_failure_reason)}")
        except Exception as e:
            logger.error(f"Failed to run compiled verification check: {e}")
            
        # Write manifold.json
        manifold = {
            "high_level_plan": [{"action": "solve"}],
            "low_level_plans": [
                {
                    "subgoal": "solve",
                    "plan": str(llm_plan) if llm_plan else "NO_PLAN",
                    "refinement_history": []
                }
            ],
            "lexicon_stats": {
                "time": execution_time,
                "completion_tokens": completion_tokens,
                "reasoning_tokens": reasoning_tokens
            },
            "ground_truth_success": ground_truth_success,
            "ground_truth_failure_reason": ground_truth_failure_reason
        }
        with open(task_results_dir / "manifold.json", "w") as f:
            json.dump(manifold, f, indent=4)
            
        logger.info(f"Finished problem {problem_id} in {execution_time:.2f}s")
        

    def _initialize_csv(self, csv_filepath):
        pass
