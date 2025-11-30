from flask import Blueprint, request, jsonify
from state_manager import StateManager
from communication import Communication

av2_bp = Blueprint("av2", __name__)

state = StateManager("AV2")
comm = Communication()

# 관제에서 데이터 받기
@av2_bp.route("/stage/update", methods=["POST"])
def stage_update():
    body = request.get_json()

    stage = body.get("stage")
    ev_info = body.get("ev_info")

    if stage is None:
        return jsonify({"error": "stage missing"}), 400

    state.update_stage(stage)

    if ev_info:
        state.update_ev_info(ev_info)

    return jsonify({"msg": "stage updated", "stage": stage})


# EV에서 데이터 받기
@av2_bp.route("/ev/data", methods=["POST"])
def ev_data():
    body = request.get_json()
    state.update_from_ev(body)
    return jsonify({"msg": "ev data received"})

# AV1에서 받기
@av2_bp.route("/av1/data", methods=["POST"])
def av1_data():
    body = request.get_json()
    state.update_from_av1(body)
    return jsonify({"msg": "av1 data received"})


# AV2에서 데이터 보내기
@av2_bp.route("/av2/send", methods=["POST"])
def send_data():
    data = state.get_data()

    comm.send_to_control(data)
    comm.send_to_av1(data)

    return jsonify({"msg": "sent", "data": data})