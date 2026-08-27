import subprocess
import sys
import shutil
import venv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
VENV_DIR = PROJECT_ROOT / ".venv311"          # consistent with README
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"
RAW_ANTI_AI_FILE = PROJECT_ROOT / "anti_ai_skill_raw.md"

def run_command(cmd, cwd=None, env=None):
    """Run a command and return True if success."""
    print(f"\n>>> {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    result = subprocess.run(cmd, cwd=cwd, env=env, shell=(isinstance(cmd, str)))
    return result.returncode == 0

def get_python_version(python_exe):
    """Return (major, minor) or None."""
    try:
        out = subprocess.check_output([python_exe, "--version"], text=True, stderr=subprocess.STDOUT)
        # e.g., "Python 3.11.7"
        parts = out.strip().split()
        if len(parts) >= 2:
            ver = parts[1].split(".")
            return (int(ver[0]), int(ver[1]))
    except Exception:
        return None
    return None

def find_python_311_or_312():
    """Try to find a Python 3.11 or 3.12 executable."""
    # First check if current Python is suitable
    cur = sys.executable
    ver = get_python_version(cur)
    if ver and ver[0] == 3 and ver[1] in (11, 12):
        return cur

    # Try py launcher
    py_exe = shutil.which("py")
    if py_exe:
        for minor in (11, 12):
            try:
                out = subprocess.check_output([py_exe, f"-3.{minor}", "--version"], text=True, stderr=subprocess.STDOUT)
                if f"3.{minor}" in out:
                    return py_exe, f"-3.{minor}"
            except Exception:
                continue
    return None

def create_venv(python_exe):
    if VENV_DIR.exists():
        print(f"Virtual environment already exists at {VENV_DIR}. Skipping creation.")
        return True
    print(f"Creating virtual environment at {VENV_DIR} using {python_exe}...")
    if isinstance(python_exe, tuple):
        cmd = [python_exe[0], python_exe[1], "-m", "venv", str(VENV_DIR)]
    else:
        cmd = [python_exe, "-m", "venv", str(VENV_DIR)]
    return run_command(cmd)

def get_venv_python():
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "python.exe"
    else:
        return VENV_DIR / "bin" / "python"

def install_requirements(venv_python):
    print("\nInstalling requirements...")
    run_command([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"])
    return run_command([str(venv_python), "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)])

def download_spacy_model(venv_python):
    print("\nDownloading spaCy model...")
    # Try versioned command first (worked previously)
    success = run_command([str(venv_python), "-m", "spacy", "download", "en_core_web_md-3.7.1"])
    if success:
        return True
    # Fallback to pip package
    success = run_command([str(venv_python), "-m", "pip", "install", "en-core-web-md"])
    return success

def download_nltk_data(venv_python):
    print("\nDownloading NLTK data...")
    cmd = [str(venv_python), "-c", "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"]
    return run_command(cmd)

def chunk_anti_ai_skill(venv_python):
    if not RAW_ANTI_AI_FILE.exists():
        print(f"Warning: {RAW_ANTI_AI_FILE.name} not found. Skipping anti-AI chunk generation.")
        print("Please place the raw anti-AI skill markdown in the project root and run the chunk script manually if needed.")
        return True  # not fatal
    print("\nChunking anti-AI skill...")
    cmd = [str(venv_python), "scripts/chunk_anti_ai_skill.py"]
    return run_command(cmd)

def run_pipeline(venv_python):
    print("\nRunning full pipeline...")
    cmd = [str(venv_python), "scripts/run_pipeline.py"]
    return run_command(cmd)

def main():
    print("=== Personalized Humanizer Setup ===")
    # 1. Find suitable Python
    python_info = find_python_311_or_312()
    if python_info is None:
        print("ERROR: Python 3.11 or 3.12 not found. Install one and try again.")
        sys.exit(1)

    # 2. Create venv
    if not create_venv(python_info):
        print("Failed to create virtual environment.")
        sys.exit(1)

    venv_python = get_venv_python()
    if not venv_python.exists():
        print("Virtual environment Python not found.")
        sys.exit(1)

    # 3. Install requirements
    if not install_requirements(venv_python):
        print("Failed to install requirements.")
        sys.exit(1)

    # 4. Download spaCy model
    if not download_spacy_model(venv_python):
        print("Failed to download spaCy model.")
        sys.exit(1)

    # 5. Download NLTK data
    if not download_nltk_data(venv_python):
        print("Failed to download NLTK data.")
        sys.exit(1)

    # 6. Chunk anti-AI skill (if raw file exists)
    if not chunk_anti_ai_skill(venv_python):
        print("Failed to chunk anti-AI skill. Continue? (y/n)")
        ans = input().lower()
        if ans != 'y':
            sys.exit(1)

    print("\nSetup completed successfully!")

    # 7. Optionally run pipeline
    print("\nDo you want to run the full pipeline now? (y/n)")
    ans = input().lower().strip()
    if ans == 'y':
        if not run_pipeline(venv_python):
            print("Pipeline failed.")
            sys.exit(1)
        print("\nPipeline completed!")
    else:
        print("You can run the pipeline later with: python scripts/run_pipeline.py")
        print("(Make sure to activate the virtual environment first, or use the venv's Python directly.)")

if __name__ == "__main__":
    main()