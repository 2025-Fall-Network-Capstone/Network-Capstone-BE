import socketio
import time
from config import CONTROL, EV, AV2

class CommunicationWS:
    def __init__(self, state):
        self.state = state

        # 외부 서버 연결 클라이언트들
        self.control_client = socketio.Client(reconnection=True, reconnection_attempts=0)
        self.ev_client = socketio.Client(reconnection=True, reconnection_attempts=0)
        self.av2_client = socketio.Client(reconnection=True, reconnection_attempts=0)

        # 서버 연결 시도 스레드 시작
        import threading
        t = threading.Thread(target=self.connect_all_loop)
        t.daemon = True
        t.start()

        # ⭐ EV state 수신
        self.ev_client.on("ev_state", self.handle_ev_state)

        # ⭐ AV2 state 수신 추가
        self.av2_client.on("av2_state", self.handle_av2_state)

        # ⭐ CONTROL → stage_update 수신 추가 (가장 중요)
        self.control_client.on("stage_update", self.handle_stage_update)


    # 반복적으로 서버 연결 시도
    def connect_all_loop(self):
        while True:
            self.try_connect(self.control_client, CONTROL, "[AV1] CONTROL")
            self.try_connect(self.ev_client, EV, "[AV1] EV")
            self.try_connect(self.av2_client, AV2, "[AV1] AV2")
            time.sleep(5)


    def try_connect(self, client, addr, name):
        if not client.connected:
            try:
                client.connect(f"http://{addr}")
                print(f"{name} connected")
            except Exception as e:
                print(f"{name} connection failed: {e}")


    # ⭐ 외부로 AV1 상태 전송
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


    # ⭐ EV 상태 수신
    def handle_ev_state(self, data):
        print("[AV1] Received EV state:", data)


    # ⭐ AV2 상태 수신
    def handle_av2_state(self, data):
        print("[AV1] Received AV2 state:", data)


    # ⭐ CONTROL → stage_update 수신 (가장 핵심)
    def handle_stage_update(self, data):
        stage = data.get("stage")
        if stage is not None:
            print(f"[AV1] Received stage from CONTROL: {stage}")
            self.state.update_stage(stage)  # 내부 state 업데이트
            print(f"[AV1] Updated internal state → {self.state.get()}")
