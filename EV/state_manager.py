import threading

class StateManager:
    def __init__(self, role):
        self.role = role
        self.lock = threading.Lock()
        self.data = {
            "id": role,
            "speed": 0,
            "lane_change": False,
            "position": [6, 6],
            "direction": "straight",
            "emergency": False,
            "stage": 0
        }

    def update_stage(self, stage):

        if stage is None:
            return
        
        with self.lock:
            self.data["stage"] = stage
            self.apply_stage_rules(stage)

    
    def apply_stage_rules(self, stage):

        # 기본값 초기화
        self.data["speed"] = 0
        self.data["lane_change"] = False
        self.data["direction"] = "straight"
        self.data["position"] = [6, 6]
        self.data["emergency"] = False

        if stage == 0:
            self.data["speed"] = 80
            self.data["lane_change"] = False
            self.data["direction"] = "straight"
        elif stage == 1:
            self.data["position"] = [6,6]
            self.data["speed"] = 80
            self.data["direction"] = "straight"
            self.data["emergency"] = True
        elif stage == 2:
            self.data["position"] = [4,6]
            self.data["speed"] = 80
            self.data["direction"] = "straight"
            self.data["emergency"] = True
        elif stage == 3:
            self.data["position"] = [3,6]
            self.data["speed"] = 80
            self.data["direction"] = "straight"
            self.data["emergency"] = True
        elif stage == 4:
            self.data["position"] = [0,6]
            self.data["speed"] = 80
            self.data["direction"] = "straight"
            self.data["emergency"] = True

    def get(self):
        with self.lock:
            return self.data.copy()

state = StateManager("EV")
