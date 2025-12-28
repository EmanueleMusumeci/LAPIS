"""Blocksworld simulator implementation using unified_planning."""

from typing import List, Tuple, Dict, Any, Optional
import unified_planning
from unified_planning.shortcuts import SequentialSimulator
from unified_planning.model import Problem

from .base_simulator import BaseSimulator
# Adjust import path based on project structure
# Assuming domains is importable from root or we need to add it to path
import sys
import os

# Add project root to path to ensure domains can be imported
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from third_party.lexicon_neurips.domains.blocksworld.up_domain import get_blocksworld_problem
except ImportError:
    # Try alternative path if third_party is not a package
    try:
        sys.path.append(os.path.join(project_root, "third-party/lexicon_neurips"))
        from domains.blocksworld.up_domain import get_blocksworld_problem
    except ImportError:
         print("Warning: Could not import get_blocksworld_problem. BlocksworldSimulator will not work.")
         get_blocksworld_problem = None


class BlocksworldSimulator(BaseSimulator):
    """Blocksworld simulator using unified_planning SequentialSimulator.
    
    This simulator generates Blocksworld problems and simulates them using
    the PDDL-based definition.
    """

    def __init__(self, env_name: str = "blocksworld", seed: Optional[int] = None):
        """Initialize Blocksworld simulator.
        
        Args:
            env_name: Name of the environment
            seed: Random seed
        """
        self.seed = seed
        self.problem = None
        self.simulator = None
        self.current_state = None
        # BaseSimulator expects an env, but we don't have a gym env here.
        # We pass None and handle it.
        super().__init__(None)

    def reset(self, seed: Optional[int] = None, **kwargs) -> Tuple[Dict, Dict]:
        """Reset the simulator to an initial state.
        
        Args:
            seed: Random seed
            **kwargs: Additional parameters (e.g. num_blocks)
            
        Returns:
            observation: Initial observation (current state fluents)
            info: Additional info
        """
        if seed is not None:
            self.seed = seed
            
        num_blocks = kwargs.get("num_blocks", 5)
        
        if get_blocksworld_problem is None:
            raise ImportError("Blocksworld domain logic not found.")
            
        self.problem = get_blocksworld_problem(num_blocks=num_blocks, seed=self.seed)
        self.simulator = SequentialSimulator(self.problem)
        self.current_state = self.simulator.get_initial_state()
        
        return self.observation(self.current_state), {"problem": self.problem}

    def map_pddl2simulator(self, action: Any) -> Any:
        """Map PDDL action to simulator action.
        
        Since we use UP simulator, the PDDL action (UP ActionInstance) 
        is already in the correct format or needs to be converted to one.
        
        Args:
            action: PDDL action object
            
        Returns:
            Simulator-specific action
        """
        # If action is already a UP ActionInstance, return it.
        # If it's a plan item wrapper, extract the action.
        # SequentialSimulator.apply expects a UP ActionInstance (plan.actions elements)
        return action

    def map_plan2simulator(self, plan: List[Any]) -> List[Any]:
        """Map PDDL plan to simulator actions.
        
        Args:
            plan: List of PDDL actions
            
        Returns:
            List of simulator actions
        """
        if hasattr(plan, "actions"):
            return plan.actions
        return plan

    def step(self, action: Any) -> Tuple[Dict, float, bool, bool, Dict]:
        """Execute one step in the simulator.
        
        Args:
            action: Action to execute
            
        Returns:
            observation: New observation
            reward: Reward (1 if goal reached, else 0)
            terminated: Whether goal is reached
            truncated: False
            info: Additional info
        """
        if self.simulator is None:
            raise RuntimeError("Simulator not initialized. Call reset() first.")

        if not self.simulator.is_applicable(self.current_state, action):
            # Action not applicable
            # We can raise error or return same state with penalty
            # For now, let's raise error to match strict simulation
            raise ValueError(f"Action {action} is not applicable in current state.")

        self.current_state = self.simulator.apply(self.current_state, action)
        
        # Check goal
        is_goal = self.simulator.is_goal(self.current_state)
        reward = 1.0 if is_goal else 0.0
        
        return self.observation(self.current_state), reward, is_goal, False, {}

    def observation(self, state: Any) -> Dict:
        """Process state into observation.
        
        Args:
            state: UP State
            
        Returns:
            Dictionary of fluents
        """
        # Convert UP state to dictionary representation
        # state.values is a dictionary of {Fluent: Value}
        # We'll convert it to a string representation or keep as is
        return {"state": state}
