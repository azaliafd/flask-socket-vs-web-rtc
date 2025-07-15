import time
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

connection_start_times = {}
last_bandwidth_check = {}
total_bytes_received = {}

@app.route('/')
def index():
    return render_template('socket_video.html')

@socketio.on('connect')
def handle_connect():
    sid = request.sid
    connection_start_times[sid] = time.time()
    last_bandwidth_check[sid] = time.time()
    total_bytes_received[sid] = 0
    print(f"[SocketIO] Client connected: {sid}")

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    start = connection_start_times.pop(sid, None)
    last_bandwidth_check.pop(sid, None)
    total_bytes_received.pop(sid, None)
    if start:
        duration = time.time() - start
        print(f"[SocketIO] Client disconnected: {sid} after {duration:.2f} seconds")

@socketio.on('video_frame')
def handle_video(data):
    sid = request.sid

    sent_time = data.get('time', 0)
    current_time_ms = time.time() * 1000  # ms
    latency = current_time_ms - sent_time

    frame = data['data']
    frame_bytes = len(frame.encode('utf-8'))
    now = time.time()

    # Update akumulasi bytes untuk client ini
    total_bytes_received[sid] += frame_bytes

    # Hitung elapsed waktu sejak pemeriksaan terakhir
    elapsed = now - last_bandwidth_check[sid]

    # Hitung bandwidth tiap 4 detik
    if elapsed >= 4:
        bandwidth_kbps = (total_bytes_received[sid] * 8) / 1000 / elapsed
        print(f"[SocketIO] Bandwidth: {bandwidth_kbps:.2f} kbps")
        total_bytes_received[sid] = 0
        last_bandwidth_check[sid] = now

    connection_time = now - connection_start_times.get(sid, now)
    print(f"[SocketIO] Latency: {latency:.2f} ms | Connection Time: {connection_time:.2f} s")

    emit('video_feed', frame, broadcast=True, include_self=False)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
