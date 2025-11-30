# 관제랑 AV2로 데이터 보냄
import requests
from config import CONTROL, AV2

class Communication:
    def send_to_control(self, data):
        try:
            requests.post(f"{CONTROL}/av1/data", json=data)
        except:
            pass

    def send_to_av2(self, data):
        try:
            requests.post(f"{AV2}/av1/data", json=data)
        except:
            pass
