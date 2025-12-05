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

        # 이벤트 등록
        self.register_event_handlers()

        # 자동 재연결 스레드
        import threading
        t = threading.Thread(target=self.reconnect_loop)
        t.daemon = True
        t.start()


    # ======================================================
    # ⭐ 서버별 이벤트 핸들러 등록
    # ======================================================
    def register_event_handlers(self):
        # CONTROL → EV : stage_update
        self.control_client.on("stage_update", self.handle_stage_update)

        # AV1 → EV : av1_state
        self.av1_client.on("av1_state", self.handle_av1_state)

        # AV2 → EV : av2_state
        self.av2_client.on("av2_state", self.handle_av2_state)


    # ======================================================
    # 자동 재연결 루프
    # ======================================================
    def reconnect_loop(self):
        while True:
            self.safe_connect(self.control_client, CONTROL, "[EV] CONTROL")
            self.safe_connect(self.av1_client, AV1, "[EV] AV1")
            self.safe_connect(self.av2_client, AV2, "[EV] AV2")
            time.sleep(3)


    def safe_connect(self, client, addr, name):
        if not client.connected:
            try:
                client.connect(f"http://{addr}")
                print(f"{name} connected")
            except Exception as e:
                print(f"{name} connect failed:", e)


    # ======================================================
    # EV → 외부 서버에 상태 전송
    # ======================================================
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
            print("[EV] send_state error:", e)


    # ======================================================
    # ⭐ CONTROL → stage_update 수신
    # ======================================================
    def handle_stage_update(self, data):
        stage = data.get("stage")
        if stage is not None:
            print(f"[EV] Received stage from CONTROL: {stage}")
            self.state.update_stage(stage)
            print(f"[EV] Updated internal state:", self.state.get())


    # ======================================================
    # ⭐ AV1 상태 수신
    # ======================================================
    def handle_av1_state(self, data):
        print("[EV] Received av1_state:", data)
        # 내부에 적용할 필요 없음 → app.py에서 프론트로 forward


    # ======================================================
    # ⭐ AV2 상태 수신
    # ======================================================
    def handle_av2_state(self, data):
        print("[EV] Received av2_state:", data)
        # 내부에 적용할 필요 없음 → app.py에서 프론트로 forward
