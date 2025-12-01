# communication_ws.py (EV 전용)
import socketio
from config import CONTROL, AV1, AV2

class CommunicationWS:
    def __init__(self, state):
        self.state = state

        self.control_client = socketio.Client()
        self.av1_client = socketio.Client()
        self.av2_client = socketio.Client()

        self.connect_all()

    def connect_all(self):
        # CONTROL
        try:
            self.control_client.connect(f"http://{CONTROL}")
            print("[EV] Connected to CONTROL")
        except:
            print("[EV] Failed to connect CONTROL")

        # AV1
        try:
            self.av1_client.connect(f"http://{AV1}")
            print("[EV] Connected to AV1")
        except:
            print("[EV] Failed to connect AV1")

        # AV2
        try:
            self.av2_client.connect(f"http://{AV2}")
            print("[EV] Connected to AV2")
        except:
            print("[EV] Failed to connect AV2")

    def send_state(self):
        data = self.state.get()
        try:
            self.control_client.emit("ev_state", data)
            self.av1_client.emit("ev_state", data)
            self.av2_client.emit("ev_state", data)
        except:
            pass
