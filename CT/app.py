# app.py
import eventlet
eventlet.monkey_patch()

import time

from flask import Flask, jsonify
from flask_socketio import SocketIO

from state import ControlState
from utils.stage_logic import change_stage
from config import PORT

# 🔥 차량 서버들과의 WS 통신용
from communication_ws import comm

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# -----------------------
# 상태관리 (state.py 래퍼)
# -----------------------
state = ControlState()

# -----------------------
# 로그 주기 제한 (프론트 → CT 차량 상태)
# -----------------------
FRONT_LOG_INTERVAL = 10.0  # 초 단위
last_front_log_time = {
    "EV": 0.0,
    "AV1": 0.0,
    "AV2": 0.0,
}

# -----------------------
# 자동 스테이지 진행 플래그
# -----------------------
auto_stage_running = False


# ================================
# 공통: 현재 상태 snapshot 브로드캐스트
# ================================
def broadcast_status_all():
    """
    현재 CT에 모여 있는 전체 차량 상태(state.get_all())를
    - CONTROL 프론트(React, role=CONTROL)
    - 각 차량 서버(EV/AV1/AV2)
    에 한 번씩 쏴주는 함수.
    (주기적 X, stage 변경 시점 등에서만 호출)
    """
    all_state = state.get_all()  # { "EV": {...}, "AV1": {...}, "AV2": {...} }

    # 1) CONTROL 프론트로 전송
    socketio.emit("status_all", all_state)

    # 2) 차량 서버들(EV / AV1 / AV2)로 전송
    comm.broadcast("status_all", all_state)

    print(f"[CT → FRONT/VEHICLES] status_all: {all_state}")


def broadcast_status_all_delayed(delay: float = 1.0):
    """
    stage 신호를 먼저 쏘고,
    차량들이 새 stage 기준으로 상태(ev_state / av1_state / av2_state)를
    올려줄 시간을 조금 준 뒤 snapshot을 보내기 위한 헬퍼.
    """

    def _worker():
        # 차량들이 상태 올리는 시간 확보
        time.sleep(delay)
        broadcast_status_all()

    socketio.start_background_task(_worker)


# ================================
# 자동 스테이지 진행 워커
#   (이미 stage=1인 상태에서 시작)
#   10초 후 2 -> 3 -> 4 -> 0(종료)
# ================================
def auto_stage_worker():
    """
    /start_stage1 또는 control_start(stage=1)에서 호출.
    이 시점에는 이미 stage=1로 변경된 상태라고 가정한다.
    -> stage 1은 그대로 10초 유지
    -> 이후 2, 3, 4를 20초 간격으로 진행
    -> 마지막에 stage 0(종료)로 리셋
    """
    global auto_stage_running

    try:
        # 이미 stage 1 상태이므로, 10초 유지
        print("[AUTO] stage 1 유지 10초 대기")
        time.sleep(10)

        # 2, 3, 4 단계 자동 진행
        for s in [2, 3, 4]:
            print(f"[AUTO] change to stage {s}")
            # 1) CT 내부 상태 + 차량들에 stage 전파
            change_stage(s)
            # 2) 프론트에도 stage 알림
            socketio.emit("stage_update", {"stage": s})
            # 3) 🔥 stage 변경 후, 약간 기다렸다가 snapshot 전송
            broadcast_status_all_delayed(delay=1.0)

            time.sleep(20)

        # 종료 단계: stage 0
        print("[AUTO] stage 종료 (stage 5)")
        change_stage(5)  # 차량들에 stage_update(stage=0) 전파
        socketio.emit("stage_update", {"stage": 5, "ended": True})
        # 필요하면 종료 시에도 상태 한번 더 보낼 수 있음
        # broadcast_status_all_delayed(delay=1.0)
    finally:
        auto_stage_running = False


# ================================
# 0. CT → Front : 1단계 시작 HTTP 트리거
# ================================
@app.route("/start_stage1", methods=["POST"])
def start_stage1():
    global auto_stage_running

    print("[CT] Stage 1 Start Triggered")

    # 바로 stage 1로 변경 (차량들 + CT 내부)
    change_stage(1)

    # 프론트 UI용 이벤트
    socketio.emit("stage_1_start", {"stage": 1})
    socketio.emit("stage_update", {"stage": 1})

    # 🔥 stage 1로 바뀐 직후, 곧바로가 아니라
    #    차량들이 stage=1 상태를 올릴 시간을 약간 준 다음 snapshot 전송
    broadcast_status_all_delayed(delay=1.0)

    # 자동 진행이 안 돌고 있을 때만 백그라운드 작업 시작
    if not auto_stage_running:
        auto_stage_running = True
        socketio.start_background_task(auto_stage_worker)
        print("[AUTO] auto_stage_worker started")

    return jsonify({"status": "ok", "stage": 1})


# ================================
# 1. Front → CT : 통신 시작 신호 (control_start)
# ================================
@socketio.on("control_start")
def handle_control_start(data):
    global auto_stage_running

    print("[CONTROL START RECEIVED]", data)

    # 프론트에서 stage 안 보내면 ⇒ 1단계로 시작
    stage = data.get("stage", 1)

    # 공통 stage 변경 로직 (차량 + CT 내부)
    change_stage(stage)

    # 프론트로 브로드캐스트
    socketio.emit("stage_update", {"stage": stage})
    print(f"[CT] Broadcast stage_update to front: {stage}")

    # 🔥 stage 변경 직후 snapshot도 살짝 딜레이 후 전송
    broadcast_status_all_delayed(delay=1.0)

    # stage=1 들어오면 자동 시퀀스 시작
    if stage == 1 and not auto_stage_running:
        auto_stage_running = True
        socketio.start_background_task(auto_stage_worker)
        print("[AUTO] auto_stage_worker started by control_start")


# ================================
# 2. 차량 상태 (프론트 → CT, 시뮬레이션용)
#    로그는 10초에 한 번만 출력
# ================================
@socketio.on("ev_state")
def handle_ev_state_from_front(data):
    now = time.time()
    if now - last_front_log_time["EV"] >= FRONT_LOG_INTERVAL:
        print("[CT] EV State Update from front:", data)
        last_front_log_time["EV"] = now

    state.update_vehicle("EV", data)


@socketio.on("av1_state")
def handle_av1_state_from_front(data):
    now = time.time()
    if now - last_front_log_time["AV1"] >= FRONT_LOG_INTERVAL:
        print("[CT] AV1 State Update from front:", data)
        last_front_log_time["AV1"] = now

    state.update_vehicle("AV1", data)


@socketio.on("av2_state")
def handle_av2_state_from_front(data):
    now = time.time()
    if now - last_front_log_time["AV2"] >= FRONT_LOG_INTERVAL:
        print("[CT] AV2 State Update from front:", data)
        last_front_log_time["AV2"] = now

    state.update_vehicle("AV2", data)


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
    socketio.run(app, host="0.0.0.0", port=PORT, debug=True)
