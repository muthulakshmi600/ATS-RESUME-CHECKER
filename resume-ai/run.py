#!/usr/bin/env python3
"""
ResumeAI - Unified Application Launcher
Starts the Flask backend server and automatically opens the application in your default browser.
"""

import os
import sys
import webbrowser
import threading
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure backend directory is in python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(CURRENT_DIR, 'backend')
sys.path.insert(0, BACKEND_DIR)

from app import app, init_db

PORT = int(os.environ.get('PORT', 5050))
URL = f"http://127.0.0.1:{PORT}"

def open_browser():
    time.sleep(1.2)
    print(f"\n🌐 Opening ResumeAI in your browser: {URL}\n")
    try:
        webbrowser.open(URL)
    except Exception:
        pass

def print_banner():
    banner = f"""
======================================================================
  💼 ResumeAI — ATS Resume Score Checker
  Tagline: "Build a Resume That Gets Noticed."
======================================================================
  🚀 Status: Application Started Successfully!
  🌐 Local URL: {URL}
  
  🔑 Demo Login Credentials (Any non-empty values work!):
     • Email:    test@gmail.com   (or muthu@gmail.com)
     • Password: 12345            (or any password)

  📋 Features:
     • Drag & Drop PDF / DOCX Resume Text Extraction
     • 6-Factor Transparent Rule-Based ATS Scoring (0-100)
     • Keyword & Skills Gap Alignment Engine
     • SQLite Database + LocalStorage Hybrid Persistence
======================================================================
  Press Ctrl+C to stop the server.
"""
    print(banner)

if __name__ == '__main__':
    # Initialize DB
    init_db()

    # Launch browser in separate thread
    threading.Thread(target=open_browser, daemon=True).start()

    print_banner()
    app.run(host='0.0.0.0', port=PORT, debug=False)
