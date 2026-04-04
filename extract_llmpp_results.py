import os
import json
import pandas as pd
from pathlib import Path

def aggregate_results():
    base_dir = Path("/DATA/lapis/third-party/llm-pddl/experiments/run0/results/llm_ic_pddl")
    all_results = []
    
    if not base_dir.exists():
        print(f"Directory {base_dir} does not exist.")
        return

    domains = [d for d in base_dir.iterdir() if d.is_dir()]
    
    summary = []
    for domain in domains:
        domain_name = domain.name
        manifolds = list(domain.glob("*_manifold.json"))
        
        successes = 0
        total_time = 0
        total_plan_length = 0
        total_valid = 0
        
        for mf_path in manifolds:
            with open(mf_path, 'r') as f:
                data = json.load(f)
                if data.get("planning_successful"):
                    successes += 1
                if data.get("val_valid"):
                    total_valid += 1
                total_time += data.get("timing", {}).get("total_llm_s", 0)
                total_plan_length += data.get("plan_length", 0)
        
        count = len(manifolds)
        avg_time = total_time / count if count > 0 else 0
        avg_plan_length = total_plan_length / count if count > 0 else 0
        
        summary.append({
            "Domain": domain_name,
            "Success Rate (%)": (successes / 20) * 100,
            "Valid (%)": (total_valid / 20) * 100,
            "Avg LLM Time (s)": avg_time,
            "Avg Plan Steps": avg_plan_length,
            "Total Runs": count
        })
        
    df = pd.DataFrame(summary)
    print(df.to_string())
    
    # Save to a report (assuming it can handle md saving internally or use a simpler format)
    try:
        with open("/DATA/lapis/TRUE_LLMPP_BASELINE_RESULTS.md", "w") as rf:
            rf.write("# True LLM+P Baseline Results (Claude-3.5-Sonnet)\n\n")
            rf.write(df.to_markdown(index=False))
            rf.write("\n\n*Note: These benchmarks were run using the original LLM+P implementation (Few-Shot Context + GT domain) with the Claude-3.5-Sonnet engine for a fair comparison.*")
    except ImportError:
         with open("/DATA/lapis/TRUE_LLMPP_BASELINE_RESULTS.md", "w") as rf:
            rf.write("# True LLM+P Baseline Results (Claude-3.5-Sonnet)\n\n")
            rf.write(df.to_string(index=False))
            rf.write("\n\n*Note: These benchmarks were run using the original LLM+P implementation (Few-Shot Context + GT domain) with the Claude-3.5-Sonnet engine for a fair comparison. (Tabulate missing, using plain text)*")

if __name__ == "__main__":
    aggregate_results()
