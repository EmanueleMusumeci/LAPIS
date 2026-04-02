
import sys

def verify_file_content():
    file_path = "/DATA/LAPIS/src/lapis/pipelines/multi_level_planning.py"
    
    try:
        with open(file_path, "r") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        sys.exit(1)
    
    print(f"Analyzing {file_path}...")
    
    # 1. Verify trace check moved out of loop
    subgoal_loop_start = content.find("for i, subgoal in enumerate(plan_lines):")
    final_check_start = content.find("# After ALL subgoals: Perform Final Global LTL Check")
    
    if subgoal_loop_start == -1:
        print("Error: Could not find subgoal loop start.")
        sys.exit(1)
        
    if final_check_start == -1:
        print("Error: Could not find final check block start.")
        sys.exit(1)
        
    loop_content = content[subgoal_loop_start:final_check_start]
    
    # Check for check_trace calls in the loop
    # We allow commented out calls, but not active ones
    lines = loop_content.splitlines()
    found_trace_check = False
    for line in lines:
        stripped = line.strip()
        if "check_trace(" in stripped and not stripped.startswith("#"):
            print(f"FAILURE: Found active 'check_trace(' inside subgoal loop: {stripped}")
            found_trace_check = True
            
    if not found_trace_check:
        print("SUCCESS: No active 'check_trace(' found inside subgoal loop.")
        
    # 2. Verify new formatting logic exists
    # We look for the specific strings added for formatting
    formatting_markers = [
        "- **State {i}**:",
        "md_lines.append(f\"  - **{pred}**\")",
        "parsed = ast.literal_eval(state)"
    ]
    
    all_markers_found = True
    for marker in formatting_markers:
        if marker not in content:
            print(f"FAILURE: Could not find formatting marker: '{marker}'")
            all_markers_found = False
            
    if all_markers_found:
        print("SUCCESS: Found new trace formatting logic.")
        
    if not found_trace_check and all_markers_found:
        print("\nOVERALL: VERIFICATION PASSED")
        sys.exit(0)
    else:
        print("\nOVERALL: VERIFICATION FAILED")
        sys.exit(1)

if __name__ == "__main__":
    verify_file_content()
