#!/usr/bin/env python3
"""Simple test to verify Habitat setup is working."""

import sys
sys.path.insert(0, 'src')

print("Testing Habitat simulator setup...")
print("=" * 60)

# Test 1: Import habitat_sim
try:
    import habitat_sim
    print(f"✓ habitat_sim {habitat_sim.__version__} imported")
except ImportError as e:
    print(f"✗ Failed to import habitat_sim: {e}")
    sys.exit(1)

# Test 2: Import HabitatSimulator
try:
    from costl.simulators import HabitatSimulator
    print(f"✓ HabitatSimulator imported")
except ImportError as e:
    print(f"✗ Failed to import HabitatSimulator: {e}")
    sys.exit(1)

# Test 3: Check dependencies
try:
    import numpy, pddl, dotmap, gymnasium
    print(f"✓ All dependencies available")
except ImportError as e:
    print(f"✗ Missing dependency: {e}")
    sys.exit(1)

print("=" * 60)
print("✓ All tests passed!")
print()
print("Next steps:")
print("1. Download scene datasets:")
print("   ./scripts/download_habitat_datasets.sh")
print()  
print("2. List available scenes:")
print("   python scripts/habitat_dataset_config.py --list")
print()
print("3. Test with a scene:")
print("   python scripts/habitat_dataset_config.py --test --dataset replica --scene-id 0")
