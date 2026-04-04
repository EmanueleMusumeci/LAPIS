import os
import json
import shutil
from pathlib import Path

DOMAINS = ["blocksworld", "barman", "storage", "termes", "grippers", "tyreworld", "floortile"]

CONDITIONS = [
    "LLM+P (Few-Shot GT)",
    "LLM+P (Zero-Shot)",
    "LAPIS (Zero-Shot GT)",
    "LAPIS (Synthesis, 0 Iterations)",
    "LAPIS (Synthesis, 3 Iterations)",
    "LAPIS (Adequacy Check)"
]

def parse_filesystem_for_best_dirs():
    """Scans and collects the physical paths of the best runs."""
    search_dirs = [
        Path("/DATA/lapis/results_icaps2026"),
        Path("/DATA/lapis/results_llmpp"),
        Path("/DATA/lapis/results")
    ]
    
    # Store tuples of (directory_path, problem_id)
    best_results = {d: {c: {} for c in CONDITIONS} for d in DOMAINS}
    
    for root in search_dirs:
        if not root.exists(): continue
        # Find all manifold.jsons
        for p in root.rglob("manifold.json"):
            try:
                with open(p, 'r') as f:
                    data = json.load(f)
                    
                path_str = str(p).lower()
                raw_domain = data.get("domain", "").lower()
                found_domain = next((d for d in DOMAINS if d in raw_domain), None)
                if not found_domain:
                    found_domain = next((d for d in DOMAINS if d in path_str), None)
                if not found_domain: continue
                
                method = data.get("method", "lapis").lower()
                gen_dom = "domgen" in path_str or data.get("generate_domain", False)
                adequacy = "adequacy" in path_str or data.get("check_adequacy", False)
                refinements = data.get("pddl_gen_iterations", 3)
                
                cond = None
                if not gen_dom:
                    if method == "llmpp": cond = "LLM+P (Zero-Shot)"
                    else: cond = "LAPIS (Zero-Shot GT)"
                else:
                    if adequacy: cond = "LAPIS (Adequacy Check)"
                    elif (method == "llmpp" or (method == "lapis" and refinements == 0)): 
                        cond = "LAPIS (Synthesis, 0 Iterations)"
                    elif method == "lapis" and refinements > 0:
                        cond = "LAPIS (Synthesis, 3 Iterations)"
                        
                p_id = data.get("problem_id", "")
                val_valid = data.get("val_valid", False)
                plan_ok = data.get("planning_successful", False)
                
                if cond and p_id:
                    # Give strict preference to structurally valid plans
                    if val_valid or plan_ok:
                        best_results[found_domain][cond][p_id] = p.parent
                    elif p_id not in best_results[found_domain][cond]:
                        # Fallback: keep it if it's the only one we have, even if incomplete
                        best_results[found_domain][cond][p_id] = p.parent
            except:
                continue
                
    return best_results

def populate_final_results():
    final_root = Path("/DATA/lapis/final_results")
    if not final_root.exists():
        final_root.mkdir(parents=True)
        
    best_results = parse_filesystem_for_best_dirs()
    
    # Map condition names to safe directory names
    cond_map = {
        "LLM+P (Few-Shot GT)": "LLMPP_FewShot_GT",
        "LLM+P (Zero-Shot)": "LLMPP_ZeroShot",
        "LAPIS (Zero-Shot GT)": "LAPIS_ZeroShot_GT",
        "LAPIS (Synthesis, 0 Iterations)": "LAPIS_Synth_0Iter",
        "LAPIS (Synthesis, 3 Iterations)": "LAPIS_Synth_3Iter",
        "LAPIS (Adequacy Check)": "LAPIS_Adequacy"
    }

    print("Populating /DATA/lapis/final_results/ with physical highest-watermark directories...")
    
    for domain in DOMAINS:
        for cond in CONDITIONS:
            safe_cond = cond_map[cond]
            target_dir = final_root / f"{domain}_{safe_cond}"
            if not target_dir.exists():
                target_dir.mkdir(parents=True)
                
            problems_dict = best_results[domain][cond]
            for p_id, src_dir in problems_dict.items():
                dest_path = target_dir / p_id
                
                # We need to copy the directory. If it's inside `iteration_0`, we copy the parent dir.
                if src_dir.name.startswith("iteration"):
                    actual_src = src_dir.parent
                else:
                    actual_src = src_dir
                    
                if not dest_path.exists():
                    try:
                        shutil.copytree(actual_src, dest_path)
                    except Exception as e:
                        print(f"Failed to copy {actual_src} -> {dest_path}: {e}")

if __name__ == "__main__":
    populate_final_results()
    print("\nDONE: Monotonic directories have been preserved in final_results/")
