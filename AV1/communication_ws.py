import socketio
import time
from config import CONTROL, EV, AV2

class CommunicationWS:
    def __init__(self, state):
        self.state = state

        self.control_client = socketio.Client(reconnection=True, reconnection_attempts=0)
        self.ev_client = socketio.Client(reconnection=True, reconnection_attempts=0)
        self.av2_client = socketio.Client(reconnection=True, reconnection_attempts=0)

        # 서버 연결을 별도 스레드에서 계속 시도
        import threading
        t = threading.Thread(target=self.connect_all_loop)
        t.daemon = True
        t.start()

    def connect_all_loop(self):
        while True:
            self.try_connect(self.control_client, CONTROL, "[AV1] CONTROL")
            self.try_connect(self.ev_client, EV, "[AV1] EV")
            self.try_connect(self.av2_client, AV2, "[AV1] AV2")
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
                self.control_client.emit("av1_state", data)
            if self.ev_client.connected:
                self.ev_client.emit("av1_state", data)
            if self.av2_client.connected:
                self.av2_client.emit("av1_state", data)
        except Exception as e:
            print(f"[AV1] send_state error: {e}")
