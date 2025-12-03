# routes/status.py
from flask import Blueprint, jsonify
from state_manager import state

status_bp = Blueprint("status", __name__)

@status_bp.get("/status")
def get_status():
    return jsonify(state.get_all())
