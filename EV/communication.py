import requests
from config import CONTROL, AV1, AV2

class Communication:
    def send_to_control(self, data):
        try:
            requests.post(f"{CONTROL}/ev/data", json=data)
        except:
            pass

    def send_to_av1(self, data):
        try:
            requests.post(f"{AV1}/ev/data", json=data)
        except:
            pass

    def send_to_av2(self, data):
        try:
            requests.post(f"{AV2}/ev/data", json=data)
        except:
            pass
