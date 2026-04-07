"""Habitat simulator implementation.

This simulator integrates the Habitat environment for embodied AI research.
Habitat provides high-performance 3D simulation with photorealistic scenes.

Required packages:
    - habitat-sim: Install with `conda install -c conda-forge -c aihabitat habitat-sim`
    - habitat-lab: Install with `pip install git+https://github.com/facebookresearch/habitat-lab.git`
    
Usage:
    To use this simulator, you need to have Habitat installed and scene datasets configured.
    See: https://aihabitat.org/
    
Scene Datasets:
    - Gibson: High-quality 3D scans of real indoor environments
    - HM3D: Habitat-Matterport 3D dataset
    - Replica: High-fidelity 3D reconstructions
"""

from typing import List, Tuple, Dict, Any, Optional, Union
import numpy as np
from .base_simulator import BaseSimulator
from .utils import InfeasiblePlan


class HabitatSimulator(BaseSimulator):
    """Habitat simulator with PDDL action mapping.
    
    This simulator wraps the Habitat-Sim environment and provides PDDL action
    translation and execution for navigation and manipulation tasks in photorealistic
    3D environments.
    """

    def __init__(
        self,
        scene_path: Optional[str] = None,
        scene_dataset: str = "gibson",
        scene_id: Union[str, int] = 0,
        width: int = 640,
        height: int = 480,
        enable_physics: bool = False,
        sensor_suite: List[str] = None,
        **kwargs
    ):
        """Initialize Habitat simulator.
        
        Args:
            scene_path: Direct path to a scene file (.glb). If None, uses scene_dataset and scene_id
            scene_dataset: Dataset name ('gibson', 'mp3d', 'replica', 'hm3d')
            scene_id: Scene identifier (index or name)
            width: RGB sensor width
            height: RGB sensor height
            enable_physics: Enable physics simulation
            sensor_suite: List of sensors to enable ('rgb', 'depth', 'semantic')
            **kwargs: Additional Habitat configuration parameters
        """
        try:
            import habitat_sim
            self.habitat_sim = habitat_sim
        except ImportError:
            raise ImportError(
                "Habitat-Sim not installed. Install with:\n"
                "  conda install -c conda-forge -c aihabitat habitat-sim\n"
                "Or for headless:\n"
                "  conda install -c conda-forge -c aihabitat habitat-sim headless\n"
                "See: https://github.com/facebookresearch/habitat-sim"
            )
        
        # Default sensors
        if sensor_suite is None:
            sensor_suite = ['rgb', 'depth']
        
        # Store configuration
        self.scene_path = scene_path
        self.scene_dataset = scene_dataset
        self.scene_id = scene_id
        self.width = width
        self.height = height
        self.enable_physics = enable_physics
        self.sensor_suite = sensor_suite
        self.kwargs = kwargs
        
        # Create simulator configuration
        self.sim_cfg = self._create_sim_config()
        
        # Initialize Habitat simulator
        try:
            self.sim = habitat_sim.Simulator(self.sim_cfg)
            super().__init__(self.sim)
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize Habitat simulator: {e}\n"
                "Make sure you have scene datasets configured.\n"
                "For Gibson dataset, set the path in scene_path parameter."
            )
        
        # Initialize agent
        self.agent = self.sim.initialize_agent(0)
        self.action_space = self._get_action_space()

    def setup(self, **kwargs) -> bool:
        """Setup the simulator.
        
        Habitat simulator is set up during initialization.
        """
        return True
        
    def _create_sim_config(self) -> Any:
        """Create Habitat simulator configuration."""
        import habitat_sim
        from habitat_sim.utils.common import quat_from_angle_axis
        
        # Backend configuration
        backend_cfg = habitat_sim.SimulatorConfiguration()
        
        # Set scene
        if self.scene_path:
            backend_cfg.scene_id = self.scene_path
        else:
            # Try to construct scene path from dataset and ID
            # This is a placeholder - user will need to provide actual paths
            backend_cfg.scene_id = self._get_scene_path()
        
        # Physics
        backend_cfg.enable_physics = self.enable_physics
        if self.enable_physics:
            backend_cfg.physics_config_file = "./data/default.physics_config.json"
        
        # GPU/CPU rendering
        backend_cfg.gpu_device_id = 0
        
        # Sensor specifications
        sensor_specs = []
        
        # RGB sensor
        if 'rgb' in self.sensor_suite:
            rgb_sensor_spec = habitat_sim.CameraSensorSpec()
            rgb_sensor_spec.uuid = "color_sensor"
            rgb_sensor_spec.sensor_type = habitat_sim.SensorType.COLOR
            rgb_sensor_spec.resolution = [self.height, self.width]
            rgb_sensor_spec.position = [0.0, 1.5, 0.0]  # 1.5m height (eye level)
            sensor_specs.append(rgb_sensor_spec)
        
        # Depth sensor
        if 'depth' in self.sensor_suite:
            depth_sensor_spec = habitat_sim.CameraSensorSpec()
            depth_sensor_spec.uuid = "depth_sensor"
            depth_sensor_spec.sensor_type = habitat_sim.SensorType.DEPTH
            depth_sensor_spec.resolution = [self.height, self.width]
            depth_sensor_spec.position = [0.0, 1.5, 0.0]
            sensor_specs.append(depth_sensor_spec)
        
        # Semantic sensor
        if 'semantic' in self.sensor_suite:
            semantic_sensor_spec = habitat_sim.CameraSensorSpec()
            semantic_sensor_spec.uuid = "semantic_sensor"
            semantic_sensor_spec.sensor_type = habitat_sim.SensorType.SEMANTIC
            semantic_sensor_spec.resolution = [self.height, self.width]
            semantic_sensor_spec.position = [0.0, 1.5, 0.0]
            sensor_specs.append(semantic_sensor_spec)
        
        # Agent configuration
        agent_cfg = habitat_sim.agent.AgentConfiguration()
        agent_cfg.sensor_specifications = sensor_specs
        agent_cfg.action_space = {
            "move_forward": habitat_sim.agent.ActionSpec(
                "move_forward", habitat_sim.agent.ActuationSpec(amount=0.25)
            ),
            "turn_left": habitat_sim.agent.ActionSpec(
                "turn_left", habitat_sim.agent.ActuationSpec(amount=10.0)
            ),
            "turn_right": habitat_sim.agent.ActionSpec(
                "turn_right", habitat_sim.agent.ActuationSpec(amount=10.0)
            ),
            "look_up": habitat_sim.agent.ActionSpec(
                "look_up", habitat_sim.agent.ActuationSpec(amount=10.0)
            ),
            "look_down": habitat_sim.agent.ActionSpec(
                "look_down", habitat_sim.agent.ActuationSpec(amount=10.0)
            ),
        }
        
        return habitat_sim.Configuration(backend_cfg, [agent_cfg])
    
    def _get_scene_path(self) -> str:
        """Construct scene path from dataset and scene ID.
        
        This method checks environment variables and common dataset locations
        to find scene files. Supports Replica, HM3D, Gibson, and Matterport3D datasets.
        """
        import os
        
        # Check for environment variables first
        dataset_env_vars = {
            'replica': 'REPLICA_DATASET_PATH',
            'hm3d': 'HM3D_DATASET_PATH',
            'gibson': 'GIBSON_DATASET_PATH',
            'mp3d': 'MP3D_DATASET_PATH',
            'matterport3d': 'MP3D_DATASET_PATH',
        }
        
        # Default dataset paths
        default_paths = {
            'replica': [
                os.path.expanduser('~/datasets/replica'),
                os.path.expanduser('~/data/habitat_scenes/replica'),
                './data/habitat_scenes/replica',
            ],
            'hm3d': [
                os.path.expanduser('~/datasets/hm3d'),
                os.path.expanduser('~/data/habitat_scenes/hm3d'),
                './data/habitat_scenes/hm3d',
            ],
            'gibson': [
                os.path.expanduser('~/datasets/gibson'),
                os.path.expanduser('~/data/gibson'),
                './data/gibson',
            ],
            'mp3d': [
                os.path.expanduser('~/datasets/mp3d'),
                os.path.expanduser('~/data/mp3d'),
                './data/habitat_scenes/mp3d',
            ],
            'matterport3d': [
                os.path.expanduser('~/datasets/mp3d'),
                os.path.expanduser('~/data/mp3d'),
            ],
        }
        
        dataset_key = self.scene_dataset.lower()
        
        # Try environment variable first
        if dataset_key in dataset_env_vars:
            env_path = os.getenv(dataset_env_vars[dataset_key])
            if env_path and os.path.exists(env_path):
                return self._find_scene_in_path(env_path)
        
        # Try default paths
        if dataset_key in default_paths:
            for path in default_paths[dataset_key]:
                if os.path.exists(path):
                    scene_path = self._find_scene_in_path(path)
                    if scene_path:
                        return scene_path
        
        # Provide helpful error message
        available_datasets = ', '.join(dataset_env_vars.keys())
        error_msg = (
            f"Scene dataset '{self.scene_dataset}' not found.\n"
            f"\n"
            f"Supported datasets: {available_datasets}\n"
            f"\n"
            f"Please either:\n"
            f"  1. Set environment variable: export {dataset_env_vars.get(dataset_key, 'DATASET_PATH')}=/path/to/dataset\n"
            f"  2. Place dataset in one of the default locations:\n"
        )
        
        if dataset_key in default_paths:
            for path in default_paths[dataset_key]:
                error_msg += f"     - {path}\n"
        
        error_msg += (
            f"  3. Use scene_path parameter directly:\n"
            f"     HabitatSimulator(scene_path='/path/to/scene.glb')\n"
            f"\n"
            f"To download datasets, run:\n"
            f"  ./scripts/download_habitat_datasets.sh\n"
            f"\n"
            f"Or use the dataset configuration helper:\n"
            f"  python scripts/habitat_dataset_config.py --list\n"
        )
        
        raise ValueError(error_msg)
    
    def _find_scene_in_path(self, dataset_path: str) -> Optional[str]:
        """Find a scene file in the dataset path.
        
        Args:
            dataset_path: Path to dataset directory
            
        Returns:
            Path to scene file, or None if not found
        """
        import os
        
        if not os.path.exists(dataset_path):
            return None
        
        # Collect all .glb files
        scene_files = []
        for root, dirs, files in os.walk(dataset_path):
            for file in files:
                if file.endswith('.glb'):
                    scene_files.append(os.path.join(root, file))
        
        if not scene_files:
            return None
        
        # Sort for consistency
        scene_files.sort()
        
        # Use scene_id to select file
        if isinstance(self.scene_id, int):
            if self.scene_id < len(scene_files):
                return scene_files[self.scene_id]
            else:
                raise ValueError(
                    f"Scene ID {self.scene_id} out of range. "
                    f"Found {len(scene_files)} scenes in {dataset_path}. "
                    f"Valid range: 0-{len(scene_files)-1}"
                )
        else:
            # scene_id is a filename
            scene_name = str(self.scene_id)
            if not scene_name.endswith('.glb'):
                scene_name += '.glb'
            
            # Search for matching filename
            for scene_file in scene_files:
                if os.path.basename(scene_file) == scene_name or scene_file.endswith(scene_name):
                    return scene_file
            
            # Not found
            raise ValueError(
                f"Scene '{scene_name}' not found in {dataset_path}. "
                f"Available scenes: {[os.path.basename(f) for f in scene_files[:5]]}..."
            )
        
        return None

    
    def _get_action_space(self) -> Dict[str, Any]:
        """Get available actions from Habitat agent."""
        return {
            'move_forward': 0,
            'turn_left': 1,
            'turn_right': 2,
            'look_up': 3,
            'look_down': 4,
        }

    def reset(self, seed: Optional[int] = None, **kwargs) -> Tuple[Dict, Dict]:
        """Reset the Habitat environment.
        
        Args:
            seed: Random seed for reproducibility
            **kwargs: Additional reset parameters
            
        Returns:
            observation: Initial observation
            info: Additional information dictionary
        """
        if seed is not None:
            self.sim.seed(seed)
        
        # Reset the simulator
        self.sim.reset()
        
        # Get initial observation
        obs = self.sim.get_sensor_observations()
        
        return self.observation(obs), {
            'scene_id': self.scene_path or f"{self.scene_dataset}_{self.scene_id}",
            'agent_state': self.agent.get_state()
        }

    def map_pddl2simulator(self, action: Any) -> str:
        """Map PDDL action to Habitat action.
        
        Args:
            action: PDDL action object with action.name and action.actual_parameters
            
        Returns:
            Habitat action name (string)
        """
        action_name = action.action.name.lower()
        
        # Map PDDL action names to Habitat actions
        action_mapping = {
            'moveforward': 'move_forward',
            'move_forward': 'move_forward',
            'forward': 'move_forward',
            'turnleft': 'turn_left',
            'turn_left': 'turn_left',
            'left': 'turn_left',
            'turnright': 'turn_right',
            'turn_right': 'turn_right',
            'right': 'turn_right',
            'lookup': 'look_up',
            'look_up': 'look_up',
            'lookdown': 'look_down',
            'look_down': 'look_down',
        }
        
        if action_name in action_mapping:
            return action_mapping[action_name]
        
        raise ValueError(f"Unknown action: {action_name}. Available actions: {list(action_mapping.keys())}")

    def map_plan2simulator(self, plan: List[Any]) -> List[str]:
        """Map PDDL plan to Habitat actions.
        
        Args:
            plan: List of PDDL actions
            
        Returns:
            List of Habitat action names
        """
        return [self.map_pddl2simulator(action) for action in plan]

    def step(self, action: str) -> Tuple[Dict, float, bool, bool, Dict]:
        """Execute an action in Habitat.
        
        Args:
            action: Action name (string from action_space)
            
        Returns:
            observation: New observation
            reward: Reward (0 for navigation)
            terminated: Whether task is complete (False)
            truncated: Whether episode was truncated (False)
            info: Additional information
        """
        try:
            # Execute action
            obs = self.sim.step(action)
            
            # Get agent state for info
            agent_state = self.agent.get_state()
            
            observation = self.observation(obs)
            
            # Check for collision
            collided = not self.sim.previous_step_collided
            
            return observation, 0.0, False, False, {
                'agent_state': agent_state,
                'collided': not collided,
                'action': action
            }
            
        except Exception as e:
            raise InfeasiblePlan(f"Action '{action}' failed: {str(e)}")

    def observation(self, obs: Any) -> Dict:
        """Process raw observation from Habitat.
        
        Args:
            obs: Habitat observation dictionary
            
        Returns:
            Formatted observation dictionary
        """
        observation = {}
        
        # Add sensor observations
        if 'color_sensor' in obs:
            observation['rgb'] = obs['color_sensor']
        
        if 'depth_sensor' in obs:
            observation['depth'] = obs['depth_sensor']
        
        if 'semantic_sensor' in obs:
            observation['semantic'] = obs['semantic_sensor']
        
        # Add agent state
        agent_state = self.agent.get_state()
        observation['agent_position'] = agent_state.position.tolist()
        observation['agent_rotation'] = agent_state.rotation.components.tolist()
        
        return observation
    
    def get_agent_position(self) -> np.ndarray:
        """Get current agent position."""
        return self.agent.get_state().position
    
    def get_agent_rotation(self) -> np.ndarray:
        """Get current agent rotation (quaternion)."""
        return self.agent.get_state().rotation.components
    
    def set_agent_state(self, position: np.ndarray, rotation: np.ndarray):
        """Set agent position and rotation.
        
        Args:
            position: 3D position [x, y, z]
            rotation: Quaternion rotation [x, y, z, w]
        """
        agent_state = self.agent.get_state()
        agent_state.position = position
        
        from habitat_sim.utils.common import quat_from_coeffs
        agent_state.rotation = quat_from_coeffs(rotation)
        
        self.agent.set_state(agent_state)
    
    def render(self, mode: str = 'rgb_array') -> np.ndarray:
        """Render the current view.
        
        Args:
            mode: Render mode ('rgb_array' or 'human')
            
        Returns:
            RGB image array
        """
        obs = self.sim.get_sensor_observations()
        
        if 'color_sensor' in obs:
            img = obs['color_sensor']
            
            if mode == 'human':
                # Display with matplotlib or similar
                try:
                    import matplotlib.pyplot as plt
                    plt.imshow(img)
                    plt.axis('off')
                    plt.show()
                except ImportError:
                    print("matplotlib not available for rendering")
            
            return img
        
        return np.zeros((self.height, self.width, 3), dtype=np.uint8)
    
    def close(self):
        """Close the simulator and free resources."""
        if hasattr(self, 'sim'):
            self.sim.close()
