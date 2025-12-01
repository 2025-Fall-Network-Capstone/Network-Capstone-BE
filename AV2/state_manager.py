class StateManager:
    def __init__(self, role="AV2"):
        self.role = role
        self.data = {
            "id": "AV2",
            "speed": 35,
            "lane_change": False,
            "position": [0, 0],
            "direction": "left_turn",
            "stage": 0
        }

    def update_stage(self, stage):
        self.data["stage"] = stage
        self.apply_stage_rules(stage)

    def apply_stage_rules(self, stage):
        if stage == 0:
            self.data["speed"] = 35
            self.data["lane_change"] = False
            self.data["direction"] = "left_turn"
        elif stage == 1:
            self.data["speed"] = 40
            self.data["direction"] = "straight"
        elif stage == 2:
            self.data["lane_change"] = True
            self.data["direction"] = "right_turn"
        elif stage == 3:
            self.data["speed"] = 20
        elif stage == 4:
            self.data["speed"] = 0

    def get(self):
        return self.data

state = StateManager()
