import argparse
import sys
import os
import logging
from pathlib import Path
from dataclasses import dataclass

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

from src.costl.simulators.blocksworld_simulator import BlocksworldSimulator
from src.costl.simulators.babyai_simulator import BabyAISimulator
from src.costl.simulators.scenario import Scenario
from src.costl.simulators.utils import Action

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("simulate_plan")

def parse_plan_to_actions(plan_content):
    """Parse plan content into a list of Action objects."""
    actions = []
    for line in plan_content.splitlines():
        line = line.strip()
        if not line or line.startswith(';'):
            continue
        # Remove parentheses
        content = line.replace('(', '').replace(')', '')
        parts = content.split()
        if not parts:
            continue
        
        action_name = parts[0]
        params = parts[1:]
        
        @dataclass
        class PDDLActionWrapper:
            name: str
        
        @dataclass
        class PDDLActionInstance:
            action: PDDLActionWrapper
            actual_parameters: list
        
        action_obj = PDDLActionInstance(
            action=PDDLActionWrapper(name=action_name),
            actual_parameters=params
        )
        
        actions.append(action_obj)
        
    return actions

def main():
    parser = argparse.ArgumentParser(description="Simulate a PDDL plan.")
    parser.add_argument("--domain", required=True, help="Domain name (e.g., blocksworld, babyai)")
    parser.add_argument("--problem", required=True, help="Path to problem PDDL file")
    parser.add_argument("--plan", required=True, help="Path to plan file")
    parser.add_argument("--visualize", action="store_true", help="Enable visualization")
    
    args = parser.parse_args()
    
    # Instantiate simulator
    simulator = None
    if "blocksworld" in args.domain.lower():
        # For Blocksworld, we might need to parse the problem file to get initial state
        # The BlocksworldSimulator currently generates problems.
        # To support loading an existing problem PDDL, we might need to use UP's PDDL reader.
        # But BlocksworldSimulator uses SequentialSimulator(problem).
        # We need to load the problem from PDDL.
        
        from unified_planning.io import PDDLReader
        reader = PDDLReader()
        # We need domain PDDL too if we want to parse problem PDDL
        # Assuming domain PDDL is in the same folder or we can infer it
        problem_path = Path(args.problem)
        domain_path = problem_path.parent / "domain.pddl"
        
        if not domain_path.exists():
            logger.error(f"Domain file not found at {domain_path}")
            return

        try:
            problem = reader.parse_problem(str(domain_path), str(problem_path))
        except Exception as e:
            logger.error(f"Failed to parse PDDL: {e}")
            return

        simulator = BlocksworldSimulator()
        # Override internal problem and simulator
        from unified_planning.shortcuts import SequentialSimulator
        simulator.problem = problem
        simulator.simulator = SequentialSimulator(problem)
        simulator.current_state = simulator.simulator.get_initial_state()
        
    elif "babyai" in args.domain.lower():
        # BabyAI requires Gym env.
        # If we are running standalone, we might be able to create it if we know the level.
        # But here we only have PDDL.
        # If we can't create the env, we can't visualize or compute accurate costs.
        logger.warning("BabyAI simulation requires Gym environment. Visualization might be limited.")
        # Try to init without env? BaseSimulator needs env.
        # We can pass a mock env?
        class MockEnv:
            def reset(self, **kwargs): return {}, {}
            def step(self, action): return {}, 0, False, False, {}
            @property
            def unwrapped(self): return self
            
        simulator = BabyAISimulator(MockEnv())
        
    else:
        logger.error(f"Unknown domain: {args.domain}")
        return

    # Parse plan
    with open(args.plan, 'r') as f:
        plan_content = f.read()
    
    actions = parse_plan_to_actions(plan_content)
    
    total_cost = 0.0
    
    print(f"Simulating plan for {args.domain}...")
    
    if args.visualize and hasattr(simulator, 'render'):
        simulator.render()
        
    for i, action in enumerate(actions):
        print(f"Step {i+1}: {action.action.name} {action.actual_parameters}")
        
        # Compute cost
        cost = simulator.scenario.compute_cost(action, simulator.current_state if hasattr(simulator, 'current_state') else None)
        total_cost += cost
        
        # Execute step
        try:
            # map_pddl2simulator might be needed before step
            # But simulator.step usually expects simulator-specific action
            # BlocksworldSimulator.step expects UP ActionInstance.
            # BabyAISimulator.step expects (action, target).
            
            if "blocksworld" in args.domain.lower():
                # We need to convert our dummy action to UP ActionInstance
                # This is tricky without the UP Action object from the problem.
                # We need to find the action in the problem.
                up_action = None
                for a in simulator.problem.actions:
                    if a.name.lower() == action.action.name.lower():
                        # Match parameters
                        # We need to convert string params to Objects
                        params = []
                        for p_name in action.actual_parameters:
                            obj = simulator.problem.object(p_name)
                            params.append(obj)
                        up_action = a(*params)
                        break
                
                if up_action:
                    simulator.step(up_action)
                else:
                    logger.error(f"Action {action.action.name} not found in problem.")
            
            elif "babyai" in args.domain.lower():
                # BabyAI step expects mapped action
                mapped = simulator.map_pddl2simulator(action)
                simulator.step(mapped)
                
        except Exception as e:
            logger.error(f"Step failed: {e}")
            
        if args.visualize and hasattr(simulator, 'render'):
            simulator.render()
            
    print(f"Total Cost: {total_cost}")

if __name__ == "__main__":
    main()
