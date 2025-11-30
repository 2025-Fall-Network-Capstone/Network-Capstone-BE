import requests
from config import CONTROL, AV1

class Communication:

    def send_to_control(self, data):
        try:
            requests.post(f"{CONTROL}/av2/data", json=data)
        except:
            pass

    def send_to_av1(self, data):
        try:
            requests.post(f"{AV1}/av2/data", json=data)
        except:
            pass
