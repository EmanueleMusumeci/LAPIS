import os
import sys

# Add src to Python Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

try:
    from costl.pipelines.multi_level_planning import MultiLevelPlanningPipeline
except ImportError as e:
    print(f"Failed to import pipeline: {e}")
    sys.exit(1)

def main():
    print("Testing Pipeline on Blocksworld Sample 112 (Batch 1)")
    
    # Configure pipeline for blocksworld
    pipeline = MultiLevelPlanningPipeline(
        high_level_domain_name='blocksworld',
        batch_id='batch_1'
    )
    
    # Run the specific task
    try:
        pipeline.run_task(112)
        print("\nTest completed successfully. Check the pipeline_summary.txt and full_plan.txt in the data directory.")
    except Exception as e:
        print(f"\nTest failed with exception: {e}")

if __name__ == "__main__":
    main()
