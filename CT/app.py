# app.py
import eventlet
eventlet.monkey_patch()  # 최상단에서 패치

from flask import Flask
from flask_socketio import SocketIO
from routes.receive import receive_bp
from routes.control import control_bp
from routes.status import status_bp
from communication_ws import comm
from utils.stage_logic import change_stage
from state_manager import state
from logger import log
from config import HOST, PORT

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# 블루프린트 등록
app.register_blueprint(receive_bp)
app.register_blueprint(control_bp)
app.register_blueprint(status_bp)

# =========================
# 프론트에서 "시작" 버튼 클릭 시
# =========================
@socketio.on("control_start")
def front_start_signal(data):
    log.write("[FRONT] 시작 신호 수신")
    print("[FRONT] 시작 신호 수신")
    
    # 글로벌 stage 0 → 1
    state.update_global_stage(1)
    
    # 단계별 로직 실행
    change_stage(1)
    
    # 모든 연결된 노드(EV, AV1, AV2, 프론트)에 broadcast
    comm.broadcast("stage_update", {"stage": 1})
    socketio.emit("stage_update", {"stage": 1})
    
    log.write("[CT] Stage 1 broadcasted")
    print("[CT] Stage 1 broadcasted")

# =========================
# EV / AV1 / AV2에서 상태 수신
# =========================
@socketio.on("vehicle_state")
def handle_vehicle_state(data):
    vid = data.get("id", "UNKNOWN")
    state.update_vehicle(vid, data)  # state_manager.py에 기록
    log.write(f"[{vid}] 상태 수신: {data}")
    print(f"[{vid}] 상태 수신: {data}")
    
    # 필요시 다른 노드나 프론트로 전송
    comm.broadcast("vehicle_update", {"id": vid, "state": state.get_vehicle(vid)})
    socketio.emit("vehicle_update", {"id": vid, "state": state.get_vehicle(vid)})

if __name__ == "__main__":
    print(f"🚀 CT Server running on {HOST}:{PORT}")
    socketio.run(app, host=HOST, port=PORT)
