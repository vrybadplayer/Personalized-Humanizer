import subprocess
import sys
import shutil
from pathlib import Path

# Add project root to sys.path to import settings
sys.path.append(str(Path(__file__).resolve().parent))

from config.settings import (
    VENV_DIR,
    REQUIREMENTS_FILE,
    RAW_ANTI_AI_FILE,
    SUPPORTED_PYTHON_MINORS,
    SPACY_MODEL_DOWNLOAD,
    SPACY_MODEL_PIP,
    NLTK_DOWNLOADS,
    CHUNK_ANTI_AI_SCRIPT,
    PIPELINE_SCRIPT,
)

def run_command(cmd, cwd=None, env=None):
    """Run a command and return True if success."""
    print(f"\n>>> {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    result = subprocess.run(cmd, cwd=cwd, env=env, shell=(isinstance(cmd, str)))
    return result.returncode == 0

def get_python_version(python_exe):
    """Return (major, minor) or None."""
    try:
        out = subprocess.check_output([python_exe, "--version"], text=True, stderr=subprocess.STDOUT)
        parts = out.strip().split()
        if len(parts) >= 2:
            ver = parts[1].split(".")
            return (int(ver[0]), int(ver[1]))
    except Exception:
        return None
    return None

def find_supported_python():
    """Try to find a Python 3.11 or 3.12 executable."""
    # First check current Python
    cur = sys.executable
    ver = get_python_version(cur)
    if ver and ver[0] == 3 and ver[1] in SUPPORTED_PYTHON_MINORS:
        return cur

    # Try py launcher
    py_exe = shutil.which("py")
    if py_exe:
        for minor in SUPPORTED_PYTHON_MINORS:
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
    # Try versioned command first
    success = run_command([str(venv_python), "-m", "spacy", "download", SPACY_MODEL_DOWNLOAD])
    if success:
        return True
    # Fallback to pip package
    success = run_command([str(venv_python), "-m", "pip", "install", SPACY_MODEL_PIP])
    return success

def download_nltk_data(venv_python):
    print("\nDownloading NLTK data...")
    packages = "', '".join(NLTK_DOWNLOADS)
    cmd = [
        str(venv_python), "-c",
        f"import nltk, pathlib, sys; pathlib.Path(sys.prefix + '/nltk_data').mkdir(parents=True, exist_ok=True); "
        f"nltk.download('{packages}', download_dir=sys.prefix + '/nltk_data')"
    ]
    return run_command(cmd)

def chunk_anti_ai_skill(venv_python):
    if not RAW_ANTI_AI_FILE.exists():
        print(f"Warning: {RAW_ANTI_AI_FILE.name} not found. Skipping anti-AI chunk generation.")
        print("Please place the raw anti-AI skill markdown in the project root and run the chunk script manually if needed.")
        return True  # not fatal
    print("\nChunking anti-AI skill...")
    cmd = [str(venv_python), str(CHUNK_ANTI_AI_SCRIPT)]
    return run_command(cmd)

def run_pipeline(venv_python):
    print("\nRunning full pipeline...")
    cmd = [str(venv_python), str(PIPELINE_SCRIPT)]
    return run_command(cmd)

def main():
    print("=== Personalized Humanizer Setup ===")
    # 1. Find suitable Python
    python_info = find_supported_python()
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