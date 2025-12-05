from flask import Flask
from flask_socketio import SocketIO
from state_manager import state
from communication_ws import CommunicationWS
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
comm = CommunicationWS(state)

# CONTROL에서 stage + EV 정보 수신
@socketio.on("stage_update")
def handle_stage_update(data):
    stage = data.get("stage")
    if stage is not None:
        state.update_stage(stage)
        print(f"[AV2] Stage updated to {stage}")

# EV에서 state 수신
@socketio.on("ev_state")
def handle_ev_state(data):
    print("[AV2] Received EV state:", data)

# AV1에서 state 수신
@socketio.on("av1_state")
def handle_av1_state(data):
    print("[AV2] Received AV1 state:", data)



# AV2 state 주기적 전송
def send_state_loop():
    while True:
        comm.send_state()
        socketio.emit("av2_state", state.get())
        time.sleep(1)

if __name__ == "__main__":
    t = threading.Thread(target=send_state_loop)
    t.daemon = True
    t.start()
    socketio.run(app, host="192.168.0.7", port=5002)
