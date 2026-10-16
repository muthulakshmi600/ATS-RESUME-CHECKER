"""
Launcher for NexusAI Chat Application.
Checks dependencies, ensures database tables are initialized, and starts the server.
"""

import sys
import os
import socket

# Ensure current directory is on python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from ai_chat_app.database import init_db
from ai_chat_app.app import app


def find_free_port(start_port=5000, max_attempts=20):
    """Finds an available TCP port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return start_port


def main():
    print("=" * 65)
    print("           NEXUS AI - INTELLIGENT CHAT WORKSPACE")
    print("=" * 65)
    print("Initializing SQLite Database...")
    init_db()
    print("Database ready.")

    preferred_port = int(os.environ.get("PORT", 5000))
    port = find_free_port(preferred_port)

    print(f"\n🚀 NexusAI Server starting at:")
    print(f"   Local:   http://127.0.0.1:{port}")
    print(f"   Network: http://localhost:{port}\n")
    print("Features ready:")
    print(" ✓ Sign Up / Login with secure password hashing & strength meter")
    print(" ✓ Dashboard with Pinned Chats & Chat History")
    print(" ✓ Real-time Streaming AI Responses (SSE) + Gemini 3.8 / 2.5 Flash")
    print(" ✓ Multi-format File Analysis (PDF, DOCX, CSV, Excel, PPTX, Images)")
    print(" ✓ File Library & Previews")
    print(" ✓ Projects Workspace & Custom Guidelines")
    print(" ✓ Global Search (Ctrl + K)")
    print(" ✓ Speech-to-Text Microphone integration")
    print(" ✓ Profile, Security/Password Change, & Export")
    print("=" * 65)

    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
