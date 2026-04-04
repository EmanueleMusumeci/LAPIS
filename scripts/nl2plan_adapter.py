import os
import shutil
from pathlib import Path

def adapt_llmpp_to_nl2plan(source_base, target_base):
    source_base = Path(source_base)
    target_base = Path(target_base)
    
    # Domains to process (as specified in task_0_overview.md)
    target_domains = ['blocksworld', 'barman', 'storage', 'termes', 'grippers', 'floortile', 'tyreworld']
    
    for domain in target_domains:
        source_domain_dir = source_base / domain
        if not source_domain_dir.exists():
            print(f"Warning: Source domain directory {source_domain_dir} not found.")
            continue
            
        target_domain_dir = target_base / domain
        target_domain_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Adapt domain description
        source_domain_nl = source_domain_dir / "domain.nl"
        if source_domain_nl.exists():
            shutil.copy(source_domain_nl, target_domain_dir / "desc.txt")
        else:
            print(f"Warning: {source_domain_nl} not found.")
            
        # 2. Adapt problems
        # LLM+P has p01.nl, p02.nl, etc.
        # NL2Plan expects task1.txt, task2.txt, etc.
        for i in range(1, 21):
            source_problem_nl = source_domain_dir / f"p{i:02d}.nl"
            if source_problem_nl.exists():
                shutil.copy(source_problem_nl, target_domain_dir / f"task{i}.txt")
            else:
                # Some might not have zero-padding or different naming
                alt_source = source_domain_dir / f"p{i}.nl"
                if alt_source.exists():
                    shutil.copy(alt_source, target_domain_dir / f"task{i}.txt")
                else:
                    print(f"Warning: Problem {i} for {domain} not found.")

if __name__ == "__main__":
    SOURCE = "third-party/llm-pddl/domains"
    TARGET = "third-party/NL2Plan/domains"
    
    print(f"Adapting LLM+P data from {SOURCE} to {TARGET}...")
    adapt_llmpp_to_nl2plan(SOURCE, TARGET)
    print("Done.")
