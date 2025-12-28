#!/usr/bin/env python3
"""Test only Habitat simulator (avoiding other simulator dependencies)."""

import sys
sys.path.insert(0, 'src')

print("Testing Habitat Simulator Standalone...")
print("=" * 60)

# Test 1: Import habitat_sim
try:
    import habitat_sim
    print(f"✓ habitat_sim {habitat_sim.__version__} imported")
except ImportError as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

# Test 2: Import HabitatSimulator directly (not via __init__.py)
try:
    from costl.simulators.habitat_simulator import HabitatSimulator
    print(f"✓ HabitatSimulator class available")
except ImportError as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

# Test 3: Check it inherits from BaseSimulator
try:
    from costl.simulators.base_simulator import BaseSimulator
    assert issubclass(HabitatSimulator, BaseSimulator)
    print(f"✓ HabitatSimulator correctly inherits from BaseSimulator")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

# Test 4: Check required methods exist
required_methods = ['reset', 'step', 'observation', 'map_pddl2simulator', 'close']
for method in required_methods:
    if not hasattr(HabitatSimulator, method):
        print(f"✗ Missing required method: {method}")
        sys.exit(1)
print(f"✓ All required methods present")

print("=" * 60)
print("✓ Habitat simulator is ready to use!")
print()
print("Note: To use HabitatSimulator, import directly:")
print("  from costl.simulators.habitat_simulator import HabitatSimulator")
print()
print("Next: Download scene datasets and test with real scenes")
