from flask import Blueprint, request, jsonify
from state_manager import StateManager
from communication import Communication

ev_bp = Blueprint("ev", __name__)

state = StateManager("EV")
comm = Communication()

# 관제에서 stage 전달 받기
@ev_bp.route("/stage/update", methods=["POST"])
def stage_update():
    body = request.get_json()
    stage = body.get("stage")

    if stage is None:
        return jsonify({"error": "stage missing"}), 400

    # stage 갱신
    state.update_stage(stage)

    return jsonify({"msg": "stage updated", "stage": stage})

# 관제 / av로 주기적으로 데이터 전송
@ev_bp.route("/ev/send", methods=["POST"])
def send_data():
    data = state.get_data()

    comm.send_to_control(data)
    comm.send_to_av1(data)
    comm.send_to_av2(data)

    return jsonify({"msg": "sent", "data": data})