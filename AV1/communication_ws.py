import socketio
from config import CONTROL, EV, AV2
from state_manager import state

class CommunicationWS:
    def __init__(self, state):
        self.state = state
        # WebSocket 클라이언트
        self.control_client = socketio.Client()
        self.ev_client = socketio.Client()
        self.av2_client = socketio.Client()
        self.connect_all()

    def connect_all(self):
        try:
            self.control_client.connect(f"http://{CONTROL}")
            print("[AV1] Connected to CONTROL")
        except:
            print("[AV1] Failed to connect CONTROL")

        try:
            self.ev_client.connect(f"http://{EV}")
            print("[AV1] Connected to EV")
        except:
            print("[AV1] Failed to connect EV")

        try:
            self.av2_client.connect(f"http://{AV2}")
            print("[AV1] Connected to AV2")
        except:
            print("[AV1] Failed to connect AV2")

    def send_state(self):
        data = self.state.get()
        try:
            self.control_client.emit("av1_state", data)
            self.av2_client.emit("av1_state", data)
        except:
            pass
