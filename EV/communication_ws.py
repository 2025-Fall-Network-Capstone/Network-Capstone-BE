# communication_ws.py
import socketio
import time
from config import CONTROL, AV1, AV2

class CommunicationWS:
    def __init__(self, state):
        self.state = state

        self.control_client = socketio.Client(reconnection=True, reconnection_attempts=0)
        self.av1_client = socketio.Client(reconnection=True, reconnection_attempts=0)
        self.av2_client = socketio.Client(reconnection=True, reconnection_attempts=0)

        import threading
        t = threading.Thread(target=self.connect_all_loop)
        t.daemon = True
        t.start()

    def connect_all_loop(self):
        """서버 연결을 시도하고 실패하면 재시도"""
        while True:
            self.try_connect(self.control_client, CONTROL, "[EV] CONTROL")
            self.try_connect(self.av1_client, AV1, "[EV] AV1")
            self.try_connect(self.av2_client, AV2, "[EV] AV2")
            time.sleep(5)  # 5초마다 재시도

    def try_connect(self, client, addr, name):
        if not client.connected:
            try:
                client.connect(f"http://{addr}")
                print(f"{name} connected")
            except Exception as e:
                print(f"{name} connection failed: {e}")

    def send_state(self):
        data = self.state.get()
        try:
            if self.control_client.connected:
                self.control_client.emit("ev_state", data)
            if self.av1_client.connected:
                self.av1_client.emit("ev_state", data)
            if self.av2_client.connected:
                self.av2_client.emit("ev_state", data)
        except Exception as e:
            print(f"[EV] send_state error: {e}")
