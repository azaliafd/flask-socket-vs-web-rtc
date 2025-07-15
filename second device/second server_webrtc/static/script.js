const socket = io(); // otomatis ambil domain ngrok kamu
socket.emit("join");

const pc = new RTCPeerConnection({
  iceServers: [{ urls: "stun:stun.l.google.com:19302" }],
});

const localVideo = document.getElementById("localVideo");
const remoteVideo = document.getElementById("remoteVideo");

let localStream;
const urlParams = new URLSearchParams(window.location.search);
const role = urlParams.get("role"); // bisa 'caller' atau 'callee'

async function start() {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    alert("getUserMedia not supported in your browser");
    return;
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    localStream = stream;
    localVideo.srcObject = stream;
    stream.getTracks().forEach((track) => pc.addTrack(track, stream));

    if (role === "caller") {
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);
      socket.emit("signal", offer);
    }
  } catch (error) {
    console.error("getUserMedia error:", error);
  }
}

socket.on("init", () => {
  start(); // Mulai setelah dapat init dari server
});

// tampilkan video dari remote peer
pc.ontrack = (event) => {
  remoteVideo.srcObject = event.streams[0];
};

// kirim candidate ke peer
pc.onicecandidate = (event) => {
  if (event.candidate) {
    socket.emit("signal", { type: "candidate", candidate: event.candidate });
  }
};

// respon signaling
socket.on("signal", async (data) => {
  if (data.type === "offer" && role === "callee") {
    await pc.setRemoteDescription(new RTCSessionDescription(data));
    const answer = await pc.createAnswer();
    await pc.setLocalDescription(answer);
    socket.emit("signal", answer);
  } else if (data.type === "answer" && role === "caller") {
    await pc.setRemoteDescription(new RTCSessionDescription(data));
  } else if (data.type === "candidate") {
    await pc.addIceCandidate(new RTCIceCandidate(data.candidate));
  }
});
