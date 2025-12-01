# communication_ws.py
from flask_socketio import SocketIO, emit
from logger import log
from state_manager import state

class CommunicationWS:
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.role_map = {}  # role -> sid
        self.sid_map = {}   # sid -> role
        self._register_handlers()

    def _register_handlers(self):
        sio = self.socketio
        from flask import request

        @sio.on("connect")
        def _on_connect():
            print(f"[CONTROL] Client connected")

        @sio.on("disconnect")
        def _on_disconnect():
            sid = request.sid
            role = self.sid_map.pop(sid, None)
            if role:
                self.role_map.pop(role, None)
                log.write(f"[WS] {role} disconnected (sid={sid})")
            else:
                log.write(f"[WS] unknown client disconnected (sid={sid})")

        @sio.on("register")
        def _on_register(data):
            sid = request.sid
            role = data.get("role")
            if not role:
                emit("error", {"msg": "no role provided"})
                return
            prev = self.role_map.get(role)
            if prev:
                self.sid_map.pop(prev, None)
            self.role_map[role] = sid
            self.sid_map[sid] = role
            log.write(f"[WS] Registered {role} (sid={sid})")
            emit("stage_update", {"stage": state.get_global_stage()})

        @sio.on("ev_state")
        def _on_ev_state(data):
            sid = request.sid
            role = self.sid_map.get(sid) or data.get("id") or data.get("from")
            if not role:
                log.write(f"[WS] ev_state received but no role found: {data}")
                return
            state.update_vehicle(role, data)
            log.write(f"[WS] state updated from {role}: {data}")
            sio.emit("vehicle_update", {"id": role, "state": state.get_vehicle(role)})

        @sio.on("request_status")
        def _on_request_status(_):
            emit("status_all", state.get_all())

    def broadcast_stage(self, stage):
        state.update_global_stage(stage)
        self.socketio.emit("stage_update", {"stage": stage})
        log.write(f"[WS] broadcast stage_update -> {stage}")

    def send_to(self, role, event, data):
        sid = self.role_map.get(role)
        if not sid:
            log.write(f"[WS] send_to failed: {role} not connected")
            return False
        try:
            self.socketio.emit(event, data, to=sid)
            return True
        except Exception as e:
            log.write(f"[WS] send_to exception: {e}")
            return False

# 싱글톤 사용 가능
comm = None  # app.py에서 CommunicationWS(socketio)로 초기화
