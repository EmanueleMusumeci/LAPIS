#!/bin/bash
set -e

# Delete unused files
echo "Deleting unused files..."
rm -rf third-party/lexicon_neurips
rm -f run_lexicon_pipeline.py setup_lexicon_env.sh src/lapis/pipelines/lexicon.py

# Rename the main directory
echo "Renaming src/lapis to src/lapis..."
mv src/lapis src/lapis

# Rename the specialized evaluation pipeline
echo "Renaming lapis_low_level.py..."
mv src/lapis/pipelines/lapis_low_level.py src/lapis/pipelines/lapis_low_level.py

# Bulk Replacement across the code
echo "Running string replacements across all tracked/relevant files..."
find . -type f \( -name "*.py" -o -name "*.sh" -o -name "*.md" \) \
  -not -path "*/third-party/*" \
  -not -path "*/.venv/*" \
  -not -path "*/.git/*" \
  -not -path "*/.streamlit/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/.conda_env/*" \
  -exec sed -i \
  -e 's/lapis/lapis/g' \
  -e 's/LAPIS/LAPIS/g' \
  -e 's/LAPIS/LAPIS/g' \
  -e 's/LAPISLowLevelPipeline/LAPISLowLevelPipeline/g' \
  -e 's/lapis_low_level/lapis_low_level/g' {} +

echo "Cleanup successfully completed."
