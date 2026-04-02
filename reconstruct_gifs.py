import patch
import patch
import sys
import os
from pathlib import Path
import pprint

# Add workspace to path
sys.path.append("/DATA/LAPIS")

from src.lapis.simulators.blocksworld_simulator import BlocksworldSimulator
from src.lapis.simulators.babyai_simulator import BabyAISimulator

from dataclasses import dataclass

@dataclass
class PDDLActionWrapper:
    name: str

@dataclass
class PDDLActionInstance:
    action: PDDLActionWrapper
    actual_parameters: list

def parse_plan_file(plan_file_path):
    actions = []
    with open(plan_file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(';'):
                continue
            line = line.replace('(', '').replace(')', '')
            parts = line.split()
            if parts:
                actions.append(PDDLActionInstance(
                    action=PDDLActionWrapper(name=parts[0]),
                    actual_parameters=parts[1:]
                ))
    return actions

def get_up_actions(sim, parsed_actions, is_babyai=False):
    if is_babyai:
        return parsed_actions
    up_actions = []
    for action_obj in parsed_actions:
        up_action_name = action_obj.action.name
        up_params = action_obj.actual_parameters
        
        found_action = None
        for ua in sim.problem.actions:
            if ua.name.lower() == up_action_name.lower():
                found_action = ua
                break
        
        if found_action:
            up_args = []
            for p_name in up_params:
                if not sim.problem.has_object(p_name):
                    found_obj = None
                    for o in sim.problem.all_objects:
                        if o.name.lower() == p_name.lower():
                            found_obj = o
                            break
                    if found_obj:
                        obj = found_obj
                    else:
                        raise ValueError(f"Object {p_name} not found")
                else:
                    obj = sim.problem.object(p_name)
                up_args.append(obj)
            up_actions.append(found_action(*up_args))
    return up_actions

def reconstruct_sim_gif(name, sim, domain_path, problem_path, gif_output_path, plan_actions, goal_text=None, constraint_text=None, start_pause_frames=1, end_pause_frames=1, frame_delay_ms=500, is_babyai=False):
    print(f"--- Reconstructing {name} GIF ---")
    if not is_babyai:
        success = sim.setup(Path(domain_path), Path(problem_path))
        if not success:
            print(f"Failed to setup {name} simulator")
            return
    else:
        # BabyAI environment doesn't use PDDL files for setup in the same way, 
        # but simulator is already reset/initialized below.
        pass

    frames = []
    
    # Capture initial state
    img = sim.get_image(action_text="Initial State", goal_text=goal_text, constraint_text=constraint_text)
    if img:
        frames.append(img)
        
    up_actions = get_up_actions(sim, plan_actions, is_babyai=is_babyai)
    
    for up_action in up_actions:
        if not is_babyai and not sim.simulator.is_applicable(sim.current_state, up_action):
            print(f"Action {up_action} is NOT applicable in current state! Stopping.")
            break
        action_str = f"{up_action}"
        print(f"[{name}] Executing action: {action_str}")
        if is_babyai:
            sim_action = sim.map_pddl2simulator(up_action)
            step_result = sim.step(sim_action)
        else:
            obs, _, _, _, _ = sim.step(up_action)
        img = sim.get_image(action_text=action_str, goal_text=goal_text, constraint_text=constraint_text)
        if img:
            frames.append(img)
            
    if frames:
        durations = []
        if len(frames) == 1:
            durations = [frame_delay_ms * max(1, start_pause_frames + end_pause_frames)]
        else:
            durations.append(frame_delay_ms * max(1, start_pause_frames))
            for _ in range(len(frames) - 2):
                durations.append(frame_delay_ms)
            durations.append(frame_delay_ms * max(1, end_pause_frames))

        frames[0].save(
            gif_output_path,
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=0
        )
        print(f"Saved {name} simulation GIF to {gif_output_path} with {len(frames)} frames")
        
        # Save individual frames
        frames_dir = Path(gif_output_path).parent / f"frames_{name}"
        frames_dir.mkdir(parents=True, exist_ok=True)
        for idx, frame in enumerate(frames):
            frame_path = frames_dir / f"frame_{idx:03d}.png"
            frame.save(frame_path)
        print(f"Saved {len(frames)} individual frames to {frames_dir}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Reconstruct simulator GIFs from plan files.")
    parser.add_argument("--start-pause", type=int, default=5, help="Number of frames to pause at the start (multiplier for frame delay)")
    parser.add_argument("--end-pause", type=int, default=5, help="Number of frames to pause at the end (multiplier for frame delay)")
    parser.add_argument("--frame-delay", type=int, default=300, help="Delay between frames in milliseconds")
    parser.add_argument("--domain", type=str, default="blocksworld", help="Domain name (e.g., blocksworld, babyai)")
    parser.add_argument("--env-name", type=str, default=None, help="Gymnasium environment name (e.g., BabyAI-MiniBossLevel-v0) if domain is babyai")
    parser.add_argument("--results-base", type=str, default="/DATA/LAPIS/results/final_bench", help="Results base directory")
    
    args = parser.parse_args()

    results_base = Path(args.results_base)
    domain_data_dir = f"/DATA/LAPIS/data/{args.domain}/data"
    
    if args.domain == "babyai":
        batches = ["babyai_test"]
        # run_pipeline.py saves to real_run_100 by default in run_pipeline
        results_base = Path("/DATA/LAPIS/results/real_run_100")
    else:
        batches = ["data_1", "data_2"]

    for batch_id in batches:
        batch_dir = results_base / batch_id / "MultiLevelPlanningPipeline_GPTAgent"
        if not batch_dir.exists():
            print(f"Directory {batch_dir} not found. Skipping.")
            continue
            
        # Get the latest timestamp directory
        timestamp_dirs = sorted([d for d in batch_dir.iterdir() if d.is_dir()])
        if not timestamp_dirs:
            print(f"No timestamp directories found in {batch_dir}. Skipping.")
            continue
            
        latest_dir = timestamp_dirs[-1]
        print(f"\nProcessing Batch: {batch_id} in {latest_dir}")
        
        # Iterate over all problem IDs (e.g., 100, 101, etc.)
        for problem_dir in sorted([d for d in latest_dir.iterdir() if d.is_dir()]):
            problem_id = problem_dir.name
            plan_file = problem_dir / "full_plan.txt"
            
            if not plan_file.exists():
                print(f"  [{problem_id}] No full_plan.txt found. Skipping.")
                continue
                
            try:
                plan_actions = parse_plan_file(plan_file)
                print(f"\n  [{problem_id}] Parsed {len(plan_actions)} actions.")
                
                # 1. Reconstruct GT GIF
                gt_domain = f"{domain_data_dir}/{batch_id}/{problem_id}/domain.pddl"
                gt_problem = f"{domain_data_dir}/{batch_id}/{problem_id}/problem.pddl"
                gt_gif = problem_dir / "simulation_GT.gif"
                
                # Fetch NL goal and constraint from problem
                goal_text = None
                constraint_text = None
                nl_file = Path(f"{domain_data_dir}/{batch_id}/{problem_id}/nl")
                if nl_file.exists():
                    with open(nl_file, "r") as f:
                        content = f.read()
                        
                    if "The task is to bring about the following situation:" in content:
                        parts = content.split("The task is to bring about the following situation:\n")
                        if len(parts) > 1:
                            rest = parts[1]
                            goal_lines = []
                            for line in rest.split('\n'):
                                line = line.strip()
                                if not line: continue
                                if "A valid plan for the abovementioned problem must abide by the following constraints:" in line:
                                    break
                                goal_lines.append(line.replace('"', ''))
                            goal_text = " ".join(goal_lines)

                    if "A valid plan for the abovementioned problem must abide by the following constraints:" in content:
                        parts = content.split("A valid plan for the abovementioned problem must abide by the following constraints:\n")
                        if len(parts) > 1:
                            rest = parts[1]
                            constraint_text = rest.strip().replace('\t', '').replace('"', '')
                
                if args.domain == "babyai" or (Path(gt_domain).exists() and Path(gt_problem).exists()):
                    try:
                        is_babyai = args.domain == "babyai"
                        if is_babyai:
                            import gymnasium as gym
                            env_name = args.env_name if args.env_name else "BabyAI-MiniBossLevel-v0"
                            env = gym.make(env_name, render_mode="rgb_array", highlight=False)
                            seed = int(problem_id) if problem_id.isdigit() else 0
                            env.reset(seed=seed)
                            sim_gt = BabyAISimulator(env)
                            
                            # Mock simulator logic for get_up_actions since BabyAI doesn't use UP action definitions
                            # This bypasses mapping errors in reconstruct script
                            class DummyActionWrapper:
                                def __init__(self, name):
                                    self.name = name
                            class DummyAction:
                                def __init__(self, orig_action):
                                    self.action = DummyActionWrapper(orig_action.action.name)
                                    self.actual_parameters = orig_action.actual_parameters
                                def __str__(self):
                                    return f"{self.action.name}({', '.join(self.actual_parameters)})"
                            up_actions = [DummyAction(a) for a in plan_actions]
                            reconstruct_sim_gif("GT", sim_gt, gt_domain, gt_problem, gt_gif, up_actions, goal_text=goal_text, constraint_text=constraint_text, start_pause_frames=args.start_pause, end_pause_frames=args.end_pause, frame_delay_ms=args.frame_delay, is_babyai=True)
                        else:
                            sim_gt = BlocksworldSimulator()
                            reconstruct_sim_gif("GT", sim_gt, gt_domain, gt_problem, gt_gif, plan_actions, goal_text=goal_text, constraint_text=constraint_text, start_pause_frames=args.start_pause, end_pause_frames=args.end_pause, frame_delay_ms=args.frame_delay)
                    except Exception as e:
                        import traceback
                        traceback.print_exc()
                        print(f"  [{problem_id}] Error reconstructing GT GIF: {e}")
                else:
                    print(f"  [{problem_id}] GT PDDL files not found.")
                
                # 2. Reconstruct Generated GIF
                gen_domain = problem_dir / "subgoal_0/iteration_0/refinement_2/domain.pddl"
                gen_problem = problem_dir / "subgoal_0/iteration_0/refinement_2/problems/problem.pddl"
                if not gen_domain.exists():
                     gen_domain = problem_dir / "subgoal_0/domain.pddl"
                     gen_problem = problem_dir / "subgoal_0/problem.pddl"
                     
                gen_gif = problem_dir / "simulation_Generated.gif"
                if args.domain == "babyai" or (gen_domain.exists() and gen_problem.exists()):
                    try:
                        is_babyai = args.domain == "babyai"
                        if is_babyai:
                            import gymnasium as gym
                            env_name = args.env_name if args.env_name else "BabyAI-MiniBossLevel-v0"
                            env = gym.make(env_name, render_mode="rgb_array", highlight=False)
                            seed = int(problem_id) if problem_id.isdigit() else 0
                            env.reset(seed=seed)
                            sim_gen = BabyAISimulator(env)
                            
                            class DummyActionWrapper:
                                def __init__(self, name):
                                    self.name = name
                            class DummyAction:
                                def __init__(self, orig_action):
                                    self.action = DummyActionWrapper(orig_action.action.name)
                                    self.actual_parameters = orig_action.actual_parameters
                                def __str__(self):
                                    return f"{self.action.name}({', '.join(self.actual_parameters)})"
                            up_actions = [DummyAction(a) for a in plan_actions]
                            reconstruct_sim_gif("Generated", sim_gen, gen_domain, gen_problem, gen_gif, up_actions, goal_text=goal_text, constraint_text=constraint_text, start_pause_frames=args.start_pause, end_pause_frames=args.end_pause, frame_delay_ms=args.frame_delay, is_babyai=True)
                        else:
                            sim_gen = BlocksworldSimulator()
                            reconstruct_sim_gif("Generated", sim_gen, gen_domain, gen_problem, gen_gif, plan_actions, goal_text=goal_text, constraint_text=constraint_text, start_pause_frames=args.start_pause, end_pause_frames=args.end_pause, frame_delay_ms=args.frame_delay)
                    except Exception as e:
                        import traceback
                        traceback.print_exc()
                        print(f"  [{problem_id}] Error reconstructing Generated GIF: {e}")
                else:
                    print(f"  [{problem_id}] Generated PDDL files not found.")
            except Exception as e:
                print(f"  [{problem_id}] Error processing problem: {e}")

if __name__ == "__main__":
    main()
