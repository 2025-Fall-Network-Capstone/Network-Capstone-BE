from flask import Flask
from flask_socketio import SocketIO
from state_manager import state
from communication_ws import CommunicationWS
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# EV → CONTROL/AV1/AV2 연결
comm = CommunicationWS(state)

# stage 변화 감지용
last_av1_stage = None
last_av2_stage = None
first_av1_received = False
first_av2_received = False


# ======================================================
# 1) CONTROL → EV : stage_update 수신
# ======================================================
@socketio.on("stage_update")
def handle_stage_update(data):
    stage = data.get("stage")

    if stage is not None:
        # 1) EV 내부 상태 업데이트
        state.update_stage(stage)
        print(f"[EV] Stage updated to {stage}")

        # 2) 프론트에 stage 변화 push
        socketio.emit("stage_update", data)

        # 3) 변경된 최신 EV 상태 즉시 push
        socketio.emit("ev_state", state.get())


# ======================================================
# 2) AV1 → EV 상태 수신 (필터 + 프론트 forward)
# ======================================================
@socketio.on("av1_state")
def handle_av1_state(data):
    global last_av1_stage, first_av1_received

    new_stage = data.get("stage")

    # 1) 첫 데이터는 무조건 프린트
    if not first_av1_received:
        print("[EV SERVER] AV1 First Data:", data)
        first_av1_received = True
        last_av1_stage = new_stage
    else:
        # 2) stage 바뀌었을 때만 찍기
        if new_stage is not None and new_stage != last_av1_stage:
            print("[EV SERVER] AV1 Data (stage changed):", data)
            last_av1_stage = new_stage

    # ⭐ 프론트로도 전송
    socketio.emit("av1_state", data)


# ======================================================
# 3) AV2 → EV 상태 수신 (필터 + 프론트 forward)
# ======================================================
@socketio.on("av2_state")
def handle_av2_state(data):
    global last_av2_stage, first_av2_received

    new_stage = data.get("stage")

    if not first_av2_received:
        print("[EV SERVER] AV2 First Data:", data)
        first_av2_received = True
        last_av2_stage = new_stage
    else:
        if new_stage is not None and new_stage != last_av2_stage:
            print("[EV SERVER] AV2 Data (stage changed):", data)
            last_av2_stage = new_stage

    # ⭐ 프론트로 전송
    socketio.emit("av2_state", data)


# ======================================================
# 4) EV → 외부로 주기적 전송 + 프론트 ev_state push
# ======================================================
def send_state_loop():
    while True:
        # CONTROL/AV1/AV2로 보내기
        comm.send_state()

        # 프론트로도 보내기
        socketio.emit("ev_state", state.get())

        time.sleep(1)


# ======================================================
# 5) 서버 실행
# ======================================================
if __name__ == "__main__":
    t = threading.Thread(target=send_state_loop)
    t.daemon = True
    t.start()

    socketio.run(app, host="192.168.0.34", port=5000)
