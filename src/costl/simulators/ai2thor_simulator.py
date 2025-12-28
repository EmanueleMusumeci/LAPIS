"""AI2THOR simulator implementation.

This simulator integrates the AI2THOR environment for household task planning.
AI2THOR provides embodied AI tasks in simulated household environments.

Required packages:
    - ai2thor: Install with `pip install ai2thor`
    
Usage:
    To use this simulator, you need to have AI2THOR installed.
    See: https://github.com/allenai/ai2thor
"""

from typing import List, Tuple, Dict, Any, Optional
from .base_simulator import BaseSimulator
from .utils import InfeasiblePlan


class AI2THORSimulator(BaseSimulator):
    """AI2THOR simulator with PDDL action mapping.
    
    This simulator wraps an AI2THOR environment and provides PDDL action
    translation and execution for household tasks.
    """

    def __init__(self, **env_kwargs):
        """Initialize AI2THOR simulator.
        
        Args:
            **env_kwargs: Additional arguments for environment creation
                          (e.g., width, height, scene)
        """
        try:
            import ai2thor.controller
        except ImportError:
            raise ImportError(
                "AI2THOR not installed. Install with: pip install ai2thor\n"
                "See: https://github.com/allenai/ai2thor"
            )
        
        # Default configuration if not provided
        if "scene" not in env_kwargs:
            env_kwargs["scene"] = "FloorPlan10"
        if "gridSize" not in env_kwargs:
            env_kwargs["gridSize"] = 0.25
            
        self.controller = ai2thor.controller.Controller(**env_kwargs)
        super().__init__(self.controller)
        
        self.current_event = None

    def reset(self, seed: Optional[int] = None, **kwargs) -> Tuple[Dict, Dict]:
        """Reset the AI2THOR environment.
        
        Args:
            seed: Random seed (not directly supported by reset, but can be used for scene selection if needed)
            **kwargs: Additional reset parameters (e.g., scene)
            
        Returns:
            observation: Initial observation
            info: Additional information dictionary
        """
        if "scene" in kwargs:
            self.current_event = self.controller.reset(kwargs["scene"])
        else:
            self.current_event = self.controller.reset(self.controller.scene)
            
        return self.observation(self.current_event), {}

    def map_pddl2simulator(self, action: Any) -> Dict[str, Any]:
        """Map PDDL action to AI2THOR action dictionary.
        
        Args:
            action: PDDL action object with action.name and action.actual_parameters
            
        Returns:
            Action dictionary for AI2THOR controller
        """
        action_name = action.action.name.lower()
        params = [str(p) for p in action.actual_parameters]
        
        # Basic mapping - this will need to be expanded based on specific PDDL domain
        if action_name == "moveahead":
            return {"action": "MoveAhead"}
        elif action_name == "moveback":
            return {"action": "MoveBack"}
        elif action_name == "moveleft":
            return {"action": "MoveLeft"}
        elif action_name == "moveright":
            return {"action": "MoveRight"}
        elif action_name == "rotateleft":
            return {"action": "RotateLeft"}
        elif action_name == "rotateright":
            return {"action": "RotateRight"}
        elif action_name == "lookup":
            return {"action": "LookUp"}
        elif action_name == "lookdown":
            return {"action": "LookDown"}
        elif action_name == "openobject":
            # Assuming params: [agent, object_id]
            return {"action": "OpenObject", "objectId": params[-1]}
        elif action_name == "closeobject":
            return {"action": "CloseObject", "objectId": params[-1]}
        elif action_name == "pickupobject":
            return {"action": "PickupObject", "objectId": params[-1]}
        elif action_name == "putobject":
            return {"action": "PutObject", "objectId": params[-2], "receptacleObjectId": params[-1]}
        # Add more mappings as needed
        
        raise ValueError(f"Unknown action: {action_name}")

    def map_plan2simulator(self, plan: List[Any]) -> List[Dict[str, Any]]:
        """Map PDDL plan to AI2THOR actions.
        
        Args:
            plan: List of PDDL actions
            
        Returns:
            List of AI2THOR action dictionaries
        """
        return [self.map_pddl2simulator(action) for action in plan]

    def step(self, action: Dict[str, Any]) -> Tuple[Dict, float, bool, bool, Dict]:
        """Execute an action in AI2THOR.
        
        Args:
            action: Action dictionary
            
        Returns:
            observation: New observation
            reward: Reward (0)
            terminated: Whether task is complete (False)
            truncated: Whether episode was truncated (False)
            info: Additional information
        """
        try:
            self.current_event = self.controller.step(action=action["action"], **{k: v for k, v in action.items() if k != "action"})
            
            if not self.current_event.metadata["lastActionSuccess"]:
                raise InfeasiblePlan(f"Action '{action}' failed: {self.current_event.metadata['errorMessage']}")
            
            observation = self.observation(self.current_event)
            
            return observation, 0.0, False, False, {}
            
        except Exception as e:
            raise InfeasiblePlan(f"Action '{action}' failed: {str(e)}")

    def observation(self, obs: Any) -> Dict:
        """Process raw observation from AI2THOR.
        
        Args:
            obs: AI2THOR Event object
            
        Returns:
            Formatted observation dictionary
        """
        # Extract relevant information from the event
        return {
            "objects": obs.metadata["objects"],
            "agent": obs.metadata["agent"],
            "camera_position": obs.metadata["cameraPosition"],
            "collided": obs.metadata["collided"],
            # Can add frame if needed, but it's heavy
            # "frame": obs.frame 
        }
