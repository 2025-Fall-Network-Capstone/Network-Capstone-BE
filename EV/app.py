from flask import Flask
from flask_socketio import SocketIO
from state_manager import state
from communication_ws import CommunicationWS
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
comm = CommunicationWS(state)

# 관제에서 stage 수신
@socketio.on('stage_update')
def handle_stage_update(data):
    stage = data.get("stage")
    if stage is not None:
        state.update_stage(stage)
        print(f"[EV] Stage updated to {stage}")

# EV state 주기적 전송
def send_state_loop():
    while True:
        comm.send_state()
        time.sleep(1)

if __name__ == "__main__":
    t = threading.Thread(target=send_state_loop)
    t.daemon = True
    t.start()
    socketio.run(app, host="192.168.0.58", port=5000)
