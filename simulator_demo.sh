#!/bin/bash

# Interactive Simulator Demo Script
# Allows running each simulator one by one

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    export PATH="$SCRIPT_DIR/.venv/bin:$PATH"
fi

show_menu() {
    echo ""
    echo "=========================================="
    echo "    LAPIS Simulator Demo"
    echo "=========================================="
    echo "1) BabyAI Simulator"
    echo "2) AI2THOR Simulator"
    echo "3) AlfWorld Simulator"
    echo "4) VirtualHome Simulator"
    echo "5) Habitat Simulator"
    echo "6) Run All Simulators Test"
    echo "q) Quit"
    echo "=========================================="
    echo -n "Select a simulator: "
}

run_babyai() {
    echo ""
    echo "=== Running BabyAI Simulator ==="
    echo "Opening visual window..."
    python3 << 'EOF'
import gymnasium as gym
from src.lapis.simulators import BabyAISimulator
import time

print("Creating BabyAI environment with rendering...")
env = gym.make("BabyAI-GoToObj-v0", render_mode="human")

print("Initializing BabyAI simulator...")
sim = BabyAISimulator(env)

print("Resetting environment...")
obs, info = sim.reset()
print(f"Initial observation keys: {obs.keys()}")
print(f"Mission: {obs.get('mission', 'N/A')}")

print("\nSimulator is ready. Visual window should be open.")
print("Press Ctrl+C to return to menu.")
try:
    while True:
        env.render()  # Keep updating the visual display
        time.sleep(0.1)  # 10 FPS refresh
except KeyboardInterrupt:
    print("\n\nClosing BabyAI simulator...")
    env.close()
EOF
}

run_ai2thor() {
    echo ""
    echo "=== Running AI2THOR Simulator ==="
    echo "Opening visual window..."
    python3 << 'EOF'
from src.lapis.simulators import AI2THORSimulator
import time

print("Initializing AI2THOR simulator with rendering...")
sim = AI2THORSimulator(scene="FloorPlan1", renderDepthImage=False, renderInstanceSegmentation=False)

print("Resetting environment...")
obs, info = sim.reset()
print(f"Initial observation keys: {obs.keys()}")
print(f"Number of objects: {len(obs['objects'])}")

print("\nSimulator is ready. Visual window should be open.")
print("Note: AI2THOR automatically displays the scene.")
print("Press Ctrl+C to return to menu.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n\nClosing AI2THOR simulator...")
EOF
}

run_alfworld() {
    echo ""
    echo "=== Running AlfWorld Simulator ==="
    echo "NOTE: AlfWorld is a TEXT-BASED simulator (like a text adventure game)"
    echo "      There are no graphics - you interact through text commands."
    echo ""
    python3 << 'EOF'
from src.lapis.simulators import AlfWorldSimulator
import textwrap

print("=" * 70)
print("          AlfWorld - Text-Based Household Simulator")
print("=" * 70)
print("\nInitializing AlfWorld simulator...")
print("(This may take a moment as it loads game files...)\n")

sim = AlfWorldSimulator()

print("Resetting environment...\n")
obs, info = sim.reset()

# Display the scene nicely formatted
print("=" * 70)
print("SCENE DESCRIPTION:")
print("=" * 70)
scene_text = obs['observation'][0] if isinstance(obs['observation'], tuple) else obs['observation']
for line in scene_text.split('\n'):
    print(textwrap.fill(line, width=70))

print("\n" + "=" * 70)
print("STATUS:")
print("=" * 70)
print(f"Location: {obs.get('location', 'Unknown')}")
print(f"Inventory: {obs.get('inventory', [])}")
print("=" * 70)

print("\nAlfWorld is TEXT-BASED - you see the world through descriptions.")
print("In a full implementation, you would type commands like:")
print("  - 'go to desk 1'")
print("  - 'take pillow from bed 1'")
print("  - 'examine desklamp'")
print("\nThis demo keeps the simulator open so you can see the environment.")
print("Press Ctrl+C to return to menu.")

try:
    while True:
        import time
        time.sleep(1)
except KeyboardInterrupt:
    print("\n\nClosing AlfWorld simulator...")
EOF
}

run_virtualhome() {
    echo ""
    echo "=== Running VirtualHome Simulator ==="
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║  VirtualHome is a 3D VISUAL simulator (like AI2THOR)          ║"
    echo "║  It requires the Unity executable to be running.              ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "CORRECT way to run VirtualHome Unity executable WITH GRAPHICS:"
    echo ""
    echo "  ./third-party/virtualhome/simulation/unity_simulator/linux_exec.v2.3.0.x86_64 -screen-fullscreen 0 -screen-quality 4 &"
    echo ""
    echo "  (-screen-fullscreen 0 = windowed mode, NOT fullscreen)"
    echo "  (-screen-quality 4 = high quality)"
    echo ""
    echo "NOTE: Do NOT use -batchmode flag! That disables graphics completely."
    echo ""
    read -p "Have you started the Unity executable with the correct flags? (y/n): " response
    
    if [[ ! $response =~ ^[Yy]$ ]]; then
        echo ""
        echo "Please start the Unity executable first, then run this option again."
        echo "Press Enter to return to menu..."
        read
        return
    fi
    
    echo ""
    echo "Connecting to VirtualHome Unity server..."
    python3 << 'EOF'
from src.lapis.simulators import VirtualHomeSimulator
import time
import os

print("=" * 70)
print("          VirtualHome - 3D Household Simulator")
print("=" * 70)
print("\nInitializing VirtualHome simulator...")
print("Connecting to Unity server on port 8080...\n")

try:
    sim = VirtualHomeSimulator()
    
    print("Loading scene...")
    obs, info = sim.reset()
    
    # Get the scene graph
    print("Querying scene graph...")
    success_graph, scene_graph = sim.comm.environment_graph()
    
    if success_graph and scene_graph:
        nodes = scene_graph.get('nodes', [])
        print(f"✓ Scene loaded with {len(nodes)} objects!")
    
    # ADD A CHARACTER
    print("Adding character to scene...")
    success_char = sim.comm.add_character()
    
    if success_char:
        print("✓ Character added successfully!")
    else:
        print("⚠ Could not add character")
    
    # Create output directory for images
    output_dir = "virtualhome_renders"
    os.makedirs(output_dir, exist_ok=True)
    
    # Render and SAVE images
    print(f"\nRendering scene and saving images to ./{output_dir}/...")
    script = ["[Walk] <chair> (0)", "[LookAt] <chair> (0)"]
    
    success, message = sim.comm.render_script(
        script,
        recording=True,
        skip_animation=False,
        camera_mode=["FIRST_PERSON"],
        image_synthesis=["normal"],
        save_pose_data=True,
        file_name_prefix=f"{output_dir}/scene",
        image_width=640,
        image_height=480
    )
    
    if success:
        print("✓ Scene rendered and images saved!")
        print(f"\n{'=' * 70}")
        print("SUCCESS! Images have been saved.")
        print("=" * 70)
        print(f"\nCheck the '{output_dir}/' directory for rendered images!")
        print("You can view them with: eog {output_dir}/*.png")
    else:
        print(f"⚠ Rendering issue: {message}")
    
    # Display scene information
    print("\n" + "=" * 70)
    print("SCENE INFORMATION:")
    print("=" * 70)
    
    if scene_graph and 'nodes' in scene_graph:
        nodes = scene_graph['nodes']
        edges = scene_graph.get('edges', [])
        
        print(f"Graph nodes: {len(nodes)}")
        print(f"Graph edges: {len(edges)}")
        
        if len(nodes) > 0:
            print("\nSample objects in scene:")
            object_types = {}
            for node in nodes[:50]:
                obj_type = node.get('class_name', 'unknown')
                object_types[obj_type] = object_types.get(obj_type, 0) + 1
            
            for obj_type, count in sorted(object_types.items())[:15]:
                print(f"  - {obj_type}: {count}")
    
    print(f"\nAgents: {len(obs.get('agents', []))}")
    print("=" * 70)
    
    print("\nNOTE: The Unity window may appear black (known Linux issue).")
    print("      However, the scene IS working - check the saved images!")
    print("\nPress Ctrl+C to return to menu.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nClosing VirtualHome simulator...")
        
except Exception as e:
    print("\n" + "=" * 70)
    print("ERROR: Could not connect to VirtualHome")
    print("=" * 70)
    print(f"Error: {e}")
    print("\nPossible issues:")
    print("  1. Unity executable is not running")
    print("  2. Port 8080 is blocked or in use")
    print("\nPress Ctrl+C to return to menu...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
EOF
}

run_habitat() {
    echo ""
    echo "=== Running Habitat Simulator ==="
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║  Habitat is a high-performance 3D simulator for embodied AI   ║"
    echo "║  It requires habitat-sim to be installed and scenes configured║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Installation:"
    echo "  conda install -c conda-forge -c aihabitat habitat-sim"
    echo ""
    echo "Scene datasets (choose one):"
    echo "  - Gibson: User has access (path to be configured)"
    echo "  - HM3D: Download from aihabitat.org/datasets/hm3d/"
    echo "  - Replica: Download from github.com/facebookresearch/Replica-Dataset"
    echo ""
    read -p "Have you installed habitat-sim and configured a scene dataset? (y/n): " response
    
    if [[ ! $response =~ ^[Yy]$ ]]; then
        echo ""
        echo "Please install habitat-sim and configure scene datasets first."
        echo "Press Enter to return to menu..."
        read
        return
    fi
    
    echo ""
    read -p "Enter path to scene file (.glb): " scene_path
    
    if [[ -z "$scene_path" ]]; then
        echo "No scene path provided. Returning to menu..."
        read
        return
    fi
    
    echo ""
    echo "Initializing Habitat with scene: $scene_path"
    python3 <<EOF
from src.lapis.simulators import HabitatSimulator
import time

print("=" * 70)
print("          Habitat - 3D Embodied AI Simulator")
print("=" * 70)
print("\nInitializing Habitat simulator...\n")

try:
    # Initialize with user-provided scene
    sim = HabitatSimulator(
        scene_path="$scene_path",
        width=640,
        height=480,
        sensor_suite=['rgb', 'depth']
    )
    
    print("Resetting environment...")
    obs, info = sim.reset()
    
    print(f"✓ Scene loaded successfully!")
    print(f"Scene ID: {info.get('scene_id', 'N/A')}")
    
    # Display observation info
    print("\n" + "=" * 70)
    print("OBSERVATION INFORMATION:")
    print("=" * 70)
    print(f"Available sensors: {list(obs.keys())}")
    
    if 'rgb' in obs:
        print(f"RGB sensor: {obs['rgb'].shape}")
    if 'depth' in obs:
        print(f"Depth sensor: {obs['depth'].shape}")
    
    print(f"Agent position: {obs.get('agent_position', 'N/A')}")
    print(f"Agent rotation: {obs.get('agent_rotation', 'N/A')}")
    print("=" * 70)
    
    # Execute a few sample actions
    print("\nExecuting sample navigation actions...")
    actions = ['move_forward', 'turn_left', 'turn_right']
    
    for action in actions:
        print(f"  - Executing: {action}")
        obs, reward, done, truncated, info = sim.step(action)
        print(f"    Position: {obs['agent_position']}")
        time.sleep(0.5)
    
    print("\n✓ Sample actions executed successfully!")
    
    print("\n" + "=" * 70)
    print("SUCCESS! Habitat simulator is working correctly.")
    print("=" * 70)
    
    print("\nAvailable actions:")
    print("  - move_forward: Move 0.25m forward")
    print("  - turn_left: Rotate 10° left")
    print("  - turn_right: Rotate 10° right")
    print("  - look_up: Tilt camera up")
    print("  - look_down: Tilt camera down")
    
    print("\nPress Ctrl+C to return to menu.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nClosing Habitat simulator...")
        sim.close()
        
except ImportError as e:
    print("\n" + "=" * 70)
    print("ERROR: Habitat-Sim not installed")
    print("=" * 70)
    print(f"Error: {e}")
    print("\nInstallation:")
    print("  conda install -c conda-forge -c aihabitat habitat-sim")
    print("  pip install git+https://github.com/facebookresearch/habitat-lab.git")
    
except Exception as e:
    print("\n" + "=" * 70)
    print("ERROR: Could not initialize Habitat")
    print("=" * 70)
    print(f"Error: {e}")
    print("\nPossible issues:")
    print("  1. Scene file path is incorrect or doesn't exist")
    print("  2. Scene file format is invalid (must be .glb)")
    print("  3. habitat-sim installation is incomplete")
    
    import traceback
    traceback.print_exc()

print("\nPress Enter to return to menu...")
input()
EOF
}

run_all_tests() {

    echo ""
    echo "=== Running All Simulators Test ==="
    python test_all_simulators.py
    echo ""
    read -p "Press Enter to return to menu..."
}

# Main loop
while true; do
    show_menu
    read choice
    
    case $choice in
        1)
            run_babyai
            ;;
        2)
            run_ai2thor
            ;;
        3)
            run_alfworld
            ;;
        4)
            run_virtualhome
            ;;
        5)
            run_habitat
            ;;
        6)
            run_all_tests
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

