# communication_ws.py
import socketio
import threading
import time
from config import CONTROL, EV, AV1, AV2
from logger import log

class CommunicationWS:
    def __init__(self):
        # CT 서버에서 상태를 저장/전송
        self.control_client = socketio.Client(reconnection=True, reconnection_attempts=0)
        self.ev_client = socketio.Client(reconnection=True, reconnection_attempts=0)
        self.av1_client = socketio.Client(reconnection=True, reconnection_attempts=0)
        self.av2_client = socketio.Client(reconnection=True, reconnection_attempts=0)

        # 연결 스레드 시작
        t = threading.Thread(target=self.connect_all_loop)
        t.daemon = True
        t.start()

    def connect_all_loop(self):
        while True:
            self.try_connect(self.control_client, CONTROL, "[CT] CONTROL")
            self.try_connect(self.ev_client, EV, "[CT] EV")
            self.try_connect(self.av1_client, AV1, "[CT] AV1")
            self.try_connect(self.av2_client, AV2, "[CT] AV2")
            time.sleep(5)

    def try_connect(self, client, addr, name):
        if not client.connected:
            try:
                client.connect(f"http://{addr}")
                print(f"{name} connected")
                log.write(f"{name} connected")
            except Exception as e:
                print(f"{name} connection failed: {e}")
                log.write(f"{name} connection failed: {e}")

    # 모든 노드에 broadcast
    def broadcast(self, event, data):
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
            log.write(f"[CT] broadcast error: {e}")

    # 특정 노드에 emit
    def emit(self, target, event, data):
        try:
            if target == "CONTROL" and self.control_client.connected:
                self.control_client.emit(event, data)
            elif target == "EV" and self.ev_client.connected:
                self.ev_client.emit(event, data)
            elif target == "AV1" and self.av1_client.connected:
                self.av1_client.emit(event, data)
            elif target == "AV2" and self.av2_client.connected:
                self.av2_client.emit(event, data)
        except Exception as e:
            print(f"[CT] emit to {target} error: {e}")
            log.write(f"[CT] emit to {target} error: {e}")

# 전역 객체
comm = CommunicationWS()
