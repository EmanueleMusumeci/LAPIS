"""Updated AlfWorld domain integration using the new simulator architecture."""

from omegaconf import DictConfig
import hydra
import os
import sys

sys.path.append(os.environ["LEXICON"])

from lexicon import LexiCon, run_lexicon

from typing import Optionalnt

from up_domain import get_alfworld_problem

from utils.constraints import (
    signed_predicates_per_constraint_type,
    domain_axioms,
)

from utils.utils import (
    Sample,
    constrained_problem_files,
)

from mapper import AlfWorldMapper

# Import the new simulator
sys.path.append(os.path.join(os.environ.get("COSTL_ROOT", "/DATA/CoSTL")))
from simulators import AlfWorldSimulator


class AlfWorld(LexiCon):

    def __init__(self, cfg):
        super().__init__(cfg)
        self.signed_predicates_per_constraint_type = signed_predicates_per_constraint_type
        self.domain_axioms = domain_axioms
        self.mapper_class = AlfWorldMapper

        self.render = False

    def _initialize_env(self):
        """Initialize the AlfWorld simulator."""
        try:
            # Initialize AlfWorld simulator with default settings
            self.env = AlfWorldSimulator(
                env_name="AlfWorld-v2"
            )
            print("AlfWorld simulator initialized successfully")
        except ImportError as e:
            print(f"Warning: AlfWorld simulator not available: {e}")
            print("Install with: pip install alfworld")
            print("Simulation features will be disabled")
            self.env = None

    def reset(self, seed: Optional[int], data: Optional[Sample] = None):
        """Reset the environment."""
        self.seed = seed
        self.unconstrained_problem = get_alfworld_problem(seed)
        
        # Reset simulator if available
        if self.env is not None:
            try:
                obs, info = self.env.reset(seed=seed)
                self.observation = obs
            except Exception as e:
                print(f"Warning: Failed to reset simulator: {e}")

    def is_feasible_low_level(self, plan):
        """Check if a plan is feasible by simulating it."""
        if self.env is None:
            print("Warning: Simulator not available, skipping plan validation")
            return True
        
        try:
            return self.env.is_feasible_plan(plan)
        except Exception as e:
            print(f"Error during plan simulation: {e}")
            return False

    def is_feasible_low_level_action(self, action):
        """Check if a single action is feasible."""
        if self.env is None:
            print("Warning: Simulator not available, skipping action validation")
            return True
        
        try:
            return self.env.is_feasible_action(action)
        except Exception as e:
            print(f"Error during action simulation: {e}")
            return False

    def set_domain_name(self):
        self.domain = "alfworld"

    def get_problem_and_plan_nl(self):
        domain_file, problem_file, plan_file = constrained_problem_files(
            self.data_samples_dir, self.seed
        )
        mapper = AlfWorldMapper(domain_file, problem_file, plan_file)

        return mapper.domain_nl(), mapper.problem_nl(), mapper.plan_nl()


@hydra.main(
    version_base=None, config_path=os.path.join(os.environ["LEXICON"], "cfg"), config_name="config"
)
def main(cfg: DictConfig):
    run_lexicon(cfg, AlfWorld)


if __name__ == "__main__":
    main()
