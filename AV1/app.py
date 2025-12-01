from flask import Flask
from flask_socketio import SocketIO
from state_manager import state
from communication_ws import CommunicationWS
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
comm = CommunicationWS(state)

# EV에서 state 수신
@socketio.on("ev_state")
def handle_ev_state(data):
    print("[AV1] Received EV state:", data)

# AV2에서 state 수신
@socketio.on("av2_state")
def handle_av2_state(data):
    print("[AV1] Received AV2 state:", data)

# CONTROL에서 stage + EV 정보 수신
@socketio.on("stage_update")
def handle_stage_update(data):
    stage = data.get("stage")
    if stage is not None:
        state.update_stage(stage)
        print(f"[AV1] Stage updated to {stage}")

# AV1 state 주기적 전송
def send_state_loop():
    while True:
        comm.send_state()
        time.sleep(1)

if __name__ == "__main__":
    t = threading.Thread(target=send_state_loop)
    t.daemon = True
    t.start()
    socketio.run(app, host="0.0.0.0", port=5001)
