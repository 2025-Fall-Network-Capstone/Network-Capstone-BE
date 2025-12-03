# routes/control.py
from flask import Blueprint, request, jsonify
from utils.stage_logic import change_stage
from logger import log

control_bp = Blueprint("control", __name__)

@control_bp.post("/stage")
def update_stage():
    stage = request.json.get("stage")
    if stage is None:
        return jsonify({"ok": False}), 400
    log.write(f"[CONTROL] Stage 변경 → {stage}")
    change_stage(stage)
    return jsonify({"ok": True})
