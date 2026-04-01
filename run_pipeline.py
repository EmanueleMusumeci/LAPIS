import sys; sys.path.insert(0, "/DATA/CoSTL")
import patch
import sys
import os
import re
from pathlib import Path

# Get the workspace root directory
workspace_root = Path(__file__).parent.absolute()

# Load API Key manually here to ensure it's available for GPTAgent AND imported modules
key_sh_path = workspace_root / "key.sh"
if key_sh_path.exists():
    with open(key_sh_path, 'r') as f:
        content = f.read().strip()
        match = re.search(r'export API_KEY=(.+)', content)
        if match:
            api_key = match.group(1)
            os.environ["API_KEY"] = api_key
            os.environ["OPENAI_API_KEY"] = api_key # GPTAgent uses this
            print(f"Loaded API Key: {api_key[:5]}...")
        else:
            print("Could not parse API_KEY from key.sh")
else:
    print("key.sh not found")

# Add paths
sys.path.append(str(workspace_root))


from src.costl.pipelines.multi_level_planning import MultiLevelPlanningPipeline
from src.costl.pipelines.baseline import BaselinePipeline
try:
    from src.costl.pipelines.lexicon import LexiconPipeline
except ImportError:
    LexiconPipeline = None

from src.costl.agents.gpt import GPTAgent


import json
import argparse

def main():
    workspace_root = Path(__file__).parent.absolute()
    default_results_dir = str(workspace_root / "results" / "real_run_100")
    
    parser = argparse.ArgumentParser(description="Run CoSTL Pipeline")
    parser.add_argument("--config", help="Path to benchmark config JSON file")
    parser.add_argument("--domain", default="blocksworld", help="High level domain name")
    parser.add_argument("--problem_ids", nargs="+", default=["100","101","102","103","104","105","106","107","108","109","110","111","112"], help="List of problem IDs")
    parser.add_argument("--results_dir", default=default_results_dir, help="Results directory")
    parser.add_argument("--planner", default="up_fd",
                        help="Low-level symbolic planner: 'up_fd' (default, FastDownward via UP), "
                             "'pyperplan' (pure-Python via UP, no forall/when support), "
                             "'fd' (FastDownward subprocess), 'symk' (SymK subprocess)")
    parser.add_argument("--batch_id", default="data_2", help="Data batch ID (e.g. data_1, data_2)")
    parser.add_argument("--use_vector_db", action="store_true", help="Enable Vector DB for refinement")
    parser.add_argument("--model", default="gpt-4o", help="Model name (e.g. gpt-4o, gpt-5.2)")
    parser.add_argument("--pipeline", default="multi_level", help="Pipeline to run: multi_level, baseline, lexicon")
    parser.add_argument("--use_gt_domain", action="store_true", default=False, help="Use the ground truth simulator domain if applicable.")
    parser.add_argument("--no_use_gt_domain", action="store_false", dest="use_gt_domain", help="Disable using the ground truth simulator domain, forcing simulation inside the generated domain.")
    parser.add_argument("--env_name", default=None, help="The specific Gymnasium environment to initialize if applicable (e.g. BabyAI-MiniBossLevel-v0). Defaults to domain-specific defaults if not provided.")

    
    args = parser.parse_args()

    # Initialize agent
    agent = GPTAgent(model=args.model)
    
    configs = []
    if args.config:
        with open(args.config, 'r') as f:
            configs = json.load(f)
    else:
        configs = [{
            "domain": args.domain,
            "problem_ids": args.problem_ids,
            "results_dir": args.results_dir,
            "constraints": 1 # Default
        }]

    for cfg in configs:
        domain = cfg.get("domain", "blocksworld")
        problem_ids = cfg.get("problem_ids", ["100","101","102","103","104","105","106","107","108","109","110","111","112"])
        results_dir = cfg.get("results_dir", args.results_dir)
        # Ensure results_dir includes the batch_id to avoid overwrites
        results_dir = str(Path(results_dir) / args.batch_id)
        constraints = cfg.get("constraints", 1)
        
        print(f"\n{'='*80}")
        print(f"PIPELINE CONFIG: domain={domain}, problems={problem_ids}, constraints={constraints}, pipeline={args.pipeline}")
        print(f"{'='*80}")
        
        if args.pipeline == "multi_level":
            # Initialize pipeline
            pipeline = MultiLevelPlanningPipeline(
                agent=agent,
                high_level_domain_name=domain,
                high_level_constraints_num=constraints,
                base_dir=str(workspace_root),
                data_dir=workspace_root / "data",
                results_dir=results_dir,
                splits=problem_ids,
                generate_domain=False,
                batch_id=args.batch_id,
                low_level_planner_name=args.planner,
                use_vector_db=args.use_vector_db,
                env_name=args.env_name
            )
            # Run pipeline
            pipeline.run()
            
        elif args.pipeline == "baseline":
            pipeline = BaselinePipeline(
                agent=agent,
                cfg=None, # Needs a mocked cfg if it starts using it
                base_dir=str(workspace_root),
                data_dir=str(workspace_root / "data"),
                results_dir=results_dir,
                splits=problem_ids
            )
            pipeline.run()
            
        elif args.pipeline == "lexicon":
            if LexiconPipeline is None:
                print("LexiconPipeline not available. Skipping.")
                continue
                
            class MockCfg:
                def __init__(self, **kwargs):
                    self.__dict__.update(kwargs)
            cfg = MockCfg(
                initial_seed=0,
                num_seeds=len(problem_ids),
                parallelize=False,
                constraint_form=MockCfg(constraints_no=constraints),
                evaluation_data=[int(pid) if pid.isdigit() else pid for pid in problem_ids],
                folder_no=0,
                llm=args.model,
                logs_dir=results_dir,
                mode="evaluation",
                render=False,
                few_shot_data=[]
            )
            
            # Dynamically import domain class inside third-party/lexicon_neurips
            sys.path.insert(0, str(workspace_root / "third-party" / "lexicon_neurips"))
            env_class = None
            if domain == "blocksworld":
                from domains.blocksworld.blocksworld import Blocksworld
                env_class = Blocksworld
            elif domain == "babyai":
                from domains.babyai.babyai import BabyAI
                env_class = BabyAI
            
            pipeline = LexiconPipeline(
                cfg=cfg,
                mode="evaluation",
                env_class=env_class,
                agent=agent,
                base_dir=str(workspace_root),
                data_dir=str(workspace_root / "data"),
                results_dir=results_dir,
                splits=problem_ids,
                batch_id=args.batch_id
            )
            pipeline.run()
        else:
            print(f"Unknown pipeline option: {args.pipeline}")

if __name__ == "__main__":
    main()
