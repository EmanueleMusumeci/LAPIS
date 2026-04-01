# CoSTL — Quick start

A compact guide to get you started with the LexiCon benchmark and tools.

Quick install
-------------
1) Automated (recommended): from repository root

```bash
chmod +x setup_lexicon_env.sh
./setup_lexicon_env.sh
```

2) Conda (better for heavy binaries):

```bash
cd third-party/lexicon_neurips
conda env create -f environment.yml
conda activate lexiconenv
mkdir -p intermediate_sas
```

Two quick commands
------------------
- Generate problems: `python3 third-party/lexicon_neurips/generate_benchmark.py blocksworld 100 1 2`
- Verify a stored plan: `python3 third-party/lexicon_neurips/verify_plan.py blocksworld 2 100 o3`

Notes
-----
- Ensure enough disk space (large pip wheels like `torch` can require hundreds of MB); prefer conda if possible.
- For evaluation with real LLMs export API keys: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`.
- If you want a minimal, fast setup for generation/verification only, remove heavy packages (e.g., `torch` and `up-*` planners) from `requirements-lexicon.txt` before installing.

Manual pip install (system deps)
-------------------------------
If you prefer a manual pip-based setup rather than the helper script or conda, first install the common system packages required to build Python extensions and planners. On Debian/Ubuntu these commands are a good starting point:

```bash
sudo apt-get update
sudo apt-get install -y build-essential python3-venv python3-dev \
	git wget curl cmake pkg-config libssl-dev libffi-dev zlib1g-dev \
	libbz2-dev libreadline-dev libsqlite3-dev libncurses5-dev libncursesw5-dev \
	liblzma-dev libgdbm-dev
```

Notes:
- If you need GPU support for `torch` install NVIDIA drivers and the appropriate CUDA toolkit separately (follow PyTorch/CUDA docs). GPU/CUDA setup is system-specific and not managed by this repo.
- Some planner backends may need extra system packages — check `third-party/lexicon_neurips/environment.yml` for hints.

Create a venv and install via pip (example):

```bash
# from repository root
python3 -m venv .venv
source .venv/bin/activate
# optional: keep pip cache inside the repo to avoid filling /tmp
export PIP_CACHE_DIR="$PWD/.cache_lexicon/pip"
mkdir -p "$PIP_CACHE_DIR"
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements-lexicon.txt

# initialize submodules and prepare intermediate folder if needed
git submodule update --init --recursive
mkdir -p third-party/lexicon_neurips/intermediate_sas
```

This installs the pip requirements listed at the repository root. If `pip install` fails due to very large wheels (for example `torch`), consider:
- using conda with `third-party/lexicon_neurips/environment.yml` (recommended for heavy binary packages), or
- editing `requirements-lexicon.txt` to remove the heaviest packages, install the rest, and add heavy binaries later when you have disk space or a prepared system-level CUDA runtime.

More details and full examples are in `third-party/lexicon_neurips/README.md` and the `setup_lexicon_env.sh` helper. Ask me to expand any section.
# CoSTL-CommonSense-enhanced-Temporal-Logics-planning
LLM-based temporal logics planner for commonsense based formal domain generation and refinement with temporal constraints and self-supervised fluent grounding

Simulator Installation
----------------------
To fully enable AlfWorld and VirtualHome simulators, you need to install their respective packages and dependencies.

### 1. AlfWorld

**Repository**: [https://github.com/alfworld/alfworld](https://github.com/alfworld/alfworld)

**Installation**:
```bash
# Initialize submodules if not already done
git submodule update --init --recursive

# Install the package
cd third-party/alfworld
pip install -e .
cd ../..

# Fix potential dependency issues
pip install --upgrade opencv-python numpy

# Download game data (required)
alfworld-download
```
*Note: This downloads a large dataset of interactive fiction games.*

**Configuration**:
The configuration will be created at `~/.alfworld/`. You may need to adjust paths in `~/.alfworld/alfworld.config` if needed.

### 2. VirtualHome

**Repository**: [https://github.com/xavierpuigf/virtualhome](https://github.com/xavierpuigf/virtualhome)

**Installation**:
```bash
# Initialize submodules if not already done
git submodule update --init --recursive

# Install the package
cd third-party/virtualhome
pip install -e .
cd ../..
```

**Unity Simulator Setup (Required)**:
VirtualHome requires a Unity executable to simulate the environment.

1.  **Download and Install**:
    We provide a helper script to download and set up the simulator automatically:
    ```bash
    chmod +x scripts/download_virtualhome.sh
    ./scripts/download_virtualhome.sh
    ```

2.  **Run the Simulator**:
    - **With Graphics**:
      ```bash
      ./third-party/virtualhome/simulation/unity_simulator/linux_exec.v2.3.0.x86_64
      ```
    - **Headless (Server/Cloud)**:
      Requires `xvfb` installed (`sudo apt-get install xvfb`).
      ```bash
      xvfb-run --auto-servernum --server-args='-screen 0 640x480x24' \
        ./third-party/virtualhome/simulation/unity_simulator/linux_exec.v2.3.0.x86_64 \
        -batchmode -http-port 8080
      ```
    
3.  **Keep it running** in the background while using the VirtualHome simulator.

### 3. Habitat

**Repository**: [https://github.com/facebookresearch/habitat-sim](https://github.com/facebookresearch/habitat-sim)

**Description**: Habitat is a high-performance 3D simulator for embodied AI research. It provides photorealistic 3D environments with RGB-D sensors, physics simulation, and supports various scene datasets including Gibson, HM3D, Matterport3D, and Replica.

**Installation**:

```bash
# Recommended: Install via conda for better binary compatibility
conda install -c conda-forge -c aihabitat habitat-sim

# Alternative: For headless mode (servers/cloud)
conda install -c conda-forge -c aihabitat habitat-sim headless

# Install habitat-lab (optional, for higher-level tasks)
pip install git+https://github.com/facebookresearch/habitat-lab.git
```

**Scene Dataset Configuration**:

Habitat requires 3D scene datasets to function. We provide automated scripts to help you download and configure datasets.

#### Automated Setup (Recommended):

```bash
# Interactive download and configuration script
./scripts/download_habitat_datasets.sh
```

This script provides options to:
- Download Replica dataset (~10 GB, free, no registration)
- Download HM3D dataset (requires Matterport API token)
- Configure all dataset paths automatically
- Test your configuration

#### Dataset Helper Tool:

```bash
# List all available scenes
python scripts/habitat_dataset_config.py --list

# List scenes from specific dataset
python scripts/habitat_dataset_config.py --list --dataset replica

# Test simulator with a scene
python scripts/habitat_dataset_config.py --test --dataset replica --scene-id 0

# Create configuration file
python scripts/habitat_dataset_config.py --create-config
```

#### Manual Configuration:

1.  **Replica Dataset** (18 scenes, ~10 GB, free):
    ```bash
    cd data
    git clone https://github.com/facebookresearch/Replica-Dataset.git replica
   cd replica && ./download.sh
    export REPLICA_DATASET_PATH=$(pwd)
    ```

2.  **HM3D Dataset** (1000 scenes, requires Matterport API token):
    - Get API token from: https://my.matterport.com/settings/account/devtools
    - Download using habitat_sim tools:
    ```bash
    python -m habitat_sim.utils.datasets_download \
        --username YOUR_TOKEN_ID \
        --password YOUR_TOKEN_SECRET \
        --uids hm3d_minival \
        --data-path ./data/hm3d
    export HM3D_DATASET_PATH=$(pwd)/data/hm3d
    ```

3.  **Gibson Dataset** (if you have access):
    ```bash
    export GIBSON_DATASET_PATH=/path/to/your/gibson/dataset
    ```

#### Environment Variables:

The simulator automatically checks these environment variables:
- `REPLICA_DATASET_PATH` - Path to Replica dataset
- `HM3D_DATASET_PATH` - Path to HM3D dataset
- `GIBSON_DATASET_PATH` - Path to Gibson dataset

To persist these settings, add them to your `~/.bashrc` or source the generated config file:
```bash
source /DATA/CoSTL/.habitat_datasets.conf
```


**Quick Test**:
```python
from costl.simulators import HabitatSimulator

# Initialize with your scene file
sim = HabitatSimulator(
    scene_path="/path/to/your/scene.glb",
    width=640,
    height=480,
    sensor_suite=['rgb', 'depth']
)

# Reset and get initial observation
obs, info = sim.reset()
print(f"RGB shape: {obs['rgb'].shape}")
print(f"Agent position: {obs['agent_position']}")

# Execute navigation actions
obs, reward, done, truncated, info = sim.step('move_forward')
```

**Features**:
- High-performance rendering (10,000+ FPS)
- RGB-D sensors
- Physics simulation (optional)
- Multiple scene datasets support
- Navigation and manipulation tasks
- Configurable agent sensors and controls


### Verification
After installation, run the test script to verify all simulators:
```bash
python test_all_simulators.py
```

## Benchmark Analysis

### Known Issues & Failures

#### Problem 102: State Hallucination in Refinement
In `data_1/102`, the pipeline failed during Ground Truth execution due to an **unsatisfied precondition**. 

**Analysis:**
- **The Issue**: During Subgoal 5, the agent was still holding a block from the previous subgoal.
- **LLM "Cheating"**: The PDDL refinement loop (LLM) encountered a failure because the physical state was "unsolvable" for the desired goal from that starting position. Instead of fixing the plan sequence, the LLM **hallucinated a new initial state** in the PDDL problem file (e.g., teleporting blocks to the table to clear the hand).
- **Consequence**: The internal planner found a "valid" plan for this imaginary state, but the real Ground Truth simulator crashed immediately when the first action (`unstack`) was not applicable in the actual world state.

**Status**: Root cause identified. Requires "Syntax-Aware State Injection" to force the refinement loop to respect the simulator's physical state while allowing syntax fixes.

---

## Low-Level Planner Selection

The symbolic planner used for low-level PDDL planning is **configurable** via the `--planner` CLI argument.

### Available planners

| `--planner` | Backend | Notes |
|-------------|---------|-------|
| `pyperplan` *(default)* | [Pyperplan](https://github.com/aibasel/pyperplan) via Unified Planning | Pure Python — no binary needed. Handles `:strips :typing`. Recommended. |
| `up_fd` | [FastDownward](https://www.fast-downward.org/) via Unified Planning | Install: `pip install up-fast-downward`. Bundles FD binary. |
| `fd` | FastDownward direct subprocess | Requires `fast-downward` binary on `PATH` or at `downward/fast-downward.py`. |
| `symk` | [SymK](https://github.com/speckdavid/symk) via local wrapper | Requires SymK binary compiled in `third-party/symk_wrapper`. |

### Install planner packages

```bash
pip install up-pyperplan        # Pyperplan (default, always install)
pip install up-fast-downward    # FastDownward via UP (optional, larger)
```

### CLI usage

```bash
# Default (pyperplan, recommended)
python run_pipeline.py --domain babyai --pipeline multi_level --batch_id data_1

# FastDownward via UP
python run_pipeline.py --domain babyai --pipeline multi_level --batch_id data_1 --planner up_fd

# Native FastDownward subprocess (requires binary)
python run_pipeline.py --domain babyai --pipeline multi_level --batch_id data_1 --planner fd
```

### Why PDDLGym was removed

[PDDLGym](https://github.com/tomsilver/pddlgym) (the previous backend) is no longer maintained:

- No commits on the `main` branch
- Open issue [#101](https://github.com/tomsilver/pddlgym/issues/101): migration from deprecated `gym` to `gymnasium` never merged
- Parser rejects valid PDDL constructs: `(when ...)`, `(either ...)`, conditional effects, and nested type hierarchies
- The local `pddlgym_planners/fd.py` was a **stub** that always returned an empty plan

It has been replaced by the [Unified Planning](https://unified-planning.readthedocs.io/) framework (`unified-planning` package v1.3+), which is actively maintained, accepts full PDDL 2.1, and supports multiple planner backends.

