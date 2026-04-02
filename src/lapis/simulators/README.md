# Simulators

This directory contains simulator implementations for various planning domains used in LAPIS.

## Overview

Each simulator provides a consistent interface for:
- Mapping PDDL actions to domain-specific actions
- Executing actions in the simulated environment
- Validating plan feasibility
- Tracking environment state

## Available Simulators

### 1. BabyAI Simulator (`babyai_simulator.py`)

Simulates a grid-based multi-room environment with objects, doors, and manipulation tasks.

**Status**: ✅ Fully implemented (migrated from lexicon)

**Dependencies**:
```bash
pip install minigrid gymnasium
```

**Usage**:
```python
from simulators import BabyAISimulator
import gymnasium as gym

env = gym.make("BabyAI-MiniBossLevel-v0")
simulator = BabyAISimulator(env)
obs, info = simulator.reset(seed=42)
```

### 2. AlfWorld Simulator (`alfworld_simulator.py`)

Simulates household tasks in text-based interactive fiction environments based on ALFRED.

**Status**: ✅ Implemented (needs testing with AlfWorld package)

**Dependencies**:
```bash
pip install alfworld
```

**Repository**: https://github.com/alfworld/alfworld

**Usage**:
```python
from simulators import AlfWorldSimulator

simulator = AlfWorldSimulator(env_name="AlfWorld-v2")
obs, info = simulator.reset()
```

**Actions**:
- `goto <location>`: Navigate to location
- `open/close <receptacle>`: Manipulate containers
- `take/put <object>`: Pick up or place objects
- `clean/heat/cool <object>`: Manipulate object states
- `slice <object>`: Cut objects
- `toggle <object>`: Turn lights on/off

### 3. VirtualHome Simulator (`virtualhome_simulator.py`)

Simulates detailed household activities with realistic physics and multi-agent support.

**Status**: ✅ Implemented (needs testing with VirtualHome package)

**Dependencies**:
```bash
git clone https://github.com/xavierpuigf/virtualhome.git
cd virtualhome
pip install -e .
```

**Repository**: https://github.com/xavierpuigf/virtualhome

**Additional Setup**:
- Download Unity simulator from VirtualHome releases
- Run Unity executable before using simulator

**Usage**:
```python
from simulators import VirtualHomeSimulator

simulator = VirtualHomeSimulator(
    scene_id=0,
    num_agents=1,
    rendering=False,
    port="8080"
)
obs, info = simulator.reset()
```

**Actions**:
- `[Walk] <object>`: Navigate to object
- `[Grab] <object>`: Pick up object
- `[Put] <object> <container>`: Place object
- `[Open/Close] <object>`: Manipulate doors/containers
- `[SwitchOn/Off] <object>`: Control appliances
- `[Sit] <object>`: Sit on furniture
- And many more...

## Architecture

All simulators inherit from `BaseSimulator` which defines the interface:

```python
class BaseSimulator(ABC):
    def reset(self, seed, **kwargs) -> Tuple[Dict, Dict]
    def map_pddl2simulator(self, action) -> Any
    def map_plan2simulator(self, plan) -> List[Any]
    def step(self, action) -> Tuple[Dict, float, bool, bool, Dict]
    def observation(self, obs) -> Dict
    def is_feasible_plan(self, plan) -> bool
    def is_feasible_action(self, action) -> bool
```

## Integration with Lexicon

The simulators integrate with the lexicon framework through domain-specific classes:

```python
# In domains/alfworld/alfworld.py
from simulators import AlfWorldSimulator

class AlfWorld(LexiCon):
    def _initialize_env(self):
        self.env = AlfWorldSimulator()
    
    def is_feasible_low_level(self, plan):
        return self.env.is_feasible_plan(plan)
```

## Adding New Simulators

To add a new simulator:

1. Create a new file `<domain>_simulator.py`
2. Inherit from `BaseSimulator`
3. Implement required methods:
   - `reset()`: Initialize environment
   - `map_pddl2simulator()`: Map PDDL action to simulator format
   - `map_plan2simulator()`: Map PDDL plan to simulator format
   - `step()`: Execute action
   - `observation()`: Process observations
4. Add to `__init__.py`
5. Update this README

## Common Utilities

The `utils.py` module provides common classes:
- `InfeasiblePlan`: Exception for plan execution failures
- `Object`: Represents objects in environments
- `Door`: Represents doors/passages
- `Room`: Represents rooms/locations
- `Action`: Represents actions with parameters

## Testing

Each simulator should be tested independently:

```python
# Test basic functionality
simulator = YourSimulator()
obs, info = simulator.reset(seed=42)

# Test action mapping
pddl_action = ...
sim_action = simulator.map_pddl2simulator(pddl_action)

# Test execution
obs, reward, done, truncated, info = simulator.step(sim_action)

# Test plan validation
plan = [...]
is_valid = simulator.is_feasible_plan(plan)
```

## Known Issues

1. **BabyAI**: Type hints need refinement for gymnasium compatibility
2. **AlfWorld**: Requires AlfWorld package and environment setup
3. **VirtualHome**: Requires Unity simulator running on specified port

## Future Work

- [ ] Add Sokoban simulator
- [ ] Add Logistics simulator  
- [ ] Add Blocksworld simulator (if simulation needed)
- [ ] Improve error handling and recovery
- [ ] Add visualization utilities
- [ ] Add performance benchmarks
- [ ] Create unified test suite

## References

- BabyAI/MiniGrid: https://github.com/Farama-Foundation/Minigrid
- AlfWorld: https://github.com/alfworld/alfworld
- VirtualHome: https://github.com/xavierpuigf/virtualhome
