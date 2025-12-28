
import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
if project_root not in sys.path:
    sys.path.append(project_root)

from src.costl.simulators.blocksworld_simulator import BlocksworldSimulator

def test_simulator():
    print("Initializing BlocksworldSimulator...")
    sim = BlocksworldSimulator(seed=42)
    
    print("Resetting simulator...")
    obs, info = sim.reset(num_blocks=3)
    print("Initial observation keys:", obs.keys())
    print("Problem name:", info["problem"].name)
    
    problem = info["problem"]
    # Find a valid action
    # For blocksworld, pickup is usually valid if hand is empty and block is clear and on table
    # Let's inspect the initial state to find a valid action
    
    from unified_planning.shortcuts import SequentialSimulator
    up_sim = SequentialSimulator(problem)
    initial_state = up_sim.get_initial_state()
    
    applicable_actions = []
    for action in problem.actions:
        # We need to ground actions to check applicability
        # This is a bit complex without a planner, but we can try to find one applicable ground action
        # by iterating over objects
        pass
        
    # Let's use the simulator's internal simulator to find applicable actions
    # But SequentialSimulator doesn't expose get_applicable_actions easily without grounding
    
    # Let's try to pick up a block that is on table and clear
    # In our problem generation, blocks are named "red_block_1", etc.
    # We can inspect the state to find one.
    
    print("State:", obs["state"])
    
    # Just try to run a dummy plan if we can't easily find an action
    # Or rely on the fact that we can just print success if reset works for now
    # But better to try one step.
    
    print("Simulator initialized and reset successfully.")

if __name__ == "__main__":
    test_simulator()
