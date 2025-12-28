# HABITAT INSTALLATION SUCCESS! 🎉

## ✅ Installation Complete

**Date**: December 16, 2025
**Environment**: `/DATA/CoSTL/.conda_env/`
**Python Version**: 3.9.25
**Habitat-sim Version**: 0.3.3

## What Was Installed

- ✓ Miniconda3 at `/home/xps/miniconda3`
- ✓ Local conda environment at `/DATA/CoSTL/.conda_env`
- ✓ habitat-sim 0.3.3
- ✓ All required dependencies (numpy, pillow, scipy, matplotlib, etc.)
- ✓ Convenience alias `habitat-activate` added to ~/.bashrc

## Quick Start

### Activate Environment
```bash
# Option 1: Full path
conda activate /DATA/CoSTL/.conda_env

# Option 2: Use alias (after reloading bash)
source ~/.bashrc
habitat-activate
```

### Test Installation
```bash
cd /DATA/CoSTL
conda activate /DATA/CoSTL/.conda_env

# Test habitat-sim
python -c "import habitat_sim; print(f'✓ habitat-sim {habitat_sim.__version__}')"

# Test HabitatSimulator
python -c "import sys; sys.path.insert(0, 'src'); from costl.simulators import HabitatSimulator; print('✓ HabitatSimulator OK')"
```

## Next Steps

### 1. Download Scene Datasets

```bash
cd /DATA/CoSTL
conda activate /DATA/CoSTL/.conda_env

# Run interactive download script
./scripts/download_habitat_datasets.sh
```

**Recommended**: Start with Replica (Option 1) - it's free and doesn't require registration.

### 2. List Available Scenes

```bash
conda activate /DATA/CoSTL/.conda_env
python scripts/habitat_dataset_config.py --list
```

### 3. Test with a Scene

```bash
conda activate /DATA/CoSTL/.conda_env
python scripts/habitat_dataset_config.py --test --dataset replica --scene-id 0
```

### 4. Use in Your Code

```python
# First: conda activate /DATA/CoSTL/.conda_env
import sys
sys.path.insert(0, '/DATA/CoSTL/src')

from costl.simulators import HabitatSimulator

# Initialize with a scene
sim = HabitatSimulator(
    scene_path="/path/to/scene.glb",  # Or use dataset auto-discovery
    sensor_suite=['rgb', 'depth']
)

# Use the simulator  
obs, info = sim.reset()
obs, reward, done, truncated, info = sim.step('move_forward')
sim.close()
```

## Troubleshooting

### Module not found errors?
Add the src directory to Python path:
```python
import sys
sys.path.insert(0, '/DATA/CoSTL/src')
```

Or set PYTHONPATH:
```bash
export PYTHONPATH=/DATA/CoSTL/src:$PYTHONPATH
```

### Conda activate not working?
```bash
source ~/miniconda3/bin/activate
conda activate /DATA/CoSTL/.conda_env
```

## Important Notes

- **Python Version**: habitat-sim 0.3.3 requires Python 3.9 (not 3.10+)
- **Environment Location**: Project-local at `/DATA/CoSTL/.conda_env/`
- **Size**: Environment is approximately 1-2 GB
- **Git**: Already added to `.gitignore`

## Documentation

All guides available in artifact directory:
- `habitat_setup_guide.md` - Complete setup guide
- `habitat_quickstart.md` - Quick command reference
- `HABITAT_INTEGRATION_SUMMARY.md` - Integration summary

## Support

If you encounter issues:
1. Check `habitat_setup_guide.md` troubleshooting section
2. Verify environment: `conda env list`
3. Test imports: `python -c "import habitat_sim"`
4. Check Python path when importing costl modules

---

**You're all set!** Download some scenes and start using Habitat simulator! 🚀
