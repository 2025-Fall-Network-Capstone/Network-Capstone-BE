# communication_ws.py (AV2 전용)
import socketio
from config import CONTROL, EV, AV1

class CommunicationWS:
    def __init__(self, state):
        self.state = state

        self.control_client = socketio.Client()
        self.ev_client = socketio.Client()
        self.av1_client = socketio.Client()

        self.connect_all()

    def connect_all(self):
        # CONTROL
        try:
            self.control_client.connect(f"http://{CONTROL}")
            print("[AV2] Connected to CONTROL")
        except:
            print("[AV2] Failed to connect CONTROL")

        # EV
        try:
            self.ev_client.connect(f"http://{EV}")
            print("[AV2] Connected to EV")
        except:
            print("[AV2] Failed to connect EV")

        # AV1
        try:
            self.av1_client.connect(f"http://{AV1}")
            print("[AV2] Connected to AV1")
        except:
            print("[AV2] Failed to connect AV1")

    def send_state(self):
        data = self.state.get()
        try:
            self.control_client.emit("av2_state", data)
            self.ev_client.emit("av2_state", data)
            self.av1_client.emit("av2_state", data)
        except:
            pass
