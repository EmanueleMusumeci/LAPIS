import os
import sys
from omegaconf import OmegaConf
from src.costl.pipelines.lexicon import LexiconPipeline

# Add third-party to path to import domains
sys.path.append(os.path.abspath("third-party/lexicon_neurips"))

from domains.blocksworld.blocksworld import Blocksworld

def get_cfg(mode, initial_seed=0, num_seeds=1):
    """Create a configuration object for Lexicon."""
    # Basic config structure based on generate_benchmark.py and config.yaml
    cfg_dict = {
        "mode": mode,
        "initial_seed": initial_seed,
        "num_seeds": num_seeds,
        "parallelize": False,
        "render": False,
        "folder_no": 2,
        "llm": "gpt-4o",
        "planner_name": None, # Set to "symk" to use SymK, or None for auto-selection
        "evaluation_data": [initial_seed + i for i in range(num_seeds)],
        "few_shot_data": [],
        "constraint_form": {
            "constraints_no": 2, # Small number for testing
            "constraint_types": {
                "always": {"operations": ["and"], "arguments_min": 1, "arguments_max": 1},
                "sometime": {"operations": ["or", "and"], "arguments_min": 1, "arguments_max": 2},
                "at_most_once": {"operations": ["and"], "arguments_min": 1, "arguments_max": 1},
                "sometime_before": {"operations": ["or"], "arguments_min": 1, "arguments_max": 2},
                "sometime_after": {"operations": ["or"], "arguments_min": 1, "arguments_max": 2},
            },
        },
        # Domain specific
        "num_blocks": 4, # Small number for testing
        "root_dir": os.path.abspath("third-party/lexicon_neurips/domains/blocksworld"),
    }
    
    # Add derived paths
    cfg_dict["logs_dir"] = os.path.join(cfg_dict["root_dir"], "logs")
    cfg_dict["data_samples_dir"] = os.path.join(cfg_dict["root_dir"], "data")
    
    return OmegaConf.create(cfg_dict)

def run_generation():
    print("\n" + "="*50)
    print("Running Generation Phase")
    print("="*50)
    
    cfg = get_cfg("generation", initial_seed=100, num_seeds=1)
    
    # Initialize pipeline
    pipeline = LexiconPipeline(
        cfg=cfg,
        mode="generation",
        env_class=Blocksworld,
        base_dir=".",
        data_dir="data",
        results_dir="results",
        splits=["test"],
        agent=None, # Not needed for generation
    )
    
    # Run pipeline
    # We call _process_task directly or rely on run() if we implemented it to call _process_task
    # BasePipeline.run() iterates over splits and calls _process_task
    pipeline.run()

def run_evaluation():
    print("\n" + "="*50)
    print("Running Evaluation Phase")
    print("="*50)
    
    cfg = get_cfg("evaluation", initial_seed=100, num_seeds=1)
    
    # Initialize pipeline
    pipeline = LexiconPipeline(
        cfg=cfg,
        mode="evaluation",
        env_class=Blocksworld,
        base_dir=".",
        data_dir="data",
        results_dir="results",
        splits=["test"],
        agent=None, 
    )
    
    # Run pipeline
    pipeline.run()

if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs("results", exist_ok=True)
    
    # Run generation
    # run_generation()
    
    # Run evaluation
    # Note: Evaluation requires LLM API keys. 
    # If not configured, it might fail or we need to mock it.
    # For now, we'll try to run it and see.
    try:
        run_evaluation()
    except Exception as e:
        print(f"Evaluation failed: {e}")
        print("This is expected if LLM API keys are missing or mock LLM is not implemented.")
