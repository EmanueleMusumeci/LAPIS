import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

def verify_imports():
    print("Verifying imports...")
    try:
        from src.costl.simulators.base_simulator import BaseSimulator
        print("✅ BaseSimulator imported successfully")
        
        # Check if new methods exist
        if hasattr(BaseSimulator, 'verify_plan') and hasattr(BaseSimulator, 'step_and_verify'):
            print("✅ BaseSimulator has verification methods")
        else:
            print("❌ BaseSimulator missing verification methods")
            
    except ImportError as e:
        print(f"❌ Failed to import BaseSimulator: {e}")

    try:
        from src.costl.pipelines.lexicon import LexiconPipeline
        print("✅ LexiconPipeline imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import LexiconPipeline: {e}")

def verify_lexicon_integration():
    print("\nVerifying lexicon integration...")
    # Add lexicon path manually to check if it exists
    lexicon_path = os.path.abspath("third-party/lexicon_neurips")
    if os.path.exists(lexicon_path):
        print(f"✅ Lexicon directory found at {lexicon_path}")
        sys.path.append(lexicon_path)
        try:
            import lexicon
            print("✅ lexicon module imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import lexicon module: {e}")
    else:
        print(f"❌ Lexicon directory not found at {lexicon_path}")

if __name__ == "__main__":
    verify_imports()
    verify_lexicon_integration()
