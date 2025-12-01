# routes/control.py
from flask import Blueprint, request, jsonify
from logger import log
from state_manager import state
from utils.stage_logic import change_stage
from communication_ws import comm

control_bp = Blueprint("control", __name__)

@control_bp.post("/stage")
def update_stage():
    stage = request.json.get("stage")
    log.write(f"[STAGE CHANGE] → {stage}")
    state.update_global_stage(stage)
    change_stage(stage)
    try:
        comm.broadcast_stage(stage)
    except Exception as e:
        log.write(f"[STAGE] broadcast failed: {e}")
    return jsonify({"ok": True})
