from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

latencies = []
bandwidths = []
connection_times = []

@app.route('/')
def index():
    return render_template('webrtc_camera.html')

@app.route('/metrics', methods=['POST'])
def log_metrics():
    data = request.get_json()
    now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    metric_type = data.get("type")
    value = data.get("value")

    # Simpan data numerik untuk perhitungan rata-rata
    try:
        if metric_type.lower() == 'latency':
            val = float(value.replace(" ms", "").strip())
            latencies.append(val)
        elif metric_type.lower() == 'bandwidth':
            val = float(value.replace(" kbps", "").strip())
            bandwidths.append(val)
        elif metric_type.lower() == 'connection time':
            val = float(value.replace(" s", "").strip())
            connection_times.append(val)
    except ValueError:
        print(f"Cannot convert {metric_type} value: {value}")

    print(f"[{now}] [WebRTC] {metric_type}: {value}")
    return jsonify(success=True), 200


@app.route('/summary')
def summary():
    def average(lst):
        return round(sum(lst) / len(lst), 2) if lst else 0

    return jsonify({
        "average_latency_ms": average(latencies),
        "average_bandwidth_kbps": average(bandwidths),
        "average_connection_time_s": average(connection_times),
        "samples": {
            "latency": len(latencies),
            "bandwidth": len(bandwidths),
            "connection_time": len(connection_times)
        }
    }), 200

@app.route('/reset', methods=['POST'])
def reset():
    latencies.clear()
    bandwidths.clear()
    connection_times.clear()
    return jsonify(message="All metrics reset."), 200


@socketio.on('signal')
def signaling(message):
    emit('signal', message, broadcast=True, include_self=False)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5002, debug=True)
