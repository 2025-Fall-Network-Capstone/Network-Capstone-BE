import socketio
from config import CONTROL, EV, AV1
from state_manager import state

class CommunicationWS:
    def __init__(self, state):
        self.state = state
        # WebSocket 클라이언트
        self.control_client = socketio.Client()
        self.ev_client = socketio.Client()
        self.av1_client = socketio.Client()
        self.connect_all()

    def connect_all(self):
        try:
            self.control_client.connect(f"http://{CONTROL}")
            print("[AV2] Connected to CONTROL")
        except:
            print("[AV2] Failed to connect CONTROL")

        try:
            self.ev_client.connect(f"http://{EV}")
            print("[AV2] Connected to EV")
        except:
            print("[AV2] Failed to connect EV")

        try:
            self.av1_client.connect(f"http://{AV1}")
            print("[AV2] Connected to AV1")
        except:
            print("[AV2] Failed to connect AV1")

    def send_state(self):
        data = self.state.get()
        try:
            self.control_client.emit("av2_state", data)
            self.av1_client.emit("av2_state", data)
        except:
            pass
