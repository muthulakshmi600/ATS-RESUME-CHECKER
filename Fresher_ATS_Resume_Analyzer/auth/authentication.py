"""
Authentication and Session Security Module for Fresher ATS Resume Analyzer.
Provides bcrypt password hashing, validation, login verification, and session state guards.
"""

import re
import bcrypt
import streamlit as st
from database.database import (
    create_user,
    get_user_by_email,
    get_user_by_id
)

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt with salt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, stored_password_hash) -> bool:
    """
    Verify a plaintext password against a stored bcrypt hash.
    Safely converts stored hash to bytes if it was retrieved as string.
    """
    try:
        if isinstance(stored_password_hash, str):
            stored_hash_bytes = stored_password_hash.encode("utf-8")
        else:
            stored_hash_bytes = stored_password_hash

        return bcrypt.checkpw(password.encode("utf-8"), stored_hash_bytes)
    except Exception:
        return False


def validate_registration(full_name: str, email: str, password: str, confirm_password: str, db_path=None):
    """
    Validate registration input criteria:
    - Full Name: not empty
    - Email / Username: not empty, valid format
    - Password: minimum 8 characters
    - Confirm Password: exact match
    - Uniqueness: check if email/username already exists
    Returns (is_valid: bool, error_message: str)
    """
    if not full_name or not full_name.strip():
        return False, "Full Name cannot be empty."

    if not email or not email.strip():
        return False, "Email / Username cannot be empty."

    cleaned_email = email.strip().lower()

    # Must be either a valid email address or an alphanumeric username (3-30 chars)
    is_valid_email = bool(EMAIL_REGEX.match(cleaned_email))
    is_valid_username = bool(re.match(r"^[a-zA-Z0-9_]{3,30}$", cleaned_email))
    if not (is_valid_email or is_valid_username):
        return False, "Please enter a valid email address (e.g., student@example.com) or username."

    if len(password) < 8:
        return False, "Password must be at least 8 characters long."

    if password != confirm_password:
        return False, "Password and Confirm Password do not match."

    existing_user = get_user_by_email(cleaned_email, db_path=db_path)
    if existing_user:
        return False, "An account with this email/username already exists. Please login."

    return True, ""


def register_user(full_name: str, email: str, password: str, confirm_password: str, db_path=None):
    """
    Execute user registration with validation and bcrypt password hashing.
    Returns (success: bool, message: str)
    """
    is_valid, err = validate_registration(full_name, email, password, confirm_password, db_path=db_path)
    if not is_valid:
        return False, err

    try:
        pw_hash = hash_password(password)
        create_user(full_name=full_name.strip(), email=email.strip().lower(), password_hash=pw_hash, db_path=db_path)
        return True, "Account created successfully. Please login."
    except Exception as e:
        return False, f"Registration failed due to a database error: {str(e)}"


def login_user(email_or_username: str, password: str, db_path=None):
    """
    Validate credentials against the database using bcrypt verification.
    Exact logic:
      entered_email = email_input.strip().lower()
      entered_password = password_input
      Find user from SQLite using entered_email.
      bcrypt.checkpw(entered_password.encode("utf-8"), stored_password_hash)
    Returns (success: bool, user_dict_or_error: dict|str)
    """
    if not email_or_username or not email_or_username.strip():
        return False, "Invalid username or email."

    if not password:
        return False, "Incorrect password."

    entered_email = email_or_username.strip().lower()
    entered_password = password

    user = get_user_by_email(entered_email, db_path=db_path)
    if not user:
        return False, "Invalid username or email."

    stored_password_hash = user["password_hash"]
    if isinstance(stored_password_hash, str):
        stored_hash_bytes = stored_password_hash.encode("utf-8")
    else:
        stored_hash_bytes = stored_password_hash

    try:
        is_correct = bcrypt.checkpw(entered_password.encode("utf-8"), stored_hash_bytes)
    except Exception:
        is_correct = False

    if not is_correct:
        return False, "Incorrect password."

    return True, user


def is_authenticated() -> bool:
    """Check if the user currently has an active, authenticated Streamlit session."""
    return bool(st.session_state.get("authenticated", False) and st.session_state.get("user_id"))


def get_current_user():
    """Retrieve the logged-in user dictionary from session state."""
    user = st.session_state.get("user")
    if not user and st.session_state.get("user_id"):
        user = get_user_by_id(st.session_state["user_id"])
        if user:
            st.session_state["user"] = user
    return user


def logout():
    """
    Clear all authentication session variables, user info, temporary resume,
    and analysis data. Sets page = 'login' and triggers st.rerun().
    """
    keys_to_clear = [
        "authenticated",
        "user_id",
        "user_name",
        "user_email",
        "user",
        "current_page",
        "page",
        "resume_text",
        "resume_metadata",
        "analysis_results",
        "uploaded_filename",
        "uploaded_filetype",
        "uploaded_filesize",
        "registration_success_msg"
    ]
    for k in keys_to_clear:
        st.session_state.pop(k, None)

    st.session_state["authenticated"] = False
    st.session_state["page"] = "login"
    st.session_state["current_page"] = "login"
    st.rerun()
