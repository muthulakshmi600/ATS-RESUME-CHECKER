"""
Convenience Runner Script for Fresher ATS Resume Analyzer.
Allows launching the Streamlit application directly from the root workspace directory:
    py run_fresher_ats.py
"""

import os
import sys
import subprocess

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(current_dir, "Fresher_ATS_Resume_Analyzer", "app.py")
    print(f"Launching Fresher ATS Resume Analyzer from: {app_path}")
    port = os.environ.get("STREAMLIT_PORT", "8502")
    subprocess.run([sys.executable, "-m", "streamlit", "run", app_path, "--server.port", port])
