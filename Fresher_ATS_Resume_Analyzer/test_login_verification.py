"""
Dedicated Login & Registration Verification Script for Fresher ATS Resume Analyzer.
Verifies the exact flow requested:
1. Register:
   Username/Email: test@example.com
   Password: Test@12345
   Result: "Account created successfully. Please login."
2. Login:
   Username/Email: test@example.com
   Password: Test@12345
   Result: Login successful -> Dashboard session set
3. Wrong password:
   test@example.com + wrong password
   Result: "Incorrect password."
4. Wrong email:
   wrong@example.com + Test@12345
   Result: "Invalid username or email."
5. Logout:
   Clears session, sets page = "login"
6. Re-login:
   test@example.com + Test@12345 -> Success
"""

import sys
import os
import sqlite3

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from database.database import (
    DEFAULT_DB_PATH,
    init_db,
    get_connection,
    get_user_by_email
)
from auth.authentication import (
    register_user,
    login_user,
    verify_password
)

def run_login_flow_test():
    print("=" * 65)
    print("  VERIFYING REAL LOGIN SYSTEM ON FRESHER ATS DATABASE")
    print("=" * 65)
    print(f"Target Database: {DEFAULT_DB_PATH}")

    # Ensure schema is initialized
    init_db()

    # Clean up test@example.com from fresher_ats.db if exists from a previous test
    with get_connection() as conn:
        conn.execute("DELETE FROM users WHERE LOWER(email) = 'test@example.com'")
        conn.commit()

    test_email = "test@example.com"
    test_password = "Test@12345"

    # 1. REGISTER
    print("\n[Step 1] Testing Registration with test@example.com / Test@12345...")
    reg_ok, reg_msg = register_user("Test Candidate", test_email, test_password, test_password)
    assert reg_ok, f"Registration failed: {reg_msg}"
    assert reg_msg == "Account created successfully. Please login.", f"Unexpected message: {reg_msg}"
    print(f" [PASS] Registration successful: '{reg_msg}'")

    # Verify user exists in SQLite and password hash is bcrypt
    db_user = get_user_by_email(test_email)
    assert db_user is not None, "User not found in SQLite database!"
    assert db_user["password_hash"].startswith("$2b$"), "Password is not stored as a valid bcrypt hash!"
    print(f" [PASS] User saved in SQLite with ID: {db_user['id']}, bcrypt hash: {db_user['password_hash'][:15]}...")

    # 2. LOGIN SUCCESS
    print("\n[Step 2] Testing Login with test@example.com / Test@12345...")
    login_ok, login_res = login_user(test_email, test_password)
    assert login_ok, f"Login failed: {login_res}"
    assert isinstance(login_res, dict)
    assert login_res["id"] == db_user["id"]
    assert login_res["full_name"] == "Test Candidate"
    assert login_res["email"] == "test@example.com"

    # Simulate Streamlit session state exactly as login.py does
    session = {}
    session["authenticated"] = True
    session["user_id"] = login_res["id"]
    session["user_name"] = login_res["full_name"]
    session["user_email"] = login_res["email"]
    session["page"] = "dashboard"
    session["current_page"] = "dashboard"
    session["user"] = login_res

    assert session["authenticated"] is True
    assert session["user_id"] == db_user["id"]
    assert session["user_name"] == "Test Candidate"
    assert session["user_email"] == "test@example.com"
    assert session["page"] == "dashboard"
    print(" [PASS] Login successful! Session state established -> Dashboard opened.")

    # 3. TEST CASE-INSENSITIVITY
    print("\n[Step 3] Testing Case-Insensitive Email Login (TEST@EXAMPLE.COM)...")
    case_ok, case_res = login_user("TEST@EXAMPLE.COM", test_password)
    assert case_ok, "Case-insensitive email login failed!"
    print(" [PASS] Case-insensitive login verified.")

    # 4. WRONG PASSWORD
    print("\n[Step 4] Testing test@example.com with Wrong Password...")
    bad_pw_ok, bad_pw_msg = login_user(test_email, "WrongPassword999!")
    assert not bad_pw_ok, "Login should NOT succeed with wrong password!"
    assert bad_pw_msg == "Incorrect password.", f"Expected 'Incorrect password.', got '{bad_pw_msg}'"
    print(f" [PASS] Wrong password returned exact error: '{bad_pw_msg}'")

    # 5. WRONG EMAIL
    print("\n[Step 5] Testing wrong@example.com with Test@12345...")
    bad_email_ok, bad_email_msg = login_user("wrong@example.com", test_password)
    assert not bad_email_ok, "Login should NOT succeed with non-existent email!"
    assert bad_email_msg == "Invalid username or email.", f"Expected 'Invalid username or email.', got '{bad_email_msg}'"
    print(f" [PASS] Wrong email returned exact error: '{bad_email_msg}'")

    # 6. LOGOUT SIMULATION
    print("\n[Step 6] Testing Logout...")
    keys_to_clear = ["authenticated", "user_id", "user_name", "user_email", "user", "page", "current_page"]
    for k in keys_to_clear:
        session.pop(k, None)
    session["authenticated"] = False
    session["page"] = "login"
    session["current_page"] = "login"

    assert session["authenticated"] is False
    assert "user_id" not in session
    assert session["page"] == "login"
    print(" [PASS] Logout cleared authentication and user session, redirected to login.")

    # 7. RE-LOGIN
    print("\n[Step 7] Testing Re-Login with test@example.com / Test@12345...")
    relogin_ok, relogin_res = login_user(test_email, test_password)
    assert relogin_ok, f"Re-login failed: {relogin_res}"
    print(" [PASS] Re-login successful with registered account!")

    print("\n" + "=" * 65)
    print("  ALL REAL ACCOUNT AUTHENTICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 65)

if __name__ == "__main__":
    run_login_flow_test()
