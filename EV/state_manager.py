class StateManager:
    def __init__(self, role):
        self.role = role
        self.data = {
            "id": role,
            "speed": 0,
            "lane_change": False,
            "position": [0, 0],
            "direction": "STRAIGHT",
            "emergency": False,
            "stage": 0
        }

    def update_stage(self, stage):
        self.data["stage"] = stage
        self.apply_stage_rules(stage)

    def apply_stage_rules(self, stage):
        if stage == 0:
            self.data["speed"] = 80
            self.data["lane_change"] = False
            self.data["direction"] = "STRAIGHT"
        elif stage == 1:
            self.data["position"] = [6,6]
            self.data["speed"] = 80
            self.data["direction"] = "STRAIGHT"
            self.data["emergency"] = True
        elif stage == 2:
            self.data["position"] = [4,6]
            self.data["speed"] = 80
            self.data["direction"] = "STRAIGHT"
            self.data["emergency"] = True
        elif stage == 3:
            self.data["position"] = [3,6]
            self.data["speed"] = 80
            self.data["direction"] = "STRAIGHT"
            self.data["emergency"] = True
        elif stage == 4:
            self.data["position"] = [0,6]
            self.data["speed"] = 80
            self.data["direction"] = "STRAIGHT"
            self.data["emergency"] = True

    def get(self):
        return self.data

state = StateManager("EV")
