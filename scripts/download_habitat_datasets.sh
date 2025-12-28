#!/bin/bash

# Download script for Habitat scene datasets (HM3D and Replica)
# This script helps set up scene datasets for the Habitat simulator

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}"))" && pwd)"
COSTL_ROOT="$(dirname "$SCRIPT_DIR")"
DATA_DIR="${DATA_DIR:-$COSTL_ROOT/data/habitat_scenes}"

echo "=============================================="
echo "  Habitat Scene Datasets Download Script"
echo "=============================================="
echo ""
echo "This script will help you download and configure:"
echo "  1. HM3D (Habitat-Matterport 3D) - 1000 indoor scenes"
echo "  2. Replica Dataset - 18 photorealistic scenes"
echo ""
echo "Target directory: $DATA_DIR"
echo ""

# Create data directory
mkdir -p "$DATA_DIR"

show_menu() {
    echo ""
    echo "=========================================="
    echo "Select dataset to download:"
    echo "=========================================="
    echo "1) Replica Dataset (recommended - free, no registration)"
    echo "2) HM3D Dataset (requires Matterport API token)"
    echo "3) Configure dataset paths"
    echo "4) Test dataset configuration"
    echo "q) Quit"
    echo "=========================================="
    echo -n "Your choice: "
}

download_replica() {
    echo ""
    echo "=== Downloading Replica Dataset ==="
    echo ""
    echo "Replica: 18 high-quality 3D reconstructions of indoor spaces"
    echo "Size: ~10 GB"
    echo "License: Creative Commons Attribution 4.0"
    echo ""
    
    REPLICA_DIR="$DATA_DIR/replica"
    mkdir -p "$REPLICA_DIR"
    
    read -p "Download Replica dataset to $REPLICA_DIR? (y/n): " confirm
    
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        echo "Skipping Replica download."
        return
    fi
    
    echo ""
    echo "Checking dependencies..."
    
    # Check for wget
    if ! command -v wget &> /dev/null; then
        echo "Error: wget is required but not installed."
        echo "Install with: sudo apt-get install wget"
        return 1
    fi
    
    # Check for unzip
    if ! command -v unzip &> /dev/null; then
        echo "Error: unzip is required but not installed."
        echo "Install with: sudo apt-get install unzip"
        return 1
    fi
    
    echo "✓ Dependencies satisfied"
    echo ""
    echo "Downloading Replica dataset..."
    echo "This may take a while depending on your connection..."
    
    cd "$REPLICA_DIR"
    
    # Download the Replica dataset
    # Using the official download script approach
    echo "Fetching download script..."
    wget -q https://raw.githubusercontent.com/facebookresearch/Replica-Dataset/main/download.sh -O download_replica.sh
    
    chmod +x download_replica.sh
    
    echo "Running Replica download script..."
    echo "Note: This will download ~10GB of data"
    ./download_replica.sh
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✓ Replica dataset downloaded successfully!"
        echo "Location: $REPLICA_DIR"
        echo ""
        echo "Available scenes:"
        ls -1 "$REPLICA_DIR" | grep -E "\.glb$|room_|apartment_|office_|hotel_|frl_apartment_" | head -n 20
    else
        echo ""
        echo "⚠ Download may have failed. Check the output above for errors."
    fi
    
    cd "$COSTL_ROOT"
}

download_hm3d() {
    echo ""
    echo "=== Downloading HM3D Dataset ==="
    echo ""
    echo "HM3D: 1000 large-scale 3D indoor environments"
    echo "Size: ~100-300 GB (depending on what you download)"
    echo "License: Academic, non-commercial use"
    echo "Requires: Matterport API token"
    echo ""
    
    echo "Steps to get Matterport API token:"
    echo "  1. Go to: https://my.matterport.com/settings/account/devtools"
    echo "  2. Generate an API token"
    echo "  3. Save both the token ID and secret (secret can't be retrieved later!)"
    echo ""
    
    read -p "Do you have a Matterport API token? (y/n): " has_token
    
    if [[ ! $has_token =~ ^[Yy]$ ]]; then
        echo ""
        echo "Please obtain a Matterport API token first:"
        echo "  1. Visit: https://my.matterport.com/settings/account/devtools"
        echo "  2. Sign up for academic/research access"
        echo "  3. Generate API token"
        echo ""
        echo "Then run this script again."
        return
    fi
    
    echo ""
    read -p "Enter Matterport API token ID (username): " token_id
    read -sp "Enter Matterport API token secret (password): " token_secret
    echo ""
    
    if [[ -z "$token_id" ]] || [[ -z "$token_secret" ]]; then
        echo "Error: Both token ID and secret are required."
        return 1
    fi
    
    HM3D_DIR="$DATA_DIR/hm3d"
    mkdir -p "$HM3D_DIR"
    
    echo ""
    echo "Download options:"
    echo "  1. hm3d_minival - Small subset for testing (~1 GB)"
    echo "  2. hm3d_train - Training set (~150 GB)"
    echo "  3. hm3d_val - Validation set (~20 GB)"
    echo "  4. hm3d_full - Complete dataset with raw GLBs (~300 GB)"
    echo ""
    read -p "Which dataset? (1-4): " dataset_choice
    
    case $dataset_choice in
        1) uid="hm3d_minival" ;;
        2) uid="hm3d_train" ;;
        3) uid="hm3d_val" ;;
        4) uid="hm3d_full" ;;
        *) echo "Invalid choice"; return 1 ;;
    esac
    
    echo ""
    echo "Downloading HM3D ($uid) to $HM3D_DIR..."
    echo "This may take several hours depending on dataset size..."
    
    # Check if habitat_sim is available
    if ! python3 -c "import habitat_sim" 2>/dev/null; then
        echo "Warning: habitat_sim not found. Attempting download with habitat_sim tools..."
        echo "You may need to install habitat-sim first:"
        echo "  conda install -c conda-forge -c aihabitat habitat-sim"
        return 1
    fi
    
    # Use habitat_sim download utility
    python3 -m habitat_sim.utils.datasets_download \
        --username "$token_id" \
        --password "$token_secret" \
        --uids "$uid" \
        --data-path "$HM3D_DIR"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✓ HM3D dataset downloaded successfully!"
        echo "Location: $HM3D_DIR"
    else
        echo ""
        echo "⚠ Download failed. Check your API credentials and network connection."
    fi
}

configure_paths() {
    echo ""
    echo "=== Configure Dataset Paths ==="
    echo ""
    
    CONFIG_FILE="$COSTL_ROOT/.habitat_datasets.conf"
    
    echo "Creating configuration file: $CONFIG_FILE"
    
    cat > "$CONFIG_FILE" << EOF
# Habitat Scene Datasets Configuration
# This file is automatically generated and sourced by CoSTL

# Dataset directories
export HABITAT_DATASETS_DIR="$DATA_DIR"
export REPLICA_DATASET_PATH="$DATA_DIR/replica"
export HM3D_DATASET_PATH="$DATA_DIR/hm3d"
export GIBSON_DATASET_PATH="${GIBSON_DATASET_PATH:-}"

# Add to Python path if needed
export PYTHONPATH="\${PYTHONPATH}:$COSTL_ROOT/src"
EOF
    
    echo "✓ Configuration file created"
    echo ""
    echo "To use these datasets, source the configuration:"
    echo "  source $CONFIG_FILE"
    echo ""
    echo "Or add to your ~/.bashrc:"
    echo "  echo 'source $CONFIG_FILE' >> ~/.bashrc"
    echo ""
    
    # Ask about Gibson dataset
    echo "You mentioned having access to Gibson dataset."
    read -p "Enter Gibson dataset path (or press Enter to skip): " gibson_path
    
    if [[ -n "$gibson_path" ]]; then
        sed -i "s|export GIBSON_DATASET_PATH=.*|export GIBSON_DATASET_PATH=\"$gibson_path\"|" "$CONFIG_FILE"
        echo "✓ Gibson dataset path configured: $gibson_path"
    fi
    
    echo ""
read -p "Press Enter to continue..."
}

test_datasets() {
    echo ""
    echo "=== Testing Dataset Configuration ==="
    echo ""
    
    CONFIG_FILE="$COSTL_ROOT/.habitat_datasets.conf"
    
    if [ -f "$CONFIG_FILE" ]; then
        echo "Loading configuration from $CONFIG_FILE"
        source "$CONFIG_FILE"
    fi
    
    echo "Checking datasets..."
    echo ""
    
    # Check Replica
    if [ -d "$REPLICA_DATASET_PATH" ]; then
        scene_count=$(find "$REPLICA_DATASET_PATH" -name "*.glb" -o -name "mesh.ply" | wc -l)
        echo "✓ Replica dataset found"
        echo "  Path: $REPLICA_DATASET_PATH"
        echo "  Scenes: $scene_count"
    else
        echo "✗ Replica dataset not found at $REPLICA_DATASET_PATH"
    fi
    
    echo ""
    
    # Check HM3D
    if [ -d "$HM3D_DATASET_PATH" ]; then
        scene_count=$(find "$HM3D_DATASET_PATH" -name "*.glb" | wc -l)
        echo "✓ HM3D dataset found"
        echo "  Path: $HM3D_DATASET_PATH"
        echo "  Scenes: $scene_count"
    else
        echo "✗ HM3D dataset not found at $HM3D_DATASET_PATH"
    fi
    
    echo ""
    
    # Check Gibson
    if [ -n "$GIBSON_DATASET_PATH" ] && [ -d "$GIBSON_DATASET_PATH" ]; then
        scene_count=$(find "$GIBSON_DATASET_PATH" -name "*.glb" | wc -l)
        echo "✓ Gibson dataset found"
        echo "  Path: $GIBSON_DATASET_PATH"
        echo "  Scenes: $scene_count"
    else
        echo "✗ Gibson dataset not configured or not found"
    fi
    
    echo ""
    
    # Test Python import
    echo "Testing Python integration..."
    python3 << EOF
import sys
sys.path.insert(0, "$COSTL_ROOT/src")

try:
    from costl.simulators import HabitatSimulator
    print("✓ HabitatSimulator can be imported")
    
    # Check if we can list any scenes
    import os
    datasets = {
        'Replica': '$REPLICA_DATASET_PATH',
        'HM3D': '$HM3D_DATASET_PATH',
        'Gibson': '$GIBSON_DATASET_PATH'
    }
    
    print("\nAvailable scene files:")
    for name, path in datasets.items():
        if os.path.exists(path):
            glb_files = []
            for root, dirs, files in os.walk(path):
                glb_files.extend([f for f in files if f.endswith('.glb')])
            if glb_files:
                print(f"  {name}: {len(glb_files)} .glb files")
                # Show first 3 as examples
                for glb in glb_files[:3]:
                    print(f"    - {glb}")
                if len(glb_files) > 3:
                    print(f"    ... and {len(glb_files) - 3} more")
    
except ImportError as e:
    print(f"✗ Failed to import HabitatSimulator: {e}")
    sys.exit(1)
EOF
    
    echo ""
    read -p "Press Enter to continue..."
}

# Main loop
while true; do
    show_menu
    read choice
    
    case $choice in
        1)
            download_replica
            ;;
        2)
            download_hm3d
            ;;
        3)
            configure_paths
            ;;
        4)
            test_datasets
            ;;
        q|Q)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo "Invalid option. Please try again."
            sleep 1
            ;;
    esac
done
