from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('webrtc_camera.html')  # kamu bisa pakai file HTML yang dimodifikasi nanti

@socketio.on('signal')
def handle_signal(data):
    # Teruskan pesan signaling ke semua selain pengirim
    emit('signal', data, broadcast=True, include_self=False)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001)
