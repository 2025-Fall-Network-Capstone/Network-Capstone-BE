# routes/receive.py
from flask import Blueprint, request, jsonify
from logger import log
from state_manager import state
from utils.stage_logic import handle_message

receive_bp = Blueprint("receive", __name__)

@receive_bp.post("/receive")
def receive_data():
    data = request.json
    log.write(f"[RECEIVE] {data}")
    handle_message(data)
    return jsonify({"ok": True})
