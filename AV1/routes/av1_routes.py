from flask import Blueprint, request, jsonify
from state_manager import StateManager
from communication import Communication

av1_bp = Blueprint("av1", __name__)

state = StateManager("AV1")
comm = Communication()

# ----------------------------------------------------
# 🔥 1) 관제 → AV1 : stage + EV info POST로 받기
# ----------------------------------------------------
@av1_bp.route("/stage/update", methods=["POST"])
def stage_update():
    body = request.get_json()

    stage = body.get("stage")
    ev_info = body.get("ev_info")

    if stage is None:
        return jsonify({"error": "stage missing"}), 400

    # stage 갱신
    state.update_stage(stage)

    # EV 정보도 같이 들어오면 저장
    if ev_info:
        state.update_ev_info(ev_info)

    return jsonify({"msg": "stage updated", "stage": stage})


# ----------------------------------------------------
# 🔥 2) EV → AV1
# ----------------------------------------------------
@av1_bp.route("/ev/data", methods=["POST"])
def ev_data():
    body = request.get_json()
    state.update_from_ev(body)
    return jsonify({"msg": "ev data received"})


# ----------------------------------------------------
# 🔥 3) AV2 → AV1
# ----------------------------------------------------
@av1_bp.route("/av2/data", methods=["POST"])
def av2_data():
    body = request.get_json()
    state.update_from_av2(body)
    return jsonify({"msg": "av2 data received"})


# ----------------------------------------------------
# 🔥 4) AV1 → 관제 / AV2 데이터 PUSH
# ----------------------------------------------------
@av1_bp.route("/av1/send", methods=["POST"])
def send_data():
    data = state.get_data()

    comm.send_to_control(data)
    comm.send_to_av2(data)

    return jsonify({"msg": "sent", "data": data})
