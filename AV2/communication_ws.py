import socketio
import time
from config import CONTROL, EV, AV1

class CommunicationWS:
    def __init__(self, state):
        self.state = state

        # 🔗 외부 서버 연결 클라이언트
        self.control_client = socketio.Client(reconnection=True, reconnection_attempts=0)
        self.ev_client = socketio.Client(reconnection=True, reconnection_attempts=0)
        self.av1_client = socketio.Client(reconnection=True, reconnection_attempts=0)

        # 서버 연결 반복 시도
        import threading
        t = threading.Thread(target=self.connect_all_loop)
        t.daemon = True
        t.start()

        # ⭐ EV 이벤트 수신
        self.ev_client.on("ev_state", self.handle_ev_state)

        # ⭐ AV1 이벤트 수신 추가
        self.av1_client.on("av1_state", self.handle_av1_state)

        # ⭐ CONTROL → stage_update 수신 추가 (가장 중요)
        self.control_client.on("stage_update", self.handle_stage_update)


    # ============================================
    # 서버 연결 반복 시도
    # ============================================
    def connect_all_loop(self):
        while True:
            self.try_connect(self.control_client, CONTROL, "[AV2] CONTROL")
            self.try_connect(self.ev_client, EV, "[AV2] EV")
            self.try_connect(self.av1_client, AV1, "[AV2] AV1")
            time.sleep(5)


    def try_connect(self, client, addr, name):
        if not client.connected:
            try:
                client.connect(f"http://{addr}")
                print(f"{name} connected")
            except Exception as e:
                print(f"{name} connection failed: {e}")


    # ============================================
    # AV2 → 외부 서버로 state 전송
    # ============================================
    def send_state(self):
        data = self.state.get()
        try:
            if self.control_client.connected:
                self.control_client.emit("av2_state", data)
            if self.ev_client.connected:
                self.ev_client.emit("av2_state", data)
            if self.av1_client.connected:
                self.av1_client.emit("av2_state", data)
        except Exception as e:
            print(f"[AV2] send_state error: {e}")


    # ============================================
    # EV 상태 수신
    # ============================================
    def handle_ev_state(self, data):
        print("[AV2] Received EV state:", data)


    # ============================================
    # ⭐ AV1 상태 수신
    # ============================================
    def handle_av1_state(self, data):
        print("[AV2] Received AV1 state:", data)


    # ============================================
    # ⭐ CONTROL → stage_update 수신 (핵심)
    # ============================================
    def handle_stage_update(self, data):
        stage = data.get("stage")
        if stage is not None:
            print(f"[AV2] Received stage from CONTROL: {stage}")

            # 내부 state 업데이트
            self.state.update_stage(stage)

            print(f"[AV2] Updated internal state → {self.state.get()}")
