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
# 1) EV에서 state 수신 → 프론트로 바로 전달
# ======================================================
@socketio.on("ev_state")
def handle_ev_state(data):
    print("[AV1] Received EV state:", data)
    socketio.emit("ev_state", data)   # 프론트로 push!


# ======================================================
# 2) AV2에서 state 수신 → 프론트로 바로 전달
# ======================================================
@socketio.on("av2_state")
def handle_av2_state(data):
    print("[AV1] Received AV2 state:", data)
    socketio.emit("av2_state", data)  # 프론트로 push!


# ======================================================
# 3) CONTROL에서 stage_update 수신
#    → AV1 내부 state 업데이트
#    → 프론트에 즉시 stage & 최신 AV1 상태 push
# ======================================================
@socketio.on("stage_update")
def handle_stage_update(data):
    stage = data.get("stage")

    if stage is not None:
        # 1) AV1 내부 state 업데이트
        state.update_stage(stage)
        print(f"[AV1] Stage updated to {stage}")

        # 2) stage 자체도 프론트로 전달
        socketio.emit("stage_update", data)

        # 3) stage 반영된 최신 AV1 상태도 프론트로 즉시 전달
        socketio.emit("av1_state", state.get())


# ======================================================
# 4) AV1 state 1초 주기 전송 (프론트 + CONTROL + EV + AV2)
# ======================================================
def send_state_loop():
    while True:
        # 백 → 백 통신
        comm.send_state()

        # 백 → 프론트 통신 (실시간 상태)
        socketio.emit("av1_state", state.get())

        time.sleep(1)


# ======================================================
# 5) 서버 실행
# ======================================================
if __name__ == "__main__":
    t = threading.Thread(target=send_state_loop)
    t.daemon = True
    t.start()

    socketio.run(app, host="192.168.0.118", port=5001)
