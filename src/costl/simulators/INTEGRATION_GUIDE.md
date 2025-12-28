# Simulator Integration Guide

This document describes the missing components and setup required for full simulator integration.

## Summary of Implementation

✅ **Completed**:
- Base simulator interface (`simulators/base_simulator.py`)
- BabyAI simulator implementation (migrated and refactored)
- AlfWorld simulator implementation (new)
- VirtualHome simulator implementation (new)
- Common utilities and exception handling
- Documentation and README files

⚠️ **Missing Dependencies** (you need to provide/install):
1. **AlfWorld package**
2. **VirtualHome package**
3. Domain-specific integration files

## Required Repositories

### 1. AlfWorld

**Repository**: https://github.com/alfworld/alfworld

**Installation**:
```bash
# Initialize submodules
git submodule update --init --recursive

# Install the package
cd third-party/alfworld
pip install -e .
cd ../..

# Fix potential dependency issues
pip install --upgrade opencv-python numpy

# Download game files (required for environments)
alfworld-download
```

**Configuration**:
AlfWorld requires configuration files. After installation:
```bash
# Config will be created at ~/.alfworld/
# You may need to adjust paths in the config
```

### 2. VirtualHome

**Repository**: https://github.com/xavierpuigf/virtualhome

**Installation**:
```bash
# Initialize submodules
git submodule update --init --recursive

# Install Python package
cd third-party/virtualhome
pip install -e .
cd ../..
```

**Unity Simulator Setup**:
VirtualHome requires a Unity simulator executable:

1.  **Download and Install**:
    ```bash
    chmod +x scripts/download_virtualhome.sh
    ./scripts/download_virtualhome.sh
    ```

2.  **Run the Simulator**:
    - **With Graphics**:
      ```bash
      ./third-party/virtualhome/simulation/unity_simulator/linux_exec.v2.3.0.x86_64
      ```
    - **Headless**:
      Requires `xvfb`.
      ```bash
      xvfb-run --auto-servernum --server-args='-screen 0 640x480x24' \
        ./third-party/virtualhome/simulation/unity_simulator/linux_exec.v2.3.0.x86_64 \
        -batchmode -http-port 8080
      ```

Alternatively, use the demo mode (no Unity required):
```python
from simulators import VirtualHomeSimulator

# Use demo mode (limited functionality)
simulator = VirtualHomeSimulator(demo=True)
```

## Integration Steps

### Step 1: Install Base Requirements

```bash
# From CoSTL root directory
cd simulators
pip install -r requirements.txt
```

### Step 2: Install Optional Simulators

```bash
# For AlfWorld
cd ../third-party/alfworld && pip install -e . && cd ../..
alfworld-download

# For VirtualHome
cd ../third-party/virtualhome && pip install -e . && cd ../..
```

### Step 3: Set Environment Variables

```bash
# Add to your ~/.bashrc or environment
export COSTL_ROOT="/DATA/CoSTL"
export LEXICON="/DATA/CoSTL/third-party/lexicon_neurips"
```

### Step 4: Update Domain Files

The domain files need to be updated to use the new simulators. Example for AlfWorld:

```python
# In third-party/lexicon_neurips/domains/alfworld/alfworld.py

import sys
import os
sys.path.append(os.path.join(os.environ.get("COSTL_ROOT", "/DATA/CoSTL")))

from simulators import AlfWorldSimulator

class AlfWorld(LexiCon):
    def _initialize_env(self):
        self.env = AlfWorldSimulator()
    
    def is_feasible_low_level(self, plan):
        return self.env.is_feasible_plan(plan)
    
    def is_feasible_low_level_action(self, action):
        return self.env.is_feasible_action(action)
```

### Step 5: Test Simulators

```python
# Test AlfWorld
from simulators import AlfWorldSimulator

try:
    sim = AlfWorldSimulator()
    obs, info = sim.reset()
    print("AlfWorld simulator working!")
except ImportError as e:
    print(f"AlfWorld not available: {e}")

# Test VirtualHome
from simulators import VirtualHomeSimulator

try:
    sim = VirtualHomeSimulator(scene_id=0)
    obs, info = sim.reset()
    print("VirtualHome simulator working!")
except ImportError as e:
    print(f"VirtualHome not available: {e}")
```

## Current Status by Domain

### BabyAI ✅
- **Status**: Fully implemented and migrated
- **Simulator**: `BabyAISimulator`
- **Dependencies**: `minigrid`, `gymnasium` (already in lexicon requirements)
- **Action**: Ready to use

### AlfWorld ⚠️
- **Status**: Implementation complete, needs testing
- **Simulator**: `AlfWorldSimulator`
- **Missing**: AlfWorld package installation
- **Action**: Install alfworld package and test

### VirtualHome ⚠️
- **Status**: Implementation complete, needs testing
- **Simulator**: `VirtualHomeSimulator`
- **Missing**: VirtualHome package + Unity simulator
- **Action**: Install virtualhome package, download Unity simulator

### Blocksworld, Sokoban, Logistics ❌
- **Status**: No simulator implemented
- **Reason**: These domains typically use symbolic planning without low-level simulation
- **Action**: Simulation may not be needed, or simple symbolic validation is sufficient

## What I Cannot Provide

I cannot directly provide or install:

1. **AlfWorld Package**: You need to clone and install from GitHub
   - Reason: It's a separate package with its own dependencies
   - Action: Follow installation steps above

2. **VirtualHome Unity Simulator**: You need to download the Unity executable
   - Reason: It's a large binary file (~500MB+)
   - Action: Download from VirtualHome releases page

3. **AlfWorld Game Data**: Downloaded via `alfworld-download` command
   - Reason: Large dataset of interactive fiction games
   - Action: Run `alfworld-download` after installing alfworld

4. **Updated Domain Integration Files**: I created example but you may need to customize
   - Reason: Depends on your specific lexicon configuration
   - Action: Update domain files based on your needs

## Architecture Overview

```
CoSTL/
├── simulators/                    # New simulator directory ✅
│   ├── __init__.py               # Package init
│   ├── base_simulator.py         # Abstract base class
│   ├── babyai_simulator.py       # BabyAI implementation
│   ├── alfworld_simulator.py     # AlfWorld implementation
│   ├── virtualhome_simulator.py  # VirtualHome implementation
│   ├── utils.py                  # Common utilities
│   ├── requirements.txt          # Dependencies
│   └── README.md                 # Documentation
│
├── domains/                       # Domain-specific code (optional)
│   └── alfworld/
│       └── alfworld_updated.py   # Example updated integration
│
└── third-party/lexicon_neurips/
    └── domains/                   # Original lexicon domains
        ├── alfworld/
        │   └── alfworld.py       # Update to use new simulator
        ├── babyai/
        │   └── babyai.py         # Update to use new simulator
        └── ...
```

## Testing Your Setup

Create a test script:

```python
# test_simulators.py

import os
os.environ['COSTL_ROOT'] = '/DATA/CoSTL'

print("Testing simulators...\n")

# Test 1: BabyAI (should work if minigrid installed)
print("1. Testing BabyAI...")
try:
    from simulators import BabyAISimulator
    import gymnasium as gym
    env = gym.make("BabyAI-MiniBossLevel-v0")
    sim = BabyAISimulator(env)
    print("   ✅ BabyAI simulator available")
except Exception as e:
    print(f"   ❌ BabyAI simulator failed: {e}")

# Test 2: AlfWorld
print("\n2. Testing AlfWorld...")
try:
    from simulators import AlfWorldSimulator
    sim = AlfWorldSimulator()
    print("   ✅ AlfWorld simulator available")
except ImportError as e:
    print(f"   ⚠️  AlfWorld not installed: {e}")
except Exception as e:
    print(f"   ❌ AlfWorld simulator failed: {e}")

# Test 3: VirtualHome
print("\n3. Testing VirtualHome...")
try:
    from simulators import VirtualHomeSimulator
    sim = VirtualHomeSimulator(scene_id=0)
    print("   ✅ VirtualHome simulator available")
except ImportError as e:
    print(f"   ⚠️  VirtualHome not installed: {e}")
except Exception as e:
    print(f"   ❌ VirtualHome simulator failed: {e}")

print("\nDone!")
```

Run with:
```bash
python test_simulators.py
```

## Next Steps

1. **Install missing packages** (AlfWorld, VirtualHome)
2. **Test each simulator** independently
3. **Update domain integration files** in lexicon
4. **Run end-to-end tests** with actual planning tasks
5. **Report any issues** or missing functionality

## Additional Notes

- The simulators are designed to be modular and independent
- You can use BabyAI simulator immediately (if minigrid installed)
- AlfWorld and VirtualHome require external packages
- All simulators follow the same interface (BaseSimulator)
- Error handling is included to gracefully handle missing dependencies

## Contact & Support

If you encounter issues:
1. Check that all dependencies are installed
2. Verify environment variables are set correctly
3. Ensure Unity simulator is running (for VirtualHome)
4. Check the simulator README for domain-specific requirements
