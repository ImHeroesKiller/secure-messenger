from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from config import Config
from models import SessionLocal, Message, User
from utils.crypto import encrypt_message, decrypt_message
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
db = SessionLocal()

# ==================== AUTH ====================
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if db.query(User).filter_by(username=username).first():
        return jsonify({"error": "Username sudah dipakai"}), 400

    new_user = User(username=username)
    new_user.set_password(password)
    db.add(new_user)
    db.commit()
    return jsonify({"status": "success"})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = db.query(User).filter_by(username=data.get('username')).first()
    if user and user.check_password(data.get('password')):
        session['user_id'] = user.id
        session['username'] = user.username
        return jsonify({"status": "success", "username": user.username})
    return jsonify({"error": "Login gagal"}), 401

@app.route('/logout')
def logout():
    session.clear()
    return jsonify({"status": "logged out"})

# ==================== CHAT + ROOMS ====================
@app.route('/')
def index():
    if 'user_id' not in session:
        return render_template('index.html', logged_in=False)
    return render_template('index.html', logged_in=True, username=session.get('username'))

@socketio.on('join_room')
def handle_join_room(data):
    room = data.get('room', 'general')
    join_room(room)
    print(f"{session.get('username')} joined room: {room}")

@socketio.on('leave_room')
def handle_leave_room(data):
    room = data.get('room', 'general')
    leave_room(room)

@socketio.on('send_message')
def handle_send_message(data):
    if 'user_id' not in session:
        return

    content = data.get('message', '')
    room = data.get('room', 'general')

    if not content:
        return

    encrypted = encrypt_message(content, Config.ENCRYPTION_KEY)
    
    new_msg = Message(
        sender_id=session['user_id'],
        content_encrypted=encrypted,
        room=room
    )
    db.add(new_msg)
    db.commit()

    # Broadcast hanya ke room tersebut
    emit('new_message', {
        'content': content,
        'username': session.get('username'),
        'time': datetime.now().strftime("%H:%M"),
        'room': room
    }, room=room)

@app.route('/messages')
def get_messages():
    if 'user_id' not in session:
        return jsonify({"error": "Harus login"}), 401

    room = request.args.get('room', 'general')
    messages = db.query(Message).filter_by(room=room).order_by(Message.timestamp.desc()).limit(30).all()
    
    result = []
    for msg in messages:
        try:
            decrypted = decrypt_message(msg.content_encrypted, Config.ENCRYPTION_KEY)
        except:
            decrypted = "[Gagal dekripsi]"
        
        result.append({
            "id": msg.id,
            "content": decrypted,
            "username": db.query(User).get(msg.sender_id).username if msg.sender_id else "Unknown",
            "time": msg.timestamp.strftime("%H:%M"),
            "is_mine": msg.sender_id == session['user_id']
        })
    
    return jsonify(result)

if __name__ == '__main__':
    print("🚀 Multiple Rooms Secure Messenger running...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
