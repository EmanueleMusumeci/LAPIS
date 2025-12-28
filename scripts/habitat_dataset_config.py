#!/usr/bin/env python3
"""
Habitat Dataset Configuration Helper

This script helps discover and configure scene datasets for Habitat simulator.
It searches for .glb scene files in configured dataset directories and provides
easy access to scene paths.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
import json

# Add src to path
SCRIPT_DIR = Path(__file__).parent.absolute()
COSTL_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(COSTL_ROOT / "src"))


class HabitatDatasetConfig:
    """Helper class to manage Habitat dataset configurations."""
    
    def __init__(self):
        self.costl_root = COSTL_ROOT
        self.config_file = self.costl_root / ".habitat_datasets.conf"
        self.cache_file = self.costl_root / ".habitat_scenes_cache.json"
        
        # Default dataset paths
        self.dataset_paths = {
            'replica': os.getenv('REPLICA_DATASET_PATH', str(self.costl_root / 'data/habitat_scenes/replica')),
            'hm3d': os.getenv('HM3D_DATASET_PATH', str(self.costl_root / 'data/habitat_scenes/hm3d')),
            'gibson': os.getenv('GIBSON_DATASET_PATH', ''),
            'mp3d': os.getenv('MP3D_DATASET_PATH', ''),
        }
        
        self.scenes_cache = {}
        self.load_cache()
    
    def load_cache(self):
        """Load cached scene information."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    self.scenes_cache = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load cache: {e}")
                self.scenes_cache = {}
    
    def save_cache(self):
        """Save scene information to cache."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.scenes_cache, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save cache: {e}")
    
    def discover_scenes(self, dataset_name: Optional[str] = None, refresh: bool = False) -> Dict[str, List[str]]:
        """
        Discover .glb scene files in dataset directories.
        
        Args:
            dataset_name: Specific dataset to search ('replica', 'hm3d', 'gibson', 'mp3d')
                         If None, searches all datasets
            refresh: If True, refresh cache even if it exists
            
        Returns:
            Dictionary mapping dataset names to lists of scene file paths
        """
        if not refresh and self.scenes_cache:
            if dataset_name:
                return {dataset_name: self.scenes_cache.get(dataset_name, [])}
            return self.scenes_cache
        
        scenes = {}
        datasets_to_search = [dataset_name] if dataset_name else list(self.dataset_paths.keys())
        
        for ds_name in datasets_to_search:
            path = self.dataset_paths.get(ds_name, '')
            if not path or not os.path.exists(path):
                scenes[ds_name] = []
                continue
            
            print(f"Searching {ds_name} dataset at {path}...")
            scene_files = []
            
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith('.glb'):
                        scene_files.append(os.path.join(root, file))
            
            scenes[ds_name] = sorted(scene_files)
            print(f"  Found {len(scene_files)} scenes")
        
        self.scenes_cache.update(scenes)
        self.save_cache()
        
        return scenes
    
    def list_scenes(self, dataset_name: Optional[str] = None, limit: int = 10):
        """Print available scenes."""
        scenes = self.discover_scenes(dataset_name)
        
        print("\n" + "="*70)
        print("Available Habitat Scenes")
        print("="*70)
        
        total = 0
        for ds_name, scene_list in scenes.items():
            if not scene_list:
                print(f"\n{ds_name.upper()}: No scenes found")
                path = self.dataset_paths.get(ds_name, 'Not configured')
                print(f"  Dataset path: {path}")
                if not os.path.exists(path):
                    print(f"  Status: ✗ Path does not exist")
                continue
            
            print(f"\n{ds_name.upper()}: {len(scene_list)} scenes")
            print(f"  Dataset path: {self.dataset_paths[ds_name]}")
            
            # Show first N scenes
            for i, scene_path in enumerate(scene_list[:limit]):
                scene_name = os.path.basename(scene_path)
                rel_path = os.path.relpath(scene_path, self.costl_root)
                print(f"  [{i}] {scene_name}")
                print(f"      {rel_path}")
            
            if len(scene_list) > limit:
                print(f"  ... and {len(scene_list) - limit} more")
            
            total += len(scene_list)
        
        print(f"\n{'='*70}")
        print(f"Total scenes available: {total}")
        print(f"{'='*70}\n")
    
    def get_scene_path(self, dataset_name: str, scene_id: int = 0) -> Optional[str]:
        """
        Get path to a specific scene.
        
        Args:
            dataset_name: Dataset name ('replica', 'hm3d', 'gibson', 'mp3d')
            scene_id: Scene index (0-based)
            
        Returns:
            Path to scene file, or None if not found
        """
        scenes = self.discover_scenes(dataset_name)
        scene_list = scenes.get(dataset_name, [])
        
        if not scene_list:
            return None
        
        if scene_id >= len(scene_list):
            print(f"Warning: Scene ID {scene_id} out of range (0-{len(scene_list)-1})")
            return None
        
        return scene_list[scene_id]
    
    def create_config_file(self):
        """Create or update .habitat_datasets.conf file."""
        config_content = f"""# Habitat Scene Datasets Configuration
# Source this file to set environment variables

export HABITAT_DATASETS_DIR="{self.costl_root}/data/habitat_scenes"
export REPLICA_DATASET_PATH="{self.dataset_paths['replica']}"
export HM3D_DATASET_PATH="{self.dataset_paths['hm3d']}"
export GIBSON_DATASET_PATH="{self.dataset_paths['gibson']}"
export MP3D_DATASET_PATH="{self.dataset_paths['mp3d']}"

export PYTHONPATH="$PYTHONPATH:{self.costl_root}/src"
"""
        
        with open(self.config_file, 'w') as f:
            f.write(config_content)
        
        print(f"✓ Configuration file created: {self.config_file}")
        print(f"\nTo use: source {self.config_file}")
    
    def test_simulator(self, dataset_name: str = 'replica', scene_id: int = 0):
        """Test Habitat simulator with a specific scene."""
        scene_path = self.get_scene_path(dataset_name, scene_id)
        
        if not scene_path:
            print(f"Error: No scene found for {dataset_name} [:{scene_id}]")
            return False
        
        print(f"\nTesting Habitat simulator with scene:")
        print(f"  Dataset: {dataset_name}")
        print(f"  Scene: {os.path.basename(scene_path)}")
        print(f"  Path: {scene_path}")
        print()
        
        try:
            from costl.simulators import HabitatSimulator
            
            print("Initializing simulator...")
            sim = HabitatSimulator(
                scene_path=scene_path,
                width=256,
                height=256,
                sensor_suite=['rgb', 'depth']
            )
            
            print("✓ Simulator created successfully")
            
            print("Resetting environment...")
            obs, info = sim.reset()
            
            print("✓ Environment reset successfully")
            print(f"  Observation keys: {list(obs.keys())}")
            
            if 'rgb' in obs:
                print(f"  RGB sensor: {obs['rgb'].shape}")
            if 'depth' in obs:
                print(f"  Depth sensor: {obs['depth'].shape}")
            
            print(f"  Agent position: {obs.get('agent_position')}")
            
            print("\nExecuting test actions...")
            actions = ['move_forward', 'turn_left', 'turn_right']
            
            for action in actions:
                obs, reward, done, truncated, info = sim.step(action)
                print(f"  ✓ {action}: position={obs['agent_position']}")
            
            sim.close()
            
            print("\n✓ All tests passed!")
            return True
            
        except ImportError as e:
            print(f"✗ Failed to import HabitatSimulator: {e}")
            print("\nInstall habitat-sim with:")
            print("  conda install -c conda-forge -c aihabitat habitat-sim")
            return False
        except Exception as e:
            print(f"✗ Test failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main CLI interface."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Habitat Dataset Configuration Helper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all available scenes
  %(prog)s --list
  
  # List scenes from specific dataset
  %(prog)s --list --dataset replica
  
  # Refresh scene cache
  %(prog)s --list --refresh
  
  # Test simulator with a scene
  %(prog)s --test --dataset replica --scene-id 0
  
  # Create configuration file
  %(prog)s --create-config
        """
    )
    
    parser.add_argument('--list', action='store_true',
                       help='List available scenes')
    parser.add_argument('--test', action='store_true',
                       help='Test simulator with a scene')
    parser.add_argument('--dataset', type=str,
                       choices=['replica', 'hm3d', 'gibson', 'mp3d'],
                       help='Dataset name')
    parser.add_argument('--scene-id', type=int, default=0,
                       help='Scene ID (index) to use for testing')
    parser.add_argument('--limit', type=int, default=10,
                       help='Maximum number of scenes to display per dataset')
    parser.add_argument('--refresh', action='store_true',
                       help='Refresh scene cache')
    parser.add_argument('--create-config', action='store_true',
                       help='Create .habitat_datasets.conf file')
    
    args = parser.parse_args()
    
    config = HabitatDatasetConfig()
    
    if args.create_config:
        config.create_config_file()
        return
    
    if args.list:
        config.list_scenes(args.dataset, limit=args.limit)
        return
    
    if args.test:
        dataset = args.dataset or 'replica'
        success = config.test_simulator(dataset, args.scene_id)
        sys.exit(0 if success else 1)
    
    # Default: show help
    parser.print_help()


if __name__ == '__main__':
    main()
