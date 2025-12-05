class StateManager:
    def __init__(self, role="AV1"):
        self.role = role
        self.data = {
            "id": "AV1",
            "speed": 45,
            "lane_change": False,
            "position": [0, 0],
            "direction": "straight",
            "stage": 0
        }

    def update_stage(self, stage):
        self.data["stage"] = stage
        self.apply_stage_rules(stage)

    def apply_stage_rules(self, stage):
        if stage == 0:
            self.data["speed"] = 45
            self.data["lane_change"] = False
            self.data["direction"] = "straight"
        elif stage == 1:
            self.data["position"] = [4, 3]
            self.data["speed"] = 45
            self.data["direction"] = "straight"
        elif stage == 2:
            self.data["position"] = [3, 3]
            self.data["lane_change"] = True
            self.data["direction"] = "left_turn"
        elif stage == 3:
            self.data["lane_change"] = False
            self.data["position"] = [3, 3]
            self.data["direction"] = "straight"
        elif stage == 4:
            self.data["lane_change"] = True
            self.data["position"] = [1, 6]
            self.data["direction"] = "right_turn"

    def get(self):
        return self.data

state = StateManager()
