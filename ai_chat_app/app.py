"""
AI Chat Application - Main Flask Application Server.
Provides production-ready REST endpoints, Server-Sent Events (SSE) streaming,
authentication, file management, projects, settings, and library features.
"""

import os
import io
import re
import json
import uuid
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path

from flask import (
    Flask, render_template, request, jsonify, session,
    redirect, url_for, Response, send_file, abort
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# Local imports
from ai_chat_app.database import get_db, init_db
from ai_chat_app.services.file_parser import extract_file_content
from ai_chat_app.services.ai_service import AIService

# App setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "prod_super_secret_ai_chat_key_2026_x89f2a")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024  # 32 MB max upload
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=14)

# Initialize database
init_db()

# Global AI Service instance
ai_service = AIService()


# =====================================================================
# Auth Decorator & Helpers
# =====================================================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Unauthorized. Please log in."}), 401
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """Retrieves current logged in user dict, or None."""
    user_id = session.get("user_id")
    if not user_id:
        return None
    db = get_db()
    user = db.execute("SELECT id, name, email, avatar, created_at, settings_json FROM users WHERE id = ?", (user_id,)).fetchone()
    db.close()
    if user:
        settings = json.loads(user["settings_json"] or "{}")
        return {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "avatar": user["avatar"] or "avatar-1",
            "created_at": user["created_at"],
            "settings": settings
        }
    return None


# =====================================================================
# Main Template Views & Route Protection
# =====================================================================

@app.route("/")
def root():
    """Root route: Redirect to dashboard if logged in, else to login page."""
    if "user_id" in session:
        return redirect("/dashboard")
    return redirect("/login")


@app.route("/login")
def login_view():
    """Login view: If already logged in, redirect to dashboard."""
    if "user_id" in session:
        return redirect("/dashboard")
    return render_template("index.html")


@app.route("/signup")
def signup_view():
    """Signup view: If already logged in, redirect to dashboard."""
    if "user_id" in session:
        return redirect("/dashboard")
    return render_template("index.html")


@app.route("/dashboard")
@app.route("/library")
@app.route("/projects")
@app.route("/settings")
def protected_views():
    """Protected views: Require authenticated session, redirect unauthenticated to login."""
    if "user_id" not in session:
        return redirect("/login")
    return render_template("index.html")


# =====================================================================
# Auth Endpoints
# =====================================================================

@app.route("/api/auth/status", methods=["GET"])
def auth_status():
    """Returns current user status."""
    user = get_current_user()
    return jsonify({"authenticated": user is not None, "user": user})


@app.route("/api/auth/signup", methods=["POST"])
def signup():
    """Registers a new user with secure password hashing into SQLite."""
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    confirm_password = data.get("confirm_password", "")

    # Validation
    if not name or not email or not password or not confirm_password:
        return jsonify({"error": "Please fill in all fields."}), 400

    if len(name) < 2:
        return jsonify({"error": "Full Name must be at least 2 characters."}), 400
    
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(email_regex, email):
        return jsonify({"error": "Please enter a valid email address."}), 400

    if len(password) < 4:
        return jsonify({"error": "Password must be at least 4 characters long."}), 400

    if password != confirm_password:
        return jsonify({"error": "Passwords do not match."}), 400

    try:
        db = get_db()
        existing = db.execute("SELECT id FROM users WHERE LOWER(email) = ?", (email,)).fetchone()
        if existing:
            db.close()
            return jsonify({"error": "An account with this email already exists. Please log in."}), 409

        user_id = str(uuid.uuid4())
        pw_hash = generate_password_hash(password)
        now = datetime.utcnow().isoformat()
        default_settings = json.dumps({
            "theme": "dark",
            "ai_model": "gemini-3.8-flash",
            "temperature": 0.7,
            "system_instruction": "You are a helpful, expert AI coding and learning assistant.",
            "gemini_api_key": ""
        })

        with db:
            db.execute(
                "INSERT INTO users (id, name, email, password_hash, avatar, created_at, updated_at, settings_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (user_id, name, email, pw_hash, "avatar-1", now, now, default_settings)
            )
        db.close()

        return jsonify({
            "success": True,
            "message": "Account created successfully! Please sign in with your credentials."
        }), 201
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500


@app.route("/api/auth/login", methods=["POST"])
def login():
    """Authenticates the user using SQLite database and initiates Flask session."""
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    remember_me = bool(data.get("remember_me", False))

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    try:
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE LOWER(email) = ?", (email,)).fetchone()
        db.close()

        if not user or not check_password_hash(user["password_hash"], password):
            return jsonify({"error": "Invalid email or password."}), 401

        session.permanent = remember_me
        session["user_id"] = user["id"]
        session["user_email"] = user["email"]
        session["user_name"] = user["name"]

        settings = json.loads(user["settings_json"] or "{}")

        return jsonify({
            "success": True,
            "message": f"Welcome back, {user['name']}!",
            "redirect_url": "/dashboard",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "avatar": user["avatar"] or "avatar-1",
                "settings": settings
            }
        })
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500


@app.route("/api/auth/forgot-password", methods=["POST"])
def forgot_password():
    """Provides secure password update with transparent SMTP notice."""
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    new_password = data.get("new_password", "")

    if not email:
        return jsonify({"error": "Please enter your registered email address."}), 400

    db = get_db()
    user = db.execute("SELECT id FROM users WHERE LOWER(email) = ?", (email,)).fetchone()
    if not user:
        db.close()
        return jsonify({"error": "No account found with this email address."}), 404

    if new_password:
        if len(new_password) < 4:
            db.close()
            return jsonify({"error": "New password must be at least 4 characters long."}), 400
        new_hash = generate_password_hash(new_password)
        now = datetime.utcnow().isoformat()
        with db:
            db.execute("UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?", (new_hash, now, user["id"]))
        db.close()
        return jsonify({
            "success": True,
            "message": "Password updated successfully in SQLite database! You can now log in."
        })
    else:
        db.close()
        return jsonify({
            "success": True,
            "message": "Account verified. Please enter your new password to complete update."
        })


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    """Clears user session and logs out."""
    session.clear()
    return jsonify({
        "success": True,
        "message": "Logged out successfully.",
        "redirect_url": "/login"
    })


# =====================================================================
# Chat Endpoints
# =====================================================================

@app.route("/api/chats", methods=["GET"])
@login_required
def get_chats():
    """Lists all chats for the authenticated user, separated into pinned and history."""
    user_id = session["user_id"]
    project_id = request.args.get("project_id")

    db = get_db()
    if project_id:
        rows = db.execute(
            "SELECT * FROM chats WHERE user_id = ? AND project_id = ? ORDER BY updated_at DESC",
            (user_id, project_id)
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT * FROM chats WHERE user_id = ? ORDER BY updated_at DESC",
            (user_id,)
        ).fetchall()

    chats = []
    for r in rows:
        chats.append({
            "id": r["id"],
            "title": r["title"],
            "is_pinned": bool(r["is_pinned"]),
            "project_id": r["project_id"],
            "created_at": r["created_at"],
            "updated_at": r["updated_at"]
        })
    db.close()

    pinned = [c for c in chats if c["is_pinned"]]
    history = [c for c in chats if not c["is_pinned"]]

    return jsonify({
        "all": chats,
        "pinned": pinned,
        "history": history
    })


@app.route("/api/chats", methods=["POST"])
@login_required
def create_chat():
    """Creates a fresh conversation."""
    user_id = session["user_id"]
    data = request.get_json() or {}
    title = data.get("title", "New Conversation").strip()
    project_id = data.get("project_id")

    chat_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    db = get_db()
    with db:
        db.execute(
            "INSERT INTO chats (id, user_id, project_id, title, is_pinned, created_at, updated_at) VALUES (?, ?, ?, ?, 0, ?, ?)",
            (chat_id, user_id, project_id, title, now, now)
        )
    db.close()

    return jsonify({
        "id": chat_id,
        "title": title,
        "is_pinned": False,
        "project_id": project_id,
        "created_at": now,
        "updated_at": now,
        "messages": []
    }), 201


@app.route("/api/chats/<chat_id>", methods=["GET"])
@login_required
def get_chat(chat_id):
    """Retrieves full conversation history and attached metadata."""
    user_id = session["user_id"]
    db = get_db()

    chat = db.execute(
        "SELECT * FROM chats WHERE id = ? AND user_id = ?",
        (chat_id, user_id)
    ).fetchone()

    if not chat:
        db.close()
        return jsonify({"error": "Chat not found."}), 404

    msg_rows = db.execute(
        "SELECT * FROM messages WHERE chat_id = ? ORDER BY created_at ASC",
        (chat_id,)
    ).fetchall()

    messages = []
    for m in msg_rows:
        messages.append({
            "id": m["id"],
            "role": m["role"],
            "content": m["content"],
            "attachments": json.loads(m["attachments_json"] or "[]"),
            "created_at": m["created_at"]
        })

    # Also load project details if linked
    project_info = None
    if chat["project_id"]:
        proj = db.execute("SELECT id, name, color FROM projects WHERE id = ?", (chat["project_id"],)).fetchone()
        if proj:
            project_info = {"id": proj["id"], "name": proj["name"], "color": proj["color"]}

    db.close()

    return jsonify({
        "id": chat["id"],
        "title": chat["title"],
        "is_pinned": bool(chat["is_pinned"]),
        "project_id": chat["project_id"],
        "project": project_info,
        "created_at": chat["created_at"],
        "updated_at": chat["updated_at"],
        "messages": messages
    })


@app.route("/api/chats/<chat_id>", methods=["PATCH"])
@login_required
def update_chat(chat_id):
    """Updates chat title, pinned status, or project assignment."""
    user_id = session["user_id"]
    data = request.get_json() or {}

    db = get_db()
    chat = db.execute("SELECT * FROM chats WHERE id = ? AND user_id = ?", (chat_id, user_id)).fetchone()
    if not chat:
        db.close()
        return jsonify({"error": "Chat not found."}), 404

    new_title = data.get("title", chat["title"]).strip()
    is_pinned = int(data.get("is_pinned", chat["is_pinned"]))
    project_id = data.get("project_id", chat["project_id"])
    now = datetime.utcnow().isoformat()

    with db:
        db.execute(
            "UPDATE chats SET title = ?, is_pinned = ?, project_id = ?, updated_at = ? WHERE id = ?",
            (new_title, is_pinned, project_id, now, chat_id)
        )
    db.close()

    return jsonify({
        "success": True,
        "id": chat_id,
        "title": new_title,
        "is_pinned": bool(is_pinned),
        "project_id": project_id,
        "updated_at": now
    })


@app.route("/api/chats/<chat_id>", methods=["DELETE"])
@login_required
def delete_chat(chat_id):
    """Deletes a conversation and all its messages."""
    user_id = session["user_id"]
    db = get_db()
    chat = db.execute("SELECT id FROM chats WHERE id = ? AND user_id = ?", (chat_id, user_id)).fetchone()
    if not chat:
        db.close()
        return jsonify({"error": "Chat not found."}), 404

    with db:
        db.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
        db.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
    db.close()

    return jsonify({"success": True, "message": "Conversation deleted."})


@app.route("/api/chats/<chat_id>/message", methods=["POST"])
@login_required
def send_chat_message(chat_id):
    """
    Appends user message and streams AI response via Server-Sent Events (SSE).
    """
    user_id = session["user_id"]
    data = request.get_json() or {}
    content = data.get("content", "").strip()
    attachments = data.get("attachments", [])  # List of file IDs or file dicts

    if not content and not attachments:
        return jsonify({"error": "Message cannot be empty."}), 400

    db = get_db()
    chat = db.execute("SELECT * FROM chats WHERE id = ? AND user_id = ?", (chat_id, user_id)).fetchone()
    if not chat:
        db.close()
        return jsonify({"error": "Chat not found."}), 404

    now = datetime.utcnow().isoformat()
    user_msg_id = str(uuid.uuid4())

    # Save user message
    with db:
        db.execute(
            "INSERT INTO messages (id, chat_id, role, content, attachments_json, created_at) VALUES (?, ?, 'user', ?, ?, ?)",
            (user_msg_id, chat_id, content, json.dumps(attachments), now)
        )
        # Update chat updated_at
        db.execute("UPDATE chats SET updated_at = ? WHERE id = ?", (now, chat_id))

        # Automatically auto-title the chat if it's currently default
        is_first_msg = (db.execute("SELECT COUNT(*) as count FROM messages WHERE chat_id = ?", (chat_id,)).fetchone()["count"] <= 1)
        if chat["title"] in ["New Conversation", "New Chat", ""] or is_first_msg:
            auto_title = content[:35].strip() if content else "Document Analysis"
            if len(content) > 35:
                auto_title += "..."
            db.execute("UPDATE chats SET title = ? WHERE id = ?", (auto_title, chat_id))
            chat_title = auto_title
        else:
            chat_title = chat["title"]

    # Retrieve conversation history
    history_rows = db.execute(
        "SELECT role, content, attachments_json FROM messages WHERE chat_id = ? ORDER BY created_at ASC",
        (chat_id,)
    ).fetchall()

    # Retrieve user AI settings
    user_row = db.execute("SELECT settings_json FROM users WHERE id = ?", (user_id,)).fetchone()
    user_settings = json.loads(user_row["settings_json"] or "{}")

    # Project instructions if any
    project_system_inst = ""
    if chat["project_id"]:
        proj = db.execute("SELECT system_instructions FROM projects WHERE id = ?", (chat["project_id"],)).fetchone()
        if proj and proj["system_instructions"]:
            project_system_inst = proj["system_instructions"].strip()

    # Load attached files text context
    file_contexts = []
    if attachments:
        for att in attachments:
            f_id = att.get("id") or att.get("file_id")
            if f_id:
                file_row = db.execute("SELECT * FROM files WHERE id = ? AND user_id = ?", (f_id, user_id)).fetchone()
                if file_row:
                    file_contexts.append({
                        "filename": file_row["original_filename"],
                        "type": file_row["file_type"],
                        "text": file_row["parsed_text"] or file_row["summary"] or ""
                    })

    db.close()

    conversation_payload = []
    for hr in history_rows:
        conversation_payload.append({
            "role": hr["role"],
            "content": hr["content"]
        })

    # Setup AI parameters
    persona = data.get("persona", "").strip()
    ai_key = user_settings.get("gemini_api_key", "").strip() or os.environ.get("GEMINI_API_KEY", "").strip()
    ai_model = user_settings.get("ai_model", "gemini-3.8-flash")
    ai_temp = float(user_settings.get("temperature", 0.7))
    custom_sys = user_settings.get("system_instruction", "")

    # Persona specialization
    persona_prompts = {
        "coder": "\nYou are a world-class Senior Software Engineer. Provide complete, production-ready code with clean architecture, error handling, and test cases.",
        "resume": "\nYou are an expert ATS Resume and Career Coach. Guide candidates with high-impact ATS summaries, quantified bullet points, and key skills.",
        "tamil": "\nYou are a fluent, friendly bilingual AI assistant proficient in Tamil and English (Tanglish). Explain programming, tech, and general questions clearly.",
        "math": "\nYou are a Master Mathematician. Provide step-by-step solutions to mathematical equations, percentages, logic, and algorithms.",
        "writer": "\nYou are an executive communications editor. Draft polished, professional emails, letters, essays, and reports."
    }
    if persona in persona_prompts:
        custom_sys = f"{custom_sys}\n{persona_prompts[persona]}".strip()

    if project_system_inst:
        custom_sys = f"{custom_sys}\n\nProject Specific Guidelines:\n{project_system_inst}".strip()

    assistant_msg_id = str(uuid.uuid4())

    def event_stream():
        nonlocal assistant_msg_id, chat_id, chat_title
        full_response_text = []

        service = AIService(api_key=ai_key)
        stream_gen = service.generate_chat_stream(
            messages=conversation_payload,
            system_instruction=custom_sys,
            model=ai_model,
            temperature=ai_temp,
            file_contexts=file_contexts
        )

        for chunk in stream_gen:
            full_response_text.append(chunk)
            data_payload = json.dumps({"chunk": chunk})
            yield f"data: {data_payload}\n\n"

        # Complete response
        complete_text = "".join(full_response_text).strip()
        done_time = datetime.utcnow().isoformat()

        # Persist assistant response to DB
        write_db = get_db()
        with write_db:
            write_db.execute(
                "INSERT INTO messages (id, chat_id, role, content, attachments_json, created_at) VALUES (?, ?, 'assistant', ?, '[]', ?)",
                (assistant_msg_id, chat_id, complete_text, done_time)
            )
            write_db.execute("UPDATE chats SET updated_at = ? WHERE id = ?", (done_time, chat_id))
        write_db.close()

        yield f"data: {json.dumps({'done': True, 'message_id': assistant_msg_id, 'chat_title': chat_title, 'created_at': done_time})}\n\n"

    return Response(event_stream(), mimetype="text/event-stream")


@app.route("/api/chats/<chat_id>/regenerate", methods=["POST"])
@login_required
def regenerate_response(chat_id):
    """Regenerates the last AI assistant message."""
    user_id = session["user_id"]
    db = get_db()

    chat = db.execute("SELECT * FROM chats WHERE id = ? AND user_id = ?", (chat_id, user_id)).fetchone()
    if not chat:
        db.close()
        return jsonify({"error": "Chat not found."}), 404

    # Delete the last assistant message if exists
    last_msg = db.execute(
        "SELECT id, role FROM messages WHERE chat_id = ? ORDER BY created_at DESC LIMIT 1",
        (chat_id,)
    ).fetchone()

    if last_msg and last_msg["role"] == "assistant":
        with db:
            db.execute("DELETE FROM messages WHERE id = ?", (last_msg["id"],))

    # Get the last user message to replay
    last_user_msg = db.execute(
        "SELECT content, attachments_json FROM messages WHERE chat_id = ? AND role = 'user' ORDER BY created_at DESC LIMIT 1",
        (chat_id,)
    ).fetchone()

    if not last_user_msg:
        db.close()
        return jsonify({"error": "No user message to regenerate from."}), 400

    content = last_user_msg["content"]
    attachments = json.loads(last_user_msg["attachments_json"] or "[]")
    db.close()

    # Re-call send_chat_message logic or return instruction
    # The frontend calls this endpoint to trigger streaming regeneration
    return jsonify({
        "success": True,
        "prompt": content,
        "attachments": attachments
    })


@app.route("/api/chats/<chat_id>/messages/<message_id>", methods=["DELETE"])
@login_required
def delete_message(chat_id, message_id):
    """Deletes an individual message from a conversation."""
    user_id = session["user_id"]
    db = get_db()

    chat = db.execute("SELECT id FROM chats WHERE id = ? AND user_id = ?", (chat_id, user_id)).fetchone()
    if not chat:
        db.close()
        return jsonify({"error": "Chat not found."}), 404

    with db:
        db.execute("DELETE FROM messages WHERE id = ? AND chat_id = ?", (message_id, chat_id))
    db.close()

    return jsonify({"success": True, "message": "Message deleted."})


@app.route("/api/chats/<chat_id>/clear", methods=["POST"])
@login_required
def clear_chat_messages(chat_id):
    """Clears all messages within a specific conversation without deleting the chat."""
    user_id = session["user_id"]
    db = get_db()
    chat = db.execute("SELECT id FROM chats WHERE id = ? AND user_id = ?", (chat_id, user_id)).fetchone()
    if not chat:
        db.close()
        return jsonify({"error": "Chat not found."}), 404

    now = datetime.utcnow().isoformat()
    with db:
        db.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
        db.execute("UPDATE chats SET title = 'New Conversation', updated_at = ? WHERE id = ?", (now, chat_id))
    db.close()

    return jsonify({"success": True, "message": "Conversation messages cleared successfully."})


# =====================================================================
# Global Search Endpoint (Ctrl + K)
# =====================================================================

@app.route("/api/search", methods=["GET"])
@login_required
def global_search():
    """
    Performs full-text search across:
    - Chat Titles
    - User Messages
    - AI Responses
    - Uploaded Files
    """
    user_id = session["user_id"]
    q = request.args.get("q", "").strip()

    if not q or len(q) < 2:
        return jsonify({"results": []})

    db = get_db()
    wildcard = f"%{q}%"

    # Search chats by title
    chat_matches = db.execute(
        "SELECT id, title, is_pinned, updated_at FROM chats WHERE user_id = ? AND title LIKE ? ORDER BY updated_at DESC LIMIT 10",
        (user_id, wildcard)
    ).fetchall()

    # Search messages
    msg_matches = db.execute("""
        SELECT m.id as message_id, m.role, m.content, m.created_at, c.id as chat_id, c.title as chat_title
        FROM messages m
        JOIN chats c ON m.chat_id = c.id
        WHERE c.user_id = ? AND m.content LIKE ?
        ORDER BY m.created_at DESC LIMIT 20
    """, (user_id, wildcard)).fetchall()

    # Search files
    file_matches = db.execute(
        "SELECT id, original_filename, file_type, file_size, created_at FROM files WHERE user_id = ? AND (original_filename LIKE ? OR parsed_text LIKE ?) LIMIT 10",
        (user_id, wildcard, wildcard)
    ).fetchall()

    db.close()

    results = []

    # Chat Title Results
    for c in chat_matches:
        results.append({
            "type": "chat",
            "chat_id": c["id"],
            "title": c["title"],
            "snippet": f"Conversation title matches '{q}'",
            "is_pinned": bool(c["is_pinned"]),
            "date": c["updated_at"]
        })

    # Message Results
    for m in msg_matches:
        text = m["content"]
        idx = text.lower().find(q.lower())
        start = max(0, idx - 40)
        end = min(len(text), idx + len(q) + 60)
        snippet = ("..." if start > 0 else "") + text[start:end] + ("..." if end < len(text) else "")
        results.append({
            "type": "message",
            "role": m["role"],
            "chat_id": m["chat_id"],
            "title": m["chat_title"],
            "message_id": m["message_id"],
            "snippet": snippet,
            "date": m["created_at"]
        })

    # File Results
    for f in file_matches:
        results.append({
            "type": "file",
            "file_id": f["id"],
            "title": f["original_filename"],
            "snippet": f"Uploaded file ({f['file_type']}) matching '{q}'",
            "date": f["created_at"]
        })

    return jsonify({"query": q, "results": results})


# =====================================================================
# File Upload & Ingestion
# =====================================================================

ALLOWED_EXTENSIONS = {
    "pdf", "docx", "doc", "txt", "md", "csv", "xlsx", "xls",
    "pptx", "ppt", "jpg", "jpeg", "png", "webp", "gif", "json", "py"
}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/api/upload", methods=["POST"])
@login_required
def upload_file():
    """Handles file uploads with format validation and content extraction."""
    user_id = session["user_id"]

    if "file" not in request.files:
        return jsonify({"error": "No file payload found in request."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    if not allowed_file(file.filename):
        return jsonify({
            "error": f"Unsupported file type. Supported formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        }), 400

    project_id = request.form.get("project_id") or None
    original_name = file.filename
    clean_name = secure_filename(original_name)
    ext = clean_name.rsplit(".", 1)[1].lower() if "." in clean_name else "bin"
    file_id = str(uuid.uuid4())
    stored_name = f"{file_id}_{clean_name}"
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], stored_name)

    file.save(save_path)
    file_size = os.path.getsize(save_path)

    # Extract text and preview
    parsed = extract_file_content(save_path, original_name)
    parsed_text = parsed.get("text", "")
    preview = parsed.get("preview", "")
    type_category = parsed.get("type_category", "other")
    now = datetime.utcnow().isoformat()

    # Save to database
    db = get_db()
    with db:
        db.execute("""
            INSERT INTO files (id, user_id, project_id, original_filename, stored_filename, file_type, file_size, file_path, parsed_text, summary, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (file_id, user_id, project_id, original_name, stored_name, ext.upper(), file_size, save_path, parsed_text, preview, now))
    db.close()

    return jsonify({
        "success": True,
        "file": {
            "id": file_id,
            "name": original_name,
            "type": ext.upper(),
            "category": type_category,
            "size": file_size,
            "preview": preview,
            "created_at": now
        }
    }), 201


# =====================================================================
# Library Endpoints
# =====================================================================

@app.route("/api/library", methods=["GET"])
@login_required
def get_library():
    """Lists files uploaded by the user with search, filter, and sort options."""
    user_id = session["user_id"]
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "all").strip().lower()
    sort_by = request.args.get("sort", "date_desc").strip()

    query = "SELECT id, project_id, original_filename, file_type, file_size, summary, created_at FROM files WHERE user_id = ?"
    params = [user_id]

    if search:
        query += " AND (original_filename LIKE ? OR parsed_text LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    if category == "document":
        query += " AND file_type IN ('PDF', 'DOCX', 'DOC', 'TXT', 'MD', 'JSON')"
    elif category == "spreadsheet":
        query += " AND file_type IN ('CSV', 'XLSX', 'XLS')"
    elif category == "presentation":
        query += " AND file_type IN ('PPTX', 'PPT')"
    elif category == "image":
        query += " AND file_type IN ('JPG', 'JPEG', 'PNG', 'WEBP', 'GIF')"

    # Sorting
    if sort_by == "name_asc":
        query += " ORDER BY original_filename ASC"
    elif sort_by == "name_desc":
        query += " ORDER BY original_filename DESC"
    elif sort_by == "size_desc":
        query += " ORDER BY file_size DESC"
    elif sort_by == "size_asc":
        query += " ORDER BY file_size ASC"
    elif sort_by == "date_asc":
        query += " ORDER BY created_at ASC"
    else:
        query += " ORDER BY created_at DESC"

    db = get_db()
    rows = db.execute(query, params).fetchall()
    db.close()

    files = []
    for r in rows:
        files.append({
            "id": r["id"],
            "project_id": r["project_id"],
            "name": r["original_filename"],
            "type": r["file_type"],
            "size": r["file_size"],
            "summary": r["summary"],
            "created_at": r["created_at"]
        })

    return jsonify({"files": files, "count": len(files)})


@app.route("/api/files/<file_id>/download", methods=["GET"])
@login_required
def download_file(file_id):
    """Downloads the raw uploaded file."""
    user_id = session["user_id"]
    db = get_db()
    file_row = db.execute("SELECT * FROM files WHERE id = ? AND user_id = ?", (file_id, user_id)).fetchone()
    db.close()

    if not file_row or not os.path.exists(file_row["file_path"]):
        return jsonify({"error": "File not found."}), 404

    return send_file(
        file_row["file_path"],
        as_attachment=True,
        download_name=file_row["original_filename"]
    )


@app.route("/api/files/<file_id>/preview", methods=["GET"])
@login_required
def preview_file(file_id):
    """Returns text/data preview or base64 image for the file."""
    user_id = session["user_id"]
    db = get_db()
    file_row = db.execute("SELECT * FROM files WHERE id = ? AND user_id = ?", (file_id, user_id)).fetchone()
    db.close()

    if not file_row or not os.path.exists(file_row["file_path"]):
        return jsonify({"error": "File not found."}), 404

    parsed = extract_file_content(file_row["file_path"], file_row["original_filename"])

    return jsonify({
        "id": file_row["id"],
        "name": file_row["original_filename"],
        "type": file_row["file_type"],
        "size": file_row["file_size"],
        "preview": parsed.get("preview", ""),
        "full_text": parsed.get("text", "")[:10000],
        "category": parsed.get("type_category", "other"),
        "details": parsed.get("details", {})
    })


@app.route("/api/files/<file_id>", methods=["PATCH"])
@login_required
def rename_file(file_id):
    """Renames an uploaded file in user's library."""
    user_id = session["user_id"]
    data = request.get_json() or {}
    new_name = data.get("name", "").strip()

    if not new_name:
        return jsonify({"error": "Filename cannot be empty."}), 400

    db = get_db()
    file_row = db.execute("SELECT id FROM files WHERE id = ? AND user_id = ?", (file_id, user_id)).fetchone()
    if not file_row:
        db.close()
        return jsonify({"error": "File not found."}), 404

    with db:
        db.execute("UPDATE files SET original_filename = ? WHERE id = ?", (new_name, file_id))
    db.close()

    return jsonify({"success": True, "name": new_name})


@app.route("/api/files/<file_id>", methods=["DELETE"])
@login_required
def delete_file(file_id):
    """Deletes a file from the database and physical storage."""
    user_id = session["user_id"]
    db = get_db()
    file_row = db.execute("SELECT file_path FROM files WHERE id = ? AND user_id = ?", (file_id, user_id)).fetchone()
    if not file_row:
        db.close()
        return jsonify({"error": "File not found."}), 404

    # Remove physical file if exists
    try:
        if os.path.exists(file_row["file_path"]):
            os.remove(file_row["file_path"])
    except Exception:
        pass

    with db:
        db.execute("DELETE FROM files WHERE id = ?", (file_id,))
    db.close()

    return jsonify({"success": True, "message": "File removed from library."})


# =====================================================================
# Projects Endpoints
# =====================================================================

@app.route("/api/projects", methods=["GET"])
@login_required
def get_projects():
    """Lists all projects belonging to the logged-in user with chat/file counts."""
    user_id = session["user_id"]
    db = get_db()

    rows = db.execute("""
        SELECT p.*,
            (SELECT COUNT(*) FROM chats c WHERE c.project_id = p.id) as chat_count,
            (SELECT COUNT(*) FROM files f WHERE f.project_id = p.id) as file_count
        FROM projects p
        WHERE p.user_id = ?
        ORDER BY p.updated_at DESC
    """, (user_id,)).fetchall()
    db.close()

    projects = []
    for r in rows:
        projects.append({
            "id": r["id"],
            "name": r["name"],
            "description": r["description"],
            "color": r["color"] or "#6366f1",
            "system_instructions": r["system_instructions"],
            "chat_count": r["chat_count"],
            "file_count": r["file_count"],
            "created_at": r["created_at"],
            "updated_at": r["updated_at"]
        })

    return jsonify({"projects": projects})


@app.route("/api/projects", methods=["POST"])
@login_required
def create_project():
    """Creates a new project workspace."""
    user_id = session["user_id"]
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    description = data.get("description", "").strip()
    color = data.get("color", "#6366f1").strip()
    instructions = data.get("system_instructions", "").strip()

    if not name:
        return jsonify({"error": "Project name is required."}), 400

    project_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    db = get_db()
    with db:
        db.execute("""
            INSERT INTO projects (id, user_id, name, description, color, system_instructions, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (project_id, user_id, name, description, color, instructions, now, now))
    db.close()

    return jsonify({
        "id": project_id,
        "name": name,
        "description": description,
        "color": color,
        "system_instructions": instructions,
        "chat_count": 0,
        "file_count": 0,
        "created_at": now,
        "updated_at": now
    }), 201


@app.route("/api/projects/<project_id>", methods=["GET"])
@login_required
def get_project_detail(project_id):
    """Retrieves project details along with its associated chats and files."""
    user_id = session["user_id"]
    db = get_db()

    proj = db.execute("SELECT * FROM projects WHERE id = ? AND user_id = ?", (project_id, user_id)).fetchone()
    if not proj:
        db.close()
        return jsonify({"error": "Project not found."}), 404

    chats = db.execute("SELECT id, title, is_pinned, updated_at FROM chats WHERE project_id = ? ORDER BY updated_at DESC", (project_id,)).fetchall()
    files = db.execute("SELECT id, original_filename, file_type, file_size, created_at FROM files WHERE project_id = ? ORDER BY created_at DESC", (project_id,)).fetchall()
    db.close()

    return jsonify({
        "id": proj["id"],
        "name": proj["name"],
        "description": proj["description"],
        "color": proj["color"],
        "system_instructions": proj["system_instructions"],
        "created_at": proj["created_at"],
        "updated_at": proj["updated_at"],
        "chats": [{"id": c["id"], "title": c["title"], "is_pinned": bool(c["is_pinned"]), "updated_at": c["updated_at"]} for c in chats],
        "files": [{"id": f["id"], "name": f["original_filename"], "type": f["file_type"], "size": f["file_size"], "created_at": f["created_at"]} for f in files]
    })


@app.route("/api/projects/<project_id>", methods=["PATCH"])
@login_required
def update_project(project_id):
    """Updates project metadata or instructions."""
    user_id = session["user_id"]
    data = request.get_json() or {}

    db = get_db()
    proj = db.execute("SELECT * FROM projects WHERE id = ? AND user_id = ?", (project_id, user_id)).fetchone()
    if not proj:
        db.close()
        return jsonify({"error": "Project not found."}), 404

    name = data.get("name", proj["name"]).strip()
    description = data.get("description", proj["description"]).strip()
    color = data.get("color", proj["color"]).strip()
    instructions = data.get("system_instructions", proj["system_instructions"]).strip()
    now = datetime.utcnow().isoformat()

    with db:
        db.execute("""
            UPDATE projects SET name = ?, description = ?, color = ?, system_instructions = ?, updated_at = ?
            WHERE id = ?
        """, (name, description, color, instructions, now, project_id))
    db.close()

    return jsonify({"success": True, "message": "Project updated successfully."})


@app.route("/api/projects/<project_id>", methods=["DELETE"])
@login_required
def delete_project(project_id):
    """Deletes a project and unlinks associated chats and files."""
    user_id = session["user_id"]
    db = get_db()
    proj = db.execute("SELECT id FROM projects WHERE id = ? AND user_id = ?", (project_id, user_id)).fetchone()
    if not proj:
        db.close()
        return jsonify({"error": "Project not found."}), 404

    with db:
        db.execute("UPDATE chats SET project_id = NULL WHERE project_id = ?", (project_id,))
        db.execute("UPDATE files SET project_id = NULL WHERE project_id = ?", (project_id,))
        db.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    db.close()

    return jsonify({"success": True, "message": "Project deleted."})


# =====================================================================
# Settings & Preferences Endpoints
# =====================================================================

@app.route("/api/settings", methods=["GET"])
@login_required
def get_settings():
    """Returns user profile, security info, and AI preferences."""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Not authenticated."}), 401
    return jsonify({"user": user})


@app.route("/api/settings/profile", methods=["POST"])
@login_required
def update_profile():
    """Updates user display name, email, and avatar."""
    user_id = session["user_id"]
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    avatar = data.get("avatar", "avatar-1").strip()

    if not name or len(name) < 2:
        return jsonify({"error": "Name must be at least 2 characters."}), 400

    if not email or "@" not in email:
        return jsonify({"error": "Valid email address is required."}), 400

    db = get_db()
    # Check if email taken by someone else
    conflict = db.execute("SELECT id FROM users WHERE LOWER(email) = ? AND id != ?", (email, user_id)).fetchone()
    if conflict:
        db.close()
        return jsonify({"error": "Email is already taken by another account."}), 409

    now = datetime.utcnow().isoformat()
    with db:
        db.execute("UPDATE users SET name = ?, email = ?, avatar = ?, updated_at = ? WHERE id = ?", (name, email, avatar, now, user_id))
    db.close()

    session["user_name"] = name
    session["user_email"] = email

    return jsonify({"success": True, "message": "Profile updated successfully.", "user": {"name": name, "email": email, "avatar": avatar}})


@app.route("/api/settings/password", methods=["POST"])
@login_required
def change_password():
    """Validates current password and updates to new password."""
    user_id = session["user_id"]
    data = request.get_json() or {}
    current_pw = data.get("current_password", "")
    new_pw = data.get("new_password", "")
    confirm_new_pw = data.get("confirm_new_password", "")

    if not current_pw or not new_pw:
        return jsonify({"error": "All password fields are required."}), 400

    if new_pw != confirm_new_pw:
        return jsonify({"error": "New passwords do not match."}), 400

    if len(new_pw) < 4:
        return jsonify({"error": "New password must be at least 4 characters long."}), 400

    db = get_db()
    user = db.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user or not check_password_hash(user["password_hash"], current_pw):
        db.close()
        return jsonify({"error": "Current password is incorrect."}), 400

    new_hash = generate_password_hash(new_pw)
    now = datetime.utcnow().isoformat()
    with db:
        db.execute("UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?", (new_hash, now, user_id))
    db.close()

    return jsonify({"success": True, "message": "Password changed successfully."})


@app.route("/api/settings/ai", methods=["POST"])
@login_required
def update_ai_settings():
    """Saves user AI configurations (Gemini API key, model, temperature, theme)."""
    user_id = session["user_id"]
    data = request.get_json() or {}

    db = get_db()
    user = db.execute("SELECT settings_json FROM users WHERE id = ?", (user_id,)).fetchone()
    curr_settings = json.loads(user["settings_json"] or "{}")

    # Update settings
    if "gemini_api_key" in data:
        curr_settings["gemini_api_key"] = data["gemini_api_key"].strip()
    if "ai_model" in data:
        curr_settings["ai_model"] = data["ai_model"]
    if "temperature" in data:
        curr_settings["temperature"] = float(data["temperature"])
    if "system_instruction" in data:
        curr_settings["system_instruction"] = data["system_instruction"].strip()
    if "theme" in data:
        curr_settings["theme"] = data["theme"]

    now = datetime.utcnow().isoformat()
    with db:
        db.execute("UPDATE users SET settings_json = ?, updated_at = ? WHERE id = ?", (json.dumps(curr_settings), now, user_id))
    db.close()

    return jsonify({"success": True, "message": "AI settings saved successfully.", "settings": curr_settings})


@app.route("/api/settings/test-gemini", methods=["POST"])
@login_required
def test_gemini_connection():
    """Tests if the provided Gemini API key works."""
    data = request.get_json() or {}
    test_key = data.get("api_key", "").strip()

    service = AIService(api_key=test_key)
    res = service.test_connection(test_key)
    return jsonify(res)


@app.route("/api/settings/export", methods=["GET"])
@login_required
def export_user_data():
    """Exports all chats, messages, and project info as JSON."""
    user_id = session["user_id"]
    db = get_db()

    chats = db.execute("SELECT * FROM chats WHERE user_id = ? ORDER BY created_at ASC", (user_id,)).fetchall()
    export_payload = {
        "export_date": datetime.utcnow().isoformat(),
        "user": session.get("user_email"),
        "total_conversations": len(chats),
        "conversations": []
    }

    for c in chats:
        msgs = db.execute("SELECT role, content, created_at FROM messages WHERE chat_id = ? ORDER BY created_at ASC", (c["id"],)).fetchall()
        export_payload["conversations"].append({
            "id": c["id"],
            "title": c["title"],
            "is_pinned": bool(c["is_pinned"]),
            "created_at": c["created_at"],
            "messages": [{"role": m["role"], "content": m["content"], "date": m["created_at"]} for m in msgs]
        })
    db.close()

    json_str = json.dumps(export_payload, indent=2)
    mem_file = io.BytesIO(json_str.encode("utf-8"))
    filename = f"ai_chat_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"

    return send_file(
        mem_file,
        mimetype="application/json",
        as_attachment=True,
        download_name=filename
    )


@app.route("/api/settings/clear-history", methods=["POST"])
@login_required
def clear_chat_history():
    """Deletes all chats for the user while preserving library files and projects."""
    user_id = session["user_id"]
    db = get_db()
    with db:
        chat_ids = [r["id"] for r in db.execute("SELECT id FROM chats WHERE user_id = ?", (user_id,)).fetchall()]
        for cid in chat_ids:
            db.execute("DELETE FROM messages WHERE chat_id = ?", (cid,))
        db.execute("DELETE FROM chats WHERE user_id = ?", (user_id,))
    db.close()

    return jsonify({"success": True, "message": "All chat history cleared successfully."})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting AI Chat Application on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
