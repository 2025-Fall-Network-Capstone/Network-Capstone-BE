from flask import Flask
from flask_socketio import SocketIO
from state_manager import state
from communication_ws import CommunicationWS
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# EV가 CONTROL, AV1, AV2에 연결
comm = CommunicationWS(state)

# stage 초기값 0
last_av1_stage = None
last_av2_stage = None

# 첫 데이터 수신 여부
first_av1_received = False
first_av2_received = False


# -------------------------------
# 관제 → EV : stage 업데이트
# -------------------------------
@socketio.on('stage_update')
def handle_stage_update(data):
    stage = data.get("stage")
    if stage is not None:
        state.update_stage(stage)
        print(f"[EV] Stage updated to {stage}")


# -------------------------------
# AV1 → EV 수신
# -------------------------------
@socketio.on("av1_state")
def handle_av1_state(data):
    global last_av1_stage, first_av1_received

    new_stage = data.get("stage")

    # 1) 첫 데이터는 무조건 출력
    if not first_av1_received:
        print("[EV SERVER] AV1 First Data:", data)
        first_av1_received = True
        last_av1_stage = new_stage if new_stage is not None else last_av1_stage
        return

    # 2) stage 값이 있고, 이전 값과 다르면 출력
    if new_stage is not None and new_stage != last_av1_stage:
        print("[EV SERVER] AV1 Data (stage changed):", data)
        last_av1_stage = new_stage


# -------------------------------
# AV2 → EV 수신
# -------------------------------
@socketio.on("av2_state")
def handle_av2_state(data):
    global last_av2_stage, first_av2_received

    new_stage = data.get("stage")

    # 1) 첫 데이터는 무조건 출력
    if not first_av2_received:
        print("[EV SERVER] AV2 First Data:", data)
        first_av2_received = True
        last_av2_stage = new_stage if new_stage is not None else last_av2_stage
        return

    # 2) stage 값이 있고, 이전 값과 다르면 출력
    if new_stage is not None and new_stage != last_av2_stage:
        print("[EV SERVER] AV2 Data (stage changed):", data)
        last_av2_stage = new_stage


# -------------------------------
# EV state 주기적 전송
# -------------------------------
def send_state_loop():
    while True:
        comm.send_state()
        socketio.emit("ev_state", state.get())
        time.sleep(1)


# -------------------------------
# 서버 실행
# -------------------------------
if __name__ == "__main__":
    t = threading.Thread(target=send_state_loop)
    t.daemon = True
    t.start()

    socketio.run(app, host="192.168.0.34", port=5000)
