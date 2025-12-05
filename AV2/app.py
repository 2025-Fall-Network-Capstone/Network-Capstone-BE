from flask import Flask
from flask_socketio import SocketIO
from state_manager import state
from communication_ws import CommunicationWS
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
comm = CommunicationWS(state)


# ======================================================
# 1) CONTROL → stage_update 수신
# ======================================================
@socketio.on("stage_update")
def handle_stage_update(data):
    stage = data.get("stage")

    if stage is not None:
        # 1) AV2 state_manager 업데이트
        state.update_stage(stage)
        print(f"[AV2] Stage updated to {stage}")

        # 2) 프론트에 stage 알림 전송
        socketio.emit("stage_update", data)

        # 3) 프론트에 최신 AV2 상태 즉시 push
        socketio.emit("av2_state", state.get())


# ======================================================
# 2) EV → AV2 데이터 수신 → 프론트로 forward
# ======================================================
@socketio.on("ev_state")
def handle_ev_state(data):
    print("[AV2] Received EV state:", data)
    socketio.emit("ev_state", data)   # 프론트로 push


# ======================================================
# 3) AV1 → AV2 데이터 수신 → 프론트로 forward
# ======================================================
@socketio.on("av1_state")
def handle_av1_state(data):
    print("[AV2] Received AV1 state:", data)
    socketio.emit("av1_state", data)   # 프론트로 push


# ======================================================
# 4) AV2 state 주기적 전송 (CONTROL/EV/AV1 + 프론트)
# ======================================================
def send_state_loop():
    while True:
        # 백→백 통신
        comm.send_state()

        # 백→프론트 통신
        socketio.emit("av2_state", state.get())

        time.sleep(1)


# ======================================================
# 5) 서버 실행
# ======================================================
if __name__ == "__main__":
    t = threading.Thread(target=send_state_loop)
    t.daemon = True
    t.start()

    socketio.run(app, host="192.168.0.7", port=5002)
