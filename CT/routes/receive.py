# routes/receive.py
from flask import Blueprint, request, jsonify
from state_manager import state
from logger import log

receive_bp = Blueprint("receive", __name__)

@receive_bp.post("/data")
def receive_data():
    data = request.json
    log.write(f"[RECEIVE] {data}")

    vid = data.get("id")
    if vid:
        state.update_vehicle(vid, data)

    return jsonify({"ok": True})
