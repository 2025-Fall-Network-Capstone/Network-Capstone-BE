# communication_ws.py
import socketio
import threading
import time
from config import EV, AV1, AV2
from logger import log
from state_manager import state

# 차량 상태 로그 주기 제한 (초)
VEHICLE_LOG_INTERVAL = 5.0
last_vehicle_log_time = {
    "EV": 0.0,
    "AV1": 0.0,
    "AV2": 0.0,
}


class CommunicationWS:
    def __init__(self):
        # CT에서 각 차량으로 붙는 클라이언트 소켓
        self.ev_client = socketio.Client()
        self.av1_client = socketio.Client()
        self.av2_client = socketio.Client()

        # 차량 이벤트 수신 핸들러 등록 (각 차량 서버에서 emit("vehicle_state", {...}) 예상)
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

    # 🔥 차량 상태 수신 (EV / AV1 / AV2 → CT)
    def handle_vehicle_state(self, data):
        vid = data.get("id")
        if not vid:
            return

        # 1) CT 내부 상태 갱신
        state.update_vehicle(vid, data)

        # 2) 로그는 5초마다만 출력
        now = time.time()
        if now - last_vehicle_log_time.get(vid, 0.0) >= VEHICLE_LOG_INTERVAL:
            print(f"[CT] {vid} 상태 수신 (WS): {data}")
            last_vehicle_log_time[vid] = now

        # 3) 다른 차량들에게 전달 (서버 ↔ 서버 통신)
        if vid == "EV":
            self.emit("AV1", "ev_state", data)
            self.emit("AV2", "ev_state", data)
        elif vid == "AV1":
            self.emit("EV", "av1_state", data)
            self.emit("AV2", "av1_state", data)
        elif vid == "AV2":
            self.emit("EV", "av2_state", data)
            self.emit("AV1", "av2_state", data)

    # 차량 3대 전체에 이벤트 브로드캐스트
    def broadcast(self, event, data):
        for name, client in [
            ("EV", self.ev_client),
            ("AV1", self.av1_client),
            ("AV2", self.av2_client),
        ]:
            if client.connected:
                print(f"[CT] SEND {event} TO {name}: {data}")
                client.emit(event, data)
            else:
                print(f"[CT] {name} NOT CONNECTED (skip {event})")

    # 특정 차량(target)에만 이벤트 전송
    def emit(self, target, event, data):
        mapping = {
            "EV": self.ev_client,
            "AV1": self.av1_client,
            "AV2": self.av2_client,
        }
        client = mapping.get(target)
        if client and client.connected:
            print(f"[CT] SEND {event} TO {target}: {data}")
            client.emit(event, data)
        else:
            print(f"[CT] {target} NOT CONNECTED (skip {event})")


comm = CommunicationWS()
