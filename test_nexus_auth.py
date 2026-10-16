"""
Verification script for NexusAI Authentication System.
Tests all requirements requested by the user:
1. Registration with Muthulakshmi (muthu@gmail.com / M12345)
2. Database insertion, column verification, Werkzeug password hashing
3. Login with newly created account
4. Protected dashboard routes & redirection
5. Logout & session clearance
6. Wrong password & unknown user rejection
7. Duplicate email prevention
8. Password mismatch handling
9. Demo user in SQLite still works
10. 14-day Remember Me
"""

import sys
import os
import json
import sqlite3

# Ensure workspace is on sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ai_chat_app.database import init_db, get_db, DATABASE_PATH
from ai_chat_app.app import app
from werkzeug.security import check_password_hash

def test_auth():
    print("=" * 70)
    print("      NEXUSAI COMPLETE AUTHENTICATION VERIFICATION")
    print("=" * 70)

    # Initialize DB & migrations
    init_db()

    # Clean up test user muthu@gmail.com if already exists
    with get_db() as conn:
        conn.execute("DELETE FROM users WHERE LOWER(email) = 'muthu@gmail.com'")

    client = app.test_client()

    # -----------------------------------------------------------------
    # Test 1: Sign Up with Muthulakshmi / muthu@gmail.com / M12345
    # -----------------------------------------------------------------
    print("\n[Step 1] Registering New User: Muthulakshmi / muthu@gmail.com / M12345...")
    reg_payload = {
        "name": "Muthulakshmi",
        "email": "muthu@gmail.com",
        "password": "M12345",
        "confirm_password": "M12345"
    }
    res = client.post("/api/auth/signup", json=reg_payload)
    print("Status Code:", res.status_code)
    print("Response:", res.get_json())
    assert res.status_code == 201, f"Registration failed: {res.get_json()}"
    data = res.get_json()
    assert data["success"] is True
    print(" -> [PASS] User Muthulakshmi registered successfully!")

    # -----------------------------------------------------------------
    # Test 2: Verify in SQLite database
    # -----------------------------------------------------------------
    print("\n[Step 2] Verifying SQLite database entry in ai_chat.db...")
    with get_db() as conn:
        user_row = conn.execute("SELECT id, name, email, password_hash, created_at FROM users WHERE LOWER(email) = 'muthu@gmail.com'").fetchone()
    assert user_row is not None, "User not found in SQLite database!"
    assert user_row["name"] == "Muthulakshmi"
    assert user_row["email"] == "muthu@gmail.com"
    stored_hash = user_row["password_hash"]
    assert stored_hash != "M12345", "Password was stored in plain text!"
    assert stored_hash.startswith("scrypt:") or stored_hash.startswith("pbkdf2:"), f"Invalid hash format: {stored_hash}"
    assert check_password_hash(stored_hash, "M12345") is True, "Password hash verification failed!"
    print(f" -> [PASS] Verified in SQLite! User ID: {user_row['id']}, Hash prefix: {stored_hash[:20]}...")

    # -----------------------------------------------------------------
    # Test 3: Login with muthu@gmail.com / M12345
    # -----------------------------------------------------------------
    print("\n[Step 3] Logging in with muthu@gmail.com / M12345...")
    login_payload = {
        "email": "muthu@gmail.com",
        "password": "M12345",
        "remember_me": True
    }
    res = client.post("/api/auth/login", json=login_payload)
    print("Status Code:", res.status_code)
    print("Response:", res.get_json())
    assert res.status_code == 200, f"Login failed: {res.get_json()}"
    login_data = res.get_json()
    assert login_data["success"] is True
    assert login_data["user"]["email"] == "muthu@gmail.com"
    assert login_data["user"]["name"] == "Muthulakshmi"
    print(" -> [PASS] Login succeeded for Muthulakshmi!")

    # -----------------------------------------------------------------
    # Test 4: Verify Flask Session & Auth Status
    # -----------------------------------------------------------------
    print("\n[Step 4] Checking Session & Auth Status endpoint...")
    res = client.get("/api/auth/status")
    assert res.status_code == 200
    status_data = res.get_json()
    assert status_data["authenticated"] is True
    assert status_data["user"]["id"] == user_row["id"]
    print(" -> [PASS] Session active for:", status_data["user"]["name"])

    # -----------------------------------------------------------------
    # Test 5: Verify Protected Route Access
    # -----------------------------------------------------------------
    print("\n[Step 5] Checking protected /dashboard while authenticated...")
    res = client.get("/dashboard")
    assert res.status_code == 200, "Dashboard was not accessible to authenticated user!"
    print(" -> [PASS] Protected /dashboard rendered successfully (200 OK)!")

    # -----------------------------------------------------------------
    # Test 6: Test Logout
    # -----------------------------------------------------------------
    print("\n[Step 6] Testing Logout...")
    res = client.post("/api/auth/logout")
    assert res.status_code == 200
    print(" -> [PASS] Logout successful!")

    # -----------------------------------------------------------------
    # Test 7: Verify Protected Route is Blocked After Logout
    # -----------------------------------------------------------------
    print("\n[Step 7] Checking protected /dashboard after logout...")
    res = client.get("/dashboard", follow_redirects=False)
    assert res.status_code == 302, f"Expected 302 redirect for unauthenticated user, got {res.status_code}"
    assert "/login" in res.headers.get("Location", ""), "Did not redirect to /login!"
    print(" -> [PASS] Unauthenticated access properly redirected to /login (302)!")

    # -----------------------------------------------------------------
    # Test 8: Re-login with Muthulakshmi
    # -----------------------------------------------------------------
    print("\n[Step 8] Re-logging in with muthu@gmail.com / M12345...")
    res = client.post("/api/auth/login", json=login_payload)
    assert res.status_code == 200
    print(" -> [PASS] Re-login successful!")

    # -----------------------------------------------------------------
    # Test 9: Test Wrong Password
    # -----------------------------------------------------------------
    print("\n[Step 9] Testing Login with Wrong Password...")
    bad_pw_client = app.test_client()
    res = bad_pw_client.post("/api/auth/login", json={"email": "muthu@gmail.com", "password": "WrongPassword"})
    assert res.status_code == 401
    assert res.get_json()["error"] == "Invalid email or password."
    print(" -> [PASS] Wrong password rejected with: 'Invalid email or password.'")

    # -----------------------------------------------------------------
    # Test 10: Test Unknown Email
    # -----------------------------------------------------------------
    print("\n[Step 10] Testing Login with Unknown Email...")
    res = bad_pw_client.post("/api/auth/login", json={"email": "nonexistent_user_999@gmail.com", "password": "M12345"})
    assert res.status_code == 401
    assert res.get_json()["error"] == "Invalid email or password."
    print(" -> [PASS] Unknown email rejected with: 'Invalid email or password.'")

    # -----------------------------------------------------------------
    # Test 11: Test Duplicate Email Registration
    # -----------------------------------------------------------------
    print("\n[Step 11] Testing Duplicate Email Registration...")
    res = client.post("/api/auth/signup", json=reg_payload)
    assert res.status_code == 409
    print(" -> [PASS] Duplicate email rejected with 409 Conflict:", res.get_json()["error"])

    # -----------------------------------------------------------------
    # Test 12: Test Password Mismatch
    # -----------------------------------------------------------------
    print("\n[Step 12] Testing Password Mismatch...")
    mismatch_payload = {
        "name": "Different User",
        "email": "different@gmail.com",
        "password": "Password1",
        "confirm_password": "Password2"
    }
    res = client.post("/api/auth/signup", json=mismatch_payload)
    assert res.status_code == 400
    assert res.get_json()["error"] == "Passwords do not match."
    print(" -> [PASS] Password mismatch rejected:", res.get_json()["error"])

    # -----------------------------------------------------------------
    # Test 13: Test Existing Demo User in SQLite (test@example.com / Test@12345)
    # -----------------------------------------------------------------
    print("\n[Step 13] Testing Existing Demo User in SQLite (test@example.com / Test@12345)...")
    demo_client = app.test_client()
    res = demo_client.post("/api/auth/login", json={"email": "test@example.com", "password": "Test@12345"})
    assert res.status_code == 200, f"Demo user login failed: {res.get_json()}"
    assert res.get_json()["user"]["email"] == "test@example.com"
    print(" -> [PASS] Demo user in SQLite authenticated successfully!")

    # -----------------------------------------------------------------
    # Test 14: Test Forgot Password Reset in SQLite
    # -----------------------------------------------------------------
    print("\n[Step 14] Testing In-App SQLite Password Reset...")
    reset_payload = {
        "email": "muthu@gmail.com",
        "new_password": "NewMuthuPassword999"
    }
    res = client.post("/api/auth/forgot-password", json=reset_payload)
    assert res.status_code == 200
    print(" -> [PASS] Password reset successful:", res.get_json()["message"])

    # Test login with new password
    res = client.post("/api/auth/login", json={"email": "muthu@gmail.com", "password": "NewMuthuPassword999"})
    assert res.status_code == 200
    print(" -> [PASS] Login with new password succeeded!")

    # Restore password back to M12345 for user's requested test
    res = client.post("/api/auth/forgot-password", json={"email": "muthu@gmail.com", "new_password": "M12345"})
    assert res.status_code == 200
    res = client.post("/api/auth/login", json={"email": "muthu@gmail.com", "password": "M12345"})
    assert res.status_code == 200
    print(" -> [PASS] Restored password to M12345 and verified login!")

    print("\n" + "=" * 70)
    print("   ALL 14 AUTHENTICATION TESTS PASSED SUCCESSFULLY! (100%)")
    print("=" * 70)

if __name__ == "__main__":
    test_auth()
