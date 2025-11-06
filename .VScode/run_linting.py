# .vscode/run_linting.py
import os
import subprocess
import sys

# Establish repo root
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def run(cmd):
    """Run a shell command and stop on failure."""
    print(f"\n Running: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        sys.exit(result.returncode)

def main():
    print(" Linting and Structure Check Started")
    os.environ["PYTHONPATH"] = ROOT

    # Step 1 - Run flake8 for fatal errors only
    run([
        "flake8", 
        "generator", 
        "ai_core", 
        "ai_validation", 
        "ai_monitoring", 
        "--count", 
        "--select=E9,F63,F7,F82", 
        "--show-source", 
        "--statistics"
    ])

    # Step 2 - Run pylint, ignoring missing docstrings
    run([
        "pylint", 
        "generator", 
        "ai_core", 
        "ai_validation", 
        "ai_monitoring", 
        "--disable=C0114,C0115,C0116"
    ])

    # Step 3 - Syntax validation
    run(["python3", "-m", "py_compile", "ai_core/orchestrator.py"])

    print("\n All structure and linting checks passed successfully!")

if __name__ == "__main__":
    main()
