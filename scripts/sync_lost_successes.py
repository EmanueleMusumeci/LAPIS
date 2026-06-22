import os
import json
import shutil
from pathlib import Path

FINAL_RESULTS_DIR = Path("/DATA/lapis/final_results")
SEARCH_DIRS = [
    Path("/DATA/lapis/results_icaps2026"),
    Path("/DATA/lapis/results_llmpp"),
    Path("/DATA/lapis/results")
]

DOMAINS = ["blocksworld", "barman", "storage", "termes", "grippers", "tyreworld", "floortile"]

def get_condition_name(p, data):
    path_str = str(p).lower()
    method = data.get("method", "lapis").lower()
    gen_dom = "domgen" in path_str or data.get("generate_domain", False)
    adequacy = "adequacy" in path_str or data.get("check_adequacy", False)
    refinements = data.get("pddl_gen_iterations", 3)
    
    cond_suffix = None
    if not gen_dom:
        # LLM+P or LAPIS Zero-Shot GT
        if method == "llmpp": cond_suffix = "LLM+P_Zero-Shot" # Maps to a generic placeholder if needed
        else: cond_suffix = "LAPIS_GT"
    else:
        if adequacy: cond_suffix = "LAPIS_Adequacy"
        else: cond_suffix = "LAPIS_Synthesis"
    
    return cond_suffix

def sync_lost_successes():
    synced_count = 0
    
    for root in SEARCH_DIRS:
        if not root.exists(): continue
        for p in root.rglob("manifold.json"):
            try:
                with open(p, 'r') as f:
                    data = json.load(f)
                
                if not data.get("planning_successful", False): continue
                
                raw_domain = data.get("domain", "").lower()
                found_domain = next((d for d in DOMAINS if d.lower() in raw_domain), None)
                if not found_domain:
                    path_str = str(p).lower()
                    found_domain = next((d for d in DOMAINS if d.lower() in path_str), None)
                if not found_domain: continue
                
                cond_suffix = get_condition_name(p, data)
                if not cond_suffix: continue
                
                p_id = data.get("problem_id", "")
                if not p_id: continue
                
                # Check if already in final_results
                target_dir = FINAL_RESULTS_DIR / f"{found_domain}_{cond_suffix}" / p_id
                if target_dir.exists():
                    # We might already have it, check if our current one is successful
                    manifold_target = target_dir / "manifold.json"
                    if manifold_target.exists():
                        continue # Already archived
                
                # If we get here, it's a "lost" success
                print(f"🔍 Found lost success: {found_domain} {p_id} {cond_suffix} at {p.parent}")
                
                # Copy the whole problem directory to final_results
                os.makedirs(target_dir, exist_ok=True)
                for item in p.parent.iterdir():
                    if item.is_dir():
                        shutil.copytree(item, target_dir / item.name, dirs_exist_ok=True)
                    else:
                        shutil.copy2(item, target_dir / item.name)
                
                synced_count += 1
            except Exception as e:
                print(f"Error processing {p}: {e}")
                
    print(f"\n✅ Synced {synced_count} lost successes to {FINAL_RESULTS_DIR}")

if __name__ == "__main__":
    sync_lost_successes()
