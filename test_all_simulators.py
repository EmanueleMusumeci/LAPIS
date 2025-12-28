import os
import sys
import re
from typing import List, Any

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

# Mock PDDL Action for compatibility
class SimpleAction:
    def __init__(self, name, params):
        self.name = name
        self.actual_parameters = params

class PDDLActionWrapper:
    def __init__(self, name, params):
        self.action = SimpleAction(name, params)
        self.actual_parameters = params
    
    def __repr__(self):
        return f"({self.action.name} {' '.join(self.actual_parameters)})"

def parse_plan(file_path: str) -> List[PDDLActionWrapper]:
    """Parse a PDDL plan file into a list of action objects."""
    actions = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(';'):
                continue
            # Remove parentheses
            content = line.strip('()')
            parts = content.split()
            if not parts:
                continue
            name = parts[0]
            params = parts[1:]
            actions.append(PDDLActionWrapper(name, params))
    return actions

def test_babyai():
    print("\n" + "="*50)
    print("Testing BabyAI Simulator")
    print("="*50)
    
    try:
        import gymnasium as gym
        from costl.simulators import BabyAISimulator
        
        # Try to load a BabyAI environment
        # Note: This requires minigrid to be installed
        env_name = "BabyAI-MiniBossLevel-v0" 
        print(f"Loading environment: {env_name}")
        env = gym.make(env_name)
        sim = BabyAISimulator(env)
        
        print("Resetting simulator...")
        obs, info = sim.reset()
        print("Simulator reset successful.")
        
        # Load plan
        plan_path = "third-party/lexicon_neurips/domains/babyai/data/running_example/unconstrained_plan"
        if os.path.exists(plan_path):
            print(f"Loading plan from: {plan_path}")
            plan = parse_plan(plan_path)
            print(f"Plan loaded with {len(plan)} actions.")
            
            # Note: The plan might not be valid for the random seed of the environment
            # We will just try to map it to check the mapping logic
            print("Mapping plan to simulator actions...")
            try:
                sim_plan = sim.map_plan2simulator(plan)
                print(f"Successfully mapped {len(sim_plan)} actions.")
                print(f"First action: {sim_plan[0]}")
            except Exception as e:
                print(f"Mapping failed: {e}")
        else:
            print(f"Plan file not found: {plan_path}")
            
    except ImportError as e:
        print(f"Skipping BabyAI test: {e}")
    except Exception as e:
        print(f"BabyAI test failed: {e}")

def test_alfworld():
    print("\n" + "="*50)
    print("Testing AlfWorld Simulator")
    print("="*50)
    
    try:
        from costl.simulators import AlfWorldSimulator
        
        print("Initializing AlfWorld Simulator...")
        # This might fail if alfworld is not configured/downloaded
        sim = AlfWorldSimulator()
        
        print("Resetting simulator...")
        obs, info = sim.reset()
        print("Simulator reset successful.")
        
        # Load plan
        plan_path = "third-party/lexicon_neurips/domains/alfworld/data/data_1/1/unconstrained_plan"
        if os.path.exists(plan_path):
            print(f"Loading plan from: {plan_path}")
            plan = parse_plan(plan_path)
            print(f"Plan loaded with {len(plan)} actions.")
            
            print("Mapping plan to simulator actions...")
            try:
                sim_plan = sim.map_plan2simulator(plan)
                print(f"Successfully mapped {len(sim_plan)} actions.")
                print(f"First action: {sim_plan[0]}")
                
                # Try to execute first action if possible
                # print("Executing first action...")
                # sim.step(sim_plan[0])
                # print("Action executed.")
            except Exception as e:
                print(f"Mapping failed: {e}")
        else:
            print(f"Plan file not found: {plan_path}")
            
    except ImportError as e:
        print(f"Skipping AlfWorld test: {e}")
    except Exception as e:
        print(f"AlfWorld test failed: {e}")

def test_virtualhome():
    print("\n" + "="*50)
    print("Testing VirtualHome Simulator")
    print("="*50)
    
    try:
        from costl.simulators import VirtualHomeSimulator
        
        print("Initializing VirtualHome Simulator...")
        # Use demo mode if available or try default
        # Assuming demo=True might avoid Unity requirement if implemented, 
        # but based on INTEGRATION_GUIDE it seems Unity is required unless mocked.
        # Let's try to initialize and catch error
        try:
            sim = VirtualHomeSimulator(scene_id=0)
            print("Resetting simulator...")
            obs, info = sim.reset()
            print("Simulator reset successful.")
            
            # Simple test action
            action = PDDLActionWrapper("Walk", ["agent1", "Kitchen"])
            print(f"Testing action mapping for: {action}")
            mapped = sim.map_pddl2simulator(action)
            print(f"Mapped action: {mapped}")
            
        except Exception as e:
            print(f"VirtualHome initialization/run failed (expected if Unity not running): {e}")
            
    except ImportError as e:
        print(f"Skipping VirtualHome test: {e}")

def test_ai2thor():
    print("\n" + "="*50)
    print("Testing AI2THOR Simulator")
    print("="*50)
    
    try:
        from costl.simulators import AI2THORSimulator
        
        print("Initializing AI2THOR Simulator...")
        sim = AI2THORSimulator(width=300, height=300)
        
        print("Resetting simulator...")
        obs, info = sim.reset()
        print("Simulator reset successful.")
        
        # Simple test action
        action = PDDLActionWrapper("RotateRight", [])
        print(f"Testing action mapping for: {action}")
        mapped = sim.map_pddl2simulator(action)
        print(f"Mapped action: {mapped}")
        
        print("Executing action...")
        obs, _, _, _, _ = sim.step(mapped)
        print("Action executed successfully.")
        
    except ImportError as e:
        print(f"Skipping AI2THOR test: {e}")
    except Exception as e:
        print(f"AI2THOR test failed: {e}")

def test_habitat():
    print("\n" + "="*50)
    print("Testing Habitat Simulator")
    print("="*50)
    
    try:
        from costl.simulators import HabitatSimulator
        
        print("Initializing Habitat Simulator...")
        print("Note: This requires habitat-sim to be installed and scene datasets configured.")
        
        try:
            # Try to initialize with a test scene
            # User will need to provide actual scene path
            print("Attempting to create simulator (will fail gracefully if no scenes available)...")
            
            # This will fail without proper scene configuration, which is expected
            # The test is mainly to verify the import and basic structure works
            sim = HabitatSimulator(
                scene_dataset='gibson',
                scene_id=0,
                width=256,
                height=256
            )
            
            print("Resetting simulator...")
            obs, info = sim.reset()
            print("Simulator reset successful.")
            print(f"Observation keys: {obs.keys()}")
            
            # Test action mapping
            action = PDDLActionWrapper("MoveForward", [])
            print(f"Testing action mapping for: {action}")
            mapped = sim.map_pddl2simulator(action)
            print(f"Mapped action: {mapped}")
            
            print("Executing action...")
            obs, _, _, _, info = sim.step(mapped)
            print("Action executed successfully.")
            print(f"Agent position: {obs.get('agent_position', 'N/A')}")
            
            sim.close()
            
        except ValueError as e:
            # Expected error when scene datasets aren't configured
            print(f"Habitat initialization skipped (expected without scene datasets): {e}")
            print("\nTo fully test Habitat:")
            print("  1. Install habitat-sim: conda install -c conda-forge -c aihabitat habitat-sim")
            print("  2. Configure scene dataset path (e.g., Gibson dataset)")
            print("  3. Initialize with: HabitatSimulator(scene_path='/path/to/scene.glb')")
        except Exception as e:
            print(f"Habitat test failed: {e}")
            import traceback
            traceback.print_exc()
            
    except ImportError as e:
        print(f"Skipping Habitat test: {e}")
        print("\nTo install Habitat:")
        print("  conda install -c conda-forge -c aihabitat habitat-sim")
        print("  pip install git+https://github.com/facebookresearch/habitat-lab.git")


def main():
    print("Starting comprehensive simulator tests...")
    
    test_babyai()
    test_alfworld()
    test_virtualhome()
    test_ai2thor()
    test_habitat()
    
    print("\n" + "="*50)
    print("All tests completed.")
    print("="*50)
    
    # input("Press Enter to close...")

if __name__ == "__main__":
    main()

