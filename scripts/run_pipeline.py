import subprocess
import sys
from pathlib import Path

# Ensure we are running from project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Define the core pipeline steps in order
PIPELINE_STEPS = [
    "scripts/ingest.py",
    "scripts/extract_features.py",
    "scripts/build_guide_from_template.py",
    "scripts/generate_few_shot_prompt.py",
    "scripts/summarize.py",
    "scripts/generate_guide.py",
    "scripts/merge_guides.py",
]

def run_step(script_path):
    """Run a single script and return True if successful."""
    print(f"\n{'='*60}")
    print(f"Running: {script_path}")
    print(f"{'='*60}")
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / script_path)],
        cwd=PROJECT_ROOT,
        capture_output=False,  # show output directly in console
        text=True,
    )
    return result.returncode == 0

def main():
    print("Starting Personalized Humanizer Pipeline...")
    for step in PIPELINE_STEPS:
        success = run_step(step)
        if not success:
            print(f"\nPipeline failed at step: {step}")
            sys.exit(1)
    print("\nPipeline completed successfully.")
    print(f"Final output: {PROJECT_ROOT / 'data' / 'output' / 'Personalized-Humanizer-Complete.md'}")

if __name__ == "__main__":
    main()