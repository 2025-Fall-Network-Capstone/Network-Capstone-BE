# app.py
from flask import Flask
from flask_socketio import SocketIO
from logger import log
from routes.receive import receive_bp
from routes.status import status_bp
from routes.control import control_bp
from config import HOST, PORT, ROLE
from communication_ws import CommunicationWS
from state_manager import state

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# CommunicationWS 인스턴스 생성 및 싱글톤 comm으로 저장
from communication_ws import comm as comm_singleton
comm_singleton = CommunicationWS(socketio)

# 블루프린트 등록
app.register_blueprint(receive_bp)
app.register_blueprint(status_bp)
app.register_blueprint(control_bp)

if __name__ == "__main__":
    print(f"Starting {ROLE} server on port {PORT}")
    socketio.run(app, host=HOST, port=PORT)
