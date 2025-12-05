# communication_ws.py
import socketio
import threading
import time
from config import CONTROL, EV, AV1, AV2
from logger import log
from state_manager import state

class CommunicationWS:
    def __init__(self):

        self.ev_client = socketio.Client()
        self.av1_client = socketio.Client()
        self.av2_client = socketio.Client()

        # 차량 이벤트 수신 핸들러 등록
        self.ev_client.on("vehicle_state", self.handle_vehicle_state)
        self.av1_client.on("vehicle_state", self.handle_vehicle_state)
        self.av2_client.on("vehicle_state", self.handle_vehicle_state)

        t = threading.Thread(target=self.connect_all_loop)
        t.daemon = True
        t.start()

    def connect_all_loop(self):
        while True:
            self.try_connect(self.ev_client, EV, "[CT] EV")
            self.try_connect(self.av1_client, AV1, "[CT] AV1")
            self.try_connect(self.av2_client, AV2, "[CT] AV2")
            time.sleep(5)

    def try_connect(self, client, addr, name):
        if not client.connected:
            try:
                client.connect(f"http://{addr}")
                log.write(f"{name} connected")
            except Exception as e:
                log.write(f"{name} connection failed: {e}")

    # 🔥 차량 상태 수신
    def handle_vehicle_state(self, data):
        vid = data.get("id")
        state.update_vehicle(vid, data)
        log.write(f"[CT] {vid} 상태 수신 (WS): {data}")

    # broadcast
    def broadcast(self, event, data):
        for client in [self.ev_client, self.av1_client, self.av2_client]:
            if client.connected:
                client.emit(event, data)

    # emit
    def emit(self, target, event, data):
        mapping = {
            "EV": self.ev_client,
            "AV1": self.av1_client,
            "AV2": self.av2_client,
        }
        client = mapping.get(target)
        if client and client.connected:
            client.emit(event, data)


comm = CommunicationWS()
