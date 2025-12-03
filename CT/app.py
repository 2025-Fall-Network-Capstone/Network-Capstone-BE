import eventlet
eventlet.monkey_patch()

from flask import Flask, jsonify
from flask_socketio import SocketIO, emit
from state import ControlState

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# -----------------------
# 상태관리
# -----------------------
state = ControlState()


# ================================
# 0. CT → Front : 1단계 시작 신호
# ================================
@app.route("/start_stage1", methods=["POST"])
def start_stage1():
    print("[CT] Stage 1 Start Triggered")
    state.update_stage(1)

    # 프론트로 다시 1단계 시작 신호 보내기
    socketio.emit("stage_1_start", {"stage": 1})
    print("[CT] Sent stage_1_start to front")

    return jsonify({"status": "ok", "stage": 1})


# ================================
# 1. Front → CT : 단계 제어 명령
# ================================
@socketio.on("control_start")
def handle_control_start(data):
    print("[CONTROL START RECEIVED]", data)

    stage = data.get("stage")
    if stage is None:
        print("[CT] ERROR: stage missing")
        return

    state.update_stage(stage)

    # 다른 노드들에게 브로드캐스트
    socketio.emit("stage_update", {"stage": stage})
    print(f"[CT] Broadcast stage_update: {stage}")


# ================================
# 2. 차량들 → CT : 상태 업데이트
#    반드시 수정된 핵심 부분
# ================================

# AV1이 보내는 이벤트: av1_state
@socketio.on("av1_state")
def handle_av1_state(data):
    print("[CT] AV1 State Update:", data)
    state.update_vehicle("AV1", data)


# AV2가 보내는 이벤트: av2_state
@socketio.on("av2_state")
def handle_av2_state(data):
    print("[CT] AV2 State Update:", data)
    state.update_vehicle("AV2", data)


# EV가 보내는 이벤트: ev_state
@socketio.on("ev_state")
def handle_ev_state(data):
    print("[CT] EV State Update:", data)
    state.update_vehicle("EV", data)


# ================================
# 3. CT 상태 조회(GET)
# ================================
@app.route("/status", methods=["GET"])
def get_status():
    return jsonify(state.get_all())


# ================================
# 4. 서버 시작
# ================================
if __name__ == "__main__":
    print("Running CT server (with eventlet)…")
    socketio.run(app, host="0.0.0.0", port=5004, debug=True)
