#!/usr/bin/env python3
"""
Root Launcher for ResumeAI.
Directly invokes the ResumeAI application in resume-ai/run.py.
"""

import os
import sys
import subprocess

if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(current_dir, 'resume-ai')
    script_path = os.path.join(target_dir, 'run.py')
    
    if os.path.exists(script_path):
        os.chdir(target_dir)
        subprocess.call([sys.executable, 'run.py'])
    else:
        print(f"Error: {script_path} not found.")
