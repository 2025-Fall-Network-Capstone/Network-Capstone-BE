# communication_ws.py
import socketio
import time
from config import CONTROL, AV1, AV2

class CommunicationWS:
    def __init__(self, state):
        self.state = state

        self.control_client = socketio.Client(reconnection=False)
        self.av1_client = socketio.Client(reconnection=False)
        self.av2_client = socketio.Client(reconnection=False)

        import threading
        t = threading.Thread(target=self.reconnect_loop)
        t.daemon = True
        t.start()

    def reconnect_loop(self):
        """연결 안된 경우에만 connect() 시도"""
        while True:
            self.safe_connect(self.control_client, CONTROL, "[EV] CONTROL")
            self.safe_connect(self.av1_client, AV1, "[EV] AV1")
            self.safe_connect(self.av2_client, AV2, "[EV] AV2")
            time.sleep(3)

    def safe_connect(self, client, addr, name):
        """연결 안된 경우에만 connect 실행"""
        if not client.connected:
            try:
                client.connect(f"http://{addr}")
                print(f"{name} connected")
            except Exception as e:
                print(f"{name} connect failed: {e}")

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
