# state_manager.py
import threading
from datetime import datetime

class StateManager:
    def __init__(self, role="CONTROL"):
        self.role = role
        self.lock = threading.Lock()
        self.vehicles = {
            "EV":  {"id": "EV",  "speed": 0, "lane_change": False, "position": [0,0],
                    "direction": "STRAIGHT", "emergency": False, "stage": 0, "updated_at": None},
            "AV1": {"id": "AV1", "speed": 0, "lane_change": False, "position": [0,0],
                    "direction": "STRAIGHT", "emergency": False, "stage": 0, "updated_at": None},
            "AV2": {"id": "AV2", "speed": 0, "lane_change": False, "position": [0,0],
                    "direction": "STRAIGHT", "emergency": False, "stage": 0, "updated_at": None},
        }
        self.global_stage = 0

    def update_vehicle(self, vid, new_data: dict):
        with self.lock:
            if vid not in self.vehicles:
                self.vehicles[vid] = {
                    "id": vid, "speed": 0, "lane_change": False, "position": [0,0],
                    "direction": "STRAIGHT", "emergency": False, "stage": 0, "updated_at": None
                }

            for k, v in new_data.items():
                self.vehicles[vid][k] = v

            self.vehicles[vid]["updated_at"] = datetime.utcnow().isoformat()

    def get_vehicle(self, vid):
        with self.lock:
            return self.vehicles.get(vid)

    def get_all(self):
        with self.lock:
            return dict(self.vehicles)

    def get_global_stage(self):
        return self.global_stage

    def update_global_stage(self, stage):
        self.global_stage = stage


# 전역 인스턴스
state = StateManager()
