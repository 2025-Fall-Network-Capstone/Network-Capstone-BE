# communication_ws.py
import socketio
import threading
from logger import log
import config

class WSCommunicator:
    """CT가 EV/AV1/AV2 서버에 WebSocket(Client)으로 접속하는 모듈"""

    def __init__(self):
        self.targets = {
            "EV": f"http://{config.EV}",
            "AV1": f"http://{config.AV1}",
            "AV2": f"http://{config.AV2}",
        }
        self.clients = {}

    def connect(self, role):
        if role in self.clients and self.clients[role].connected:
            return

        sio = socketio.Client()

        @sio.event
        def connect():
            log.write(f"[COMM] Connected to {role}")

        @sio.event
        def disconnect():
            log.write(f"[COMM] Disconnected from {role}")

        try:
            sio.connect(self.targets[role], transports=["websocket"])
            self.clients[role] = sio
        except Exception as e:
            log.write(f"[COMM] Connection failed to {role}: {e}")

    def connect_all(self):
        for role in self.targets:
            threading.Thread(target=self.connect, args=(role,), daemon=True).start()

    def emit(self, role, event, data=None):
        data = data or {}
        if role not in self.clients or not self.clients[role].connected:
            self.connect(role)

        try:
            self.clients[role].emit(event, data)
            log.write(f"[COMM] → {role} event={event} data={data}")
        except Exception as e:
            log.write(f"[COMM ERROR] Emit failed to {role}: {e}")

    def broadcast(self, event, data=None):
        for r in self.targets:
            self.emit(r, event, data)

comm = WSCommunicator()
