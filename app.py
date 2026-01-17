import os
import pytz
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, jsonify
from flask_socketio import SocketIO, send, emit
from dotenv import load_dotenv

from database import save_message, get_messages, check_user, update_user_password, init_db

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_secret_key")

# SocketIO setup
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'zip', '7z', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'}
MONTREAL_TZ = pytz.timezone("America/Toronto")

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_current_timestamp():
    return datetime.now(MONTREAL_TZ).strftime("%y-%m-%d %H:%M")

def format_msg(username, content, timestamp=None):
    if not timestamp:
        timestamp = get_current_timestamp()
    return f"[{timestamp}] {username}: {content}"

# --- Routes ---

@app.route("/", methods=["GET", "POST"])
def index():
    if "username" in session:
        return redirect(url_for("open_chat"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if check_user(username, password):
            session["username"] = username
            return redirect(url_for("open_chat"))
        else:
            return render_template("login.html", error="Invalid credentials")
    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if "username" in session:
        return redirect(url_for("open_chat"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not username or not password:
             return render_template("register.html", error="Please fill all fields")

        if password != confirm_password:
             return render_template("register.html", error="Passwords do not match")
        
        # Save user (db handles duplicate check via unique constraint logic in save_user)
        from database import save_user 
        if save_user(username, password):
            session["username"] = username
            return redirect(url_for("open_chat"))
        else:
             return render_template("register.html", error="Username already exists")

    return render_template("register.html")

@app.route("/open-chat")
def open_chat():
    if "username" not in session:
        return redirect(url_for("index"))
    
    username = session["username"]
    
    return render_template("open_chat.html", username=username)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/modify", methods=["GET", "POST"])
def modify():
    if "username" not in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = session["username"] # Use session username for security
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")

        # Verify old password first
        if check_user(username, old_password):
            update_user_password(username, new_password)
            return redirect(url_for("open_chat"))
        else:
             return render_template("modify.html", error="Incorrect password")

    return render_template("modify.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Construct URL
        file_url = f"/uploads/{filename}"
        return jsonify({"success": True, "url": file_url, "filename": filename})

    return jsonify({"success": False, "error": "File type not allowed"}), 400

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- Socket Events ---

@socketio.on("connect")
def handle_connect():
    if "username" not in session:
        return False

    messages = get_messages()
    for msg in messages:
        timestamp_str = msg['timestamp']
        try:
            dt_utc = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            dt_mtl = dt_utc.replace(tzinfo=pytz.utc).astimezone(MONTREAL_TZ)
            ts_display = dt_mtl.strftime("%y-%m-%d %H:%M")
        except ValueError:
            ts_display = timestamp_str

        # Send structured data
        payload = {
            "username": msg['username'],
            "content": msg['content'],
            "timestamp": ts_display
        }
        emit('message', payload)

@socketio.on("message")
def handle_message(msg):
    if "username" not in session:
        return

    username = session['username']
    timestamp = get_current_timestamp()
    
    # Save raw message
    save_message(msg, username)
    
    # Broadcast structured data
    payload = {
        "username": username,
        "content": msg,
        "timestamp": timestamp
    }
    emit('message', payload, broadcast=True)

if __name__ == "__main__":
    # Ensure DB is ready
    if not os.path.exists('chat.db'):
        init_db()
        
    port = int(os.getenv("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=True)
