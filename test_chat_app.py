"""
Automated Test Suite for NexusAI Chat Application.
Verifies the complete end-to-end user flow:
Sign Up -> Login -> Dashboard -> New Chat -> AI Response -> Save Chat ->
Pin Chat -> Search Chat -> Upload File -> File QA -> Library -> Project ->
Settings -> Change Password -> Logout
"""

import sys
import os
import io
import json
import time

# Ensure current directory is on python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from ai_chat_app.database import init_db, get_db
from ai_chat_app.app import app

def run_tests():
    print("=" * 70)
    print("      RUNNING NEXUS AI APPLICATION VERIFICATION SUITE")
    print("=" * 70)

    # Initialize DB
    init_db()

    # Flask test client
    client = app.test_client()

    test_user_name = "Alex Johnson"
    test_user_email = f"alex_test_{int(time.time())}@example.com"
    test_password = "SecurePassword123!"
    new_password = "NewStrongPassword456!"

    passed = 0
    total = 14

    # -------------------------------------------------------------
    # 1. SIGN UP
    # -------------------------------------------------------------
    print("\n[Step 1] Testing Sign Up...")
    signup_payload = {
        "name": test_user_name,
        "email": test_user_email,
        "password": test_password,
        "confirm_password": test_password
    }
    res = client.post("/api/auth/signup", json=signup_payload)
    assert res.status_code == 201, f"Signup failed: {res.get_json()}"
    data = res.get_json()
    assert data["success"] is True
    print(f" ✓ Sign Up passed! User registered: {test_user_email}")
    passed += 1

    # -------------------------------------------------------------
    # 2. LOGIN
    # -------------------------------------------------------------
    print("\n[Step 2] Testing Login...")
    login_payload = {
        "email": test_user_email,
        "password": test_password,
        "remember_me": True
    }
    res = client.post("/api/auth/login", json=login_payload)
    assert res.status_code == 200, f"Login failed: {res.get_json()}"
    data = res.get_json()
    assert data["success"] is True
    user_id = data["user"]["id"]
    print(f" ✓ Login passed! User ID: {user_id}")
    passed += 1

    # -------------------------------------------------------------
    # 3. DASHBOARD / AUTH STATUS
    # -------------------------------------------------------------
    print("\n[Step 3] Testing Dashboard & Auth Status...")
    res = client.get("/api/auth/status")
    assert res.status_code == 200
    data = res.get_json()
    assert data["authenticated"] is True
    assert data["user"]["email"] == test_user_email
    print(" ✓ Dashboard session verified!")
    passed += 1

    # -------------------------------------------------------------
    # 4. NEW CHAT
    # -------------------------------------------------------------
    print("\n[Step 4] Testing New Chat Creation...")
    res = client.post("/api/chats", json={"title": "New Conversation"})
    assert res.status_code == 201
    chat = res.get_json()
    chat_id = chat["id"]
    print(f" ✓ New Chat created with ID: {chat_id}")
    passed += 1

    # -------------------------------------------------------------
    # 5. AI RESPONSE & STREAMING
    # -------------------------------------------------------------
    print("\n[Step 5] Testing AI Message Streaming...")
    msg_payload = {
        "content": "Explain Python and its key advantages.",
        "attachments": []
    }
    res = client.post(f"/api/chats/{chat_id}/message", json=msg_payload)
    assert res.status_code == 200
    streamed_text = res.get_data(as_text=True)
    assert "data: " in streamed_text
    assert '"done": true' in streamed_text
    print(f" ✓ AI Stream received successfully! Chunk length: {len(streamed_text)} chars")
    passed += 1

    # -------------------------------------------------------------
    # 6. SAVE CHAT & AUTO TITLE
    # -------------------------------------------------------------
    print("\n[Step 6] Testing Save Chat & Auto-generated Title...")
    res = client.get(f"/api/chats/{chat_id}")
    assert res.status_code == 200
    chat_details = res.get_json()
    assert len(chat_details["messages"]) >= 2  # user + assistant
    print(f" ✓ Chat automatically saved with title: '{chat_details['title']}' and {len(chat_details['messages'])} messages")
    passed += 1

    # -------------------------------------------------------------
    # 7. PIN CHAT
    # -------------------------------------------------------------
    print("\n[Step 7] Testing Pin & Unpin Chat...")
    # Pin
    res = client.patch(f"/api/chats/{chat_id}", json={"is_pinned": 1})
    assert res.status_code == 200
    assert res.get_json()["is_pinned"] is True

    # Verify in chat list
    chats_res = client.get("/api/chats").get_json()
    assert any(c["id"] == chat_id for c in chats_res["pinned"])
    print(" ✓ Chat pinned successfully to Pinned Chats section!")

    # Unpin
    res = client.patch(f"/api/chats/{chat_id}", json={"is_pinned": 0})
    assert res.status_code == 200
    assert res.get_json()["is_pinned"] is False
    print(" ✓ Chat unpinned successfully!")
    passed += 1

    # -------------------------------------------------------------
    # 8. SEARCH CHAT (Ctrl + K)
    # -------------------------------------------------------------
    print("\n[Step 8] Testing Global Search (Ctrl + K)...")
    res = client.get("/api/search?q=Python")
    assert res.status_code == 200
    search_data = res.get_json()
    assert len(search_data["results"]) > 0
    print(f" ✓ Search returned {len(search_data['results'])} matching results for query 'Python'!")
    passed += 1

    # -------------------------------------------------------------
    # 9. UPLOAD FILE
    # -------------------------------------------------------------
    print("\n[Step 9] Testing File Upload (CSV & TXT)...")
    csv_content = b"Candidate,Skill,Score\nAlice,Python,95\nBob,Machine Learning,90\nCharlie,Data Analysis,88\n"
    data = {
        "file": (io.BytesIO(csv_content), "candidate_skills.csv")
    }
    res = client.post("/api/upload", data=data, content_type="multipart/form-data")
    assert res.status_code == 201, f"Upload error: {res.get_json()}"
    file_info = res.get_json()["file"]
    file_id = file_info["id"]
    print(f" ✓ Uploaded and parsed file: {file_info['name']} (ID: {file_id}, Size: {file_info['size']} bytes)")
    passed += 1

    # -------------------------------------------------------------
    # 10. FILE Q&A WITH AI
    # -------------------------------------------------------------
    print("\n[Step 10] Testing File Q&A inside Conversation...")
    qa_payload = {
        "content": "Who has the highest score in the attached candidate list?",
        "attachments": [{"id": file_id, "name": "candidate_skills.csv", "size": file_info["size"], "type": "CSV"}]
    }
    res = client.post(f"/api/chats/{chat_id}/message", json=qa_payload)
    assert res.status_code == 200
    qa_stream = res.get_data(as_text=True)
    assert "candidate_skills.csv" in qa_stream or "Analysis" in qa_stream or "Candidate" in qa_stream
    print(" ✓ File QA streaming completed successfully with file context attached!")
    passed += 1

    # -------------------------------------------------------------
    # 11. LIBRARY MANAGEMENT
    # -------------------------------------------------------------
    print("\n[Step 11] Testing Library Listing, Preview, Rename & Download...")
    # List
    res = client.get("/api/library")
    assert res.status_code == 200
    lib_data = res.get_json()
    assert lib_data["count"] >= 1

    # Preview
    res = client.get(f"/api/files/{file_id}/preview")
    assert res.status_code == 200
    assert "Candidate" in res.get_json()["preview"] or "Candidate" in res.get_json()["full_text"]

    # Rename
    res = client.patch(f"/api/files/{file_id}", json={"name": "updated_candidate_skills.csv"})
    assert res.status_code == 200
    assert res.get_json()["name"] == "updated_candidate_skills.csv"

    # Download
    res = client.get(f"/api/files/{file_id}/download")
    assert res.status_code == 200
    assert b"Alice,Python,95" in res.data
    print(" ✓ Library features (listing, preview, rename, download) verified!")
    passed += 1

    # -------------------------------------------------------------
    # 12. PROJECTS
    # -------------------------------------------------------------
    print("\n[Step 12] Testing Projects Workspace...")
    proj_payload = {
        "name": "Python Learning Project",
        "description": "Comprehensive project to master Python programming with AI assistance.",
        "color": "#6366f1",
        "system_instructions": "Always provide clean Python code with type annotations."
    }
    res = client.post("/api/projects", json=proj_payload)
    assert res.status_code == 201
    proj_id = res.get_json()["id"]

    # Link chat to project
    res = client.patch(f"/api/chats/{chat_id}", json={"project_id": proj_id})
    assert res.status_code == 200

    # Get project details
    res = client.get(f"/api/projects/{proj_id}")
    assert res.status_code == 200
    proj_details = res.get_json()
    assert len(proj_details["chats"]) >= 1
    print(f" ✓ Project '{proj_details['name']}' created with associated chat!")
    passed += 1

    # -------------------------------------------------------------
    # 13. SETTINGS & PASSWORD CHANGE
    # -------------------------------------------------------------
    print("\n[Step 13] Testing Settings & Password Change...")
    # Profile update
    res = client.post("/api/settings/profile", json={"name": "Alex J. Updated", "email": test_user_email, "avatar": "avatar-2"})
    assert res.status_code == 200

    # Change password
    pw_payload = {
        "current_password": test_password,
        "new_password": new_password,
        "confirm_new_password": new_password
    }
    res = client.post("/api/settings/password", json=pw_payload)
    assert res.status_code == 200

    # Test export
    res = client.get("/api/settings/export")
    assert res.status_code == 200
    assert b"conversations" in res.data
    print(" ✓ Profile updated, password changed, and conversations exported successfully!")
    passed += 1

    # -------------------------------------------------------------
    # 14. LOGOUT & RE-LOGIN VERIFICATION
    # -------------------------------------------------------------
    print("\n[Step 14] Testing Logout & Re-login with New Password...")
    # Logout
    res = client.post("/api/auth/logout")
    assert res.status_code == 200

    # Verify session is cleared
    res = client.get("/api/auth/status")
    assert res.get_json()["authenticated"] is False

    # Old password should fail
    res = client.post("/api/auth/login", json={"email": test_user_email, "password": test_password})
    assert res.status_code == 401

    # New password should succeed
    res = client.post("/api/auth/login", json={"email": test_user_email, "password": new_password})
    assert res.status_code == 200
    print(" ✓ Logout verified, old password rejected, and new password logged in successfully!")
    passed += 1

    print("\n" + "=" * 70)
    print(f"  ALL {passed}/{total} END-TO-END WORKFLOW TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
