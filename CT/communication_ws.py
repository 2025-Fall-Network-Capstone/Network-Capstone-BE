# communication_ws.py
import socketio
import time
from config import EV, AV1, AV2

class CommunicationWS:
    def __init__(self):
        # CT 서버 상태 자체는 state.py에서 관리
        self.control_client = socketio.Client(reconnection=True, reconnection_attempts=0)
        self.ev_client = socketio.Client(reconnection=True, reconnection_attempts=0)
        self.av1_client = socketio.Client(reconnection=True, reconnection_attempts=0)
        self.av2_client = socketio.Client(reconnection=True, reconnection_attempts=0)

        import threading
        t = threading.Thread(target=self.connect_all_loop)
        t.daemon = True
        t.start()

        # EV / AV1 / AV2 상태 수신 이벤트 설정
        self.ev_client.on("ev_state", self.handle_ev_state)
        self.av1_client.on("av1_state", self.handle_vehicle_state)
        self.av2_client.on("av2_state", self.handle_vehicle_state)

    def connect_all_loop(self):
        """서버 연결을 시도하고 실패하면 재시도"""
        while True:
            self.try_connect(self.control_client, "CONTROL", "[CT] CONTROL")
            self.try_connect(self.ev_client, EV, "[CT] EV")
            self.try_connect(self.av1_client, AV1, "[CT] AV1")
            self.try_connect(self.av2_client, AV2, "[CT] AV2")
            time.sleep(5)  # 5초마다 재시도

    def try_connect(self, client, addr, name):
        if not client.connected:
            try:
                client.connect(f"http://{addr}")
                print(f"{name} connected")
            except Exception as e:
                print(f"{name} connection failed: {e}")

    def broadcast(self, event, data):
        """모든 노드에 이벤트 전송"""
        try:
            if self.control_client.connected:
                self.control_client.emit(event, data)
            if self.ev_client.connected:
                self.ev_client.emit(event, data)
            if self.av1_client.connected:
                self.av1_client.emit(event, data)
            if self.av2_client.connected:
                self.av2_client.emit(event, data)
        except Exception as e:
            print(f"[CT] broadcast error: {e}")

    def handle_ev_state(self, data):
        print("[CT] Received EV state:", data)

    def handle_vehicle_state(self, data):
        vid = data.get("id", "UNKNOWN")
        print(f"[CT] Received {vid} state:", data)

# CT 전역에서 사용할 객체
comm = CommunicationWS()
