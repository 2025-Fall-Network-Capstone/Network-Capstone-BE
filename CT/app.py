# app.py (CT - Control Tower)

import eventlet
eventlet.monkey_patch()

from flask import Flask, jsonify, request
from flask_socketio import SocketIO

from config import PORT
from state_manager import state
from utils.stage_logic import change_stage
from routes.control import control_bp
from routes.receive import receive_bp
from routes.status import status_bp
from logger import log

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")


# =========================================
# 0. CT → Front : 1단계 시작 HTTP 트리거
#    (프론트에서 버튼 눌러서 호출할 수 있게)
# =========================================
@app.route("/start_stage1", methods=["POST"])
def start_stage1():
    print("[CT] Stage 1 Start Triggered")

    # 🔥 전체 stage 변경 로직은 항상 여기로 통일
    change_stage(1)

    # 프론트에만 알려주는 이벤트 (UI용)
    socketio.emit("stage_1_start", {"stage": 1})
    print("[CT] Sent stage_1_start to front")

    return jsonify({"status": "ok", "stage": 1})


# =========================================
# 1. Front → CT : Socket.IO로 stage 변경 요청
#    event: "control_start"
# =========================================
@socketio.on("control_start")
def handle_control_start(data):
    print("[CONTROL START RECEIVED FROM FRONT]", data)

    stage = data.get("stage")
    if stage is None:
        print("[CT] ERROR: stage missing")
        return

    # 🔥 공통 로직 사용 (차량 3대 + CT state + 로그 + 시나리오 실행)
    change_stage(stage)

    # 프론트 쪽에 현재 stage 브로드캐스트 (React 여러 탭/클라이언트용)
    socketio.emit("stage_update", {"stage": stage})
    print(f"[CT] Broadcast stage_update to front: {stage}")


# =========================================
# 2. Front → CT : 차량 상태를 프론트에서 보내는 경우 (시뮬레이션용)
#    실 차량은 communication_ws.py 경유로 들어오고,
#    프론트에서 가짜 상태 넣고 싶을 때는 이 이벤트로 덮어쓰기 가능
# =========================================

@socketio.on("ev_state")
def handle_ev_state_from_front(data):
    print("[CT] EV State Update from front:", data)
    state.update_vehicle("EV", data)

@socketio.on("av1_state")
def handle_av1_state_from_front(data):
    print("[CT] AV1 State Update from front:", data)
    state.update_vehicle("AV1", data)

@socketio.on("av2_state")
def handle_av2_state_from_front(data):
    print("[CT] AV2 State Update from front:", data)
    state.update_vehicle("AV2", data)


# =========================================
# 3. 기존 REST 라우트( /stage, /data, /status ) 등록
#    - /stage  : routes/control.py  (POST, JSON {stage})
#    - /data   : routes/receive.py (POST, 차량 상태 수신)
#    - /status : routes/status.py  (GET, 전체 상태 조회)
# =========================================
app.register_blueprint(control_bp)
app.register_blueprint(receive_bp)
app.register_blueprint(status_bp)


# =========================================
# 4. 서버 시작
#    config.PORT = 5003 이므로 CONTROL = "HOST:5003" 과 일치
# =========================================
if __name__ == "__main__":
    print("Running CT server (with eventlet)…")
    socketio.run(app, host="0.0.0.0", port=PORT, debug=True)
