# Habitat Setup Complete! ✅

## Installation Summary

**Status**: ✓ Successfully Installed  
**Date**: December 17, 2025  
**Environment**: `/DATA/CoSTL/.conda_env/`  
**Python**: 3.9.25  
**Habitat-sim**: 0.3.3  
**Size**: 2.7 GB

## What's Working

✓ Miniconda3 installed  
✓ Local conda environment created  
✓ habitat-sim 0.3.3 installed  
✓ All CoSTL dependencies (pddl, dotmap, gymnasium, numpy)  
✓ HabitatSimulator class ready  
✓ Alias `habitat-activate` configured  

## Quick Start

### Activate Environment
```bash
# Reload bash first (one time)
source ~/.bashrc

# Then use alias
habitat-activate

# Or full path
conda activate /DATA/CoSTL/.conda_env
```

### Test Installation
```bash
cd /DATA/CoSTL
habitat-activate
python test_habitat_only.py
```

### Download Datasets
```bash
habitat-activate
./scripts/download_habitat_datasets.sh
```

Start with **Replica** (Option 1) - free, ~10GB, no registration required.

### Use in Code
```python
# Activate: conda activate /DATA/CoSTL/.conda_env
import sys
sys.path.insert(0, '/DATA/CoSTL/src')

from costl.simulators.habitat_simulator import HabitatSimulator

sim = HabitatSimulator(
    scene_path="/path/to/scene.glb",
    sensor_suite=['rgb', 'depth']
)

obs, info = sim.reset()
obs, reward, done, truncated, info = sim.step('move_forward')
sim.close()
```

## Helper Scripts

```bash
# List scenes
python scripts/habitat_dataset_config.py --list

# Test with scene
python scripts/habitat_dataset_config.py --test --dataset replica --scene-id 0

# Download datasets
./scripts/download_habitat_datasets.sh
```

## Documentation

- `HABITAT_INSTALLATION_SUCCESS.md` - Detailed instructions
- `habitat_setup_guide.md` - Complete setup guide (artifacts dir)
- `habitat_quickstart.md` - Quick reference (artifacts dir)

## Next Steps

1. Download Replica dataset (~10 GB, free)
2. List available scenes  
3. Test with a real scene
4. Start building with Habitat!

---

**Important**: Import HabitatSimulator directly:  
`from costl.simulators.habitat_simulator import HabitatSimulator`

Not via package (which loads all simulators):  
~~`from costl.simulators import HabitatSimulator`~~
