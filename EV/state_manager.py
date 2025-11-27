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
        "stage" : 0
        }

    def update_stage(self, stage):
        self.data["stage"] = stage
        self.apply_stage_rules(stage)
    

    # 단계에 맞춰 데이터 변경 필요
    def apply_stage_rules(self, stage):
        if stage == 0:
            self.data["speed"] = 0
            self.data["lane_change"] = False
            self.data["direction"] = "STRAIGHT"

        elif stage == 1:
            self.data["speed"] = 10
            self.data["direction"] = "STRAIGHT"

        elif stage == 2:
            self.data["lane_change"] = True
            self.data["direction"] = "LEFT"

        elif stage == 3:
            self.data["speed"] = 3

        elif stage == 4:
            self.data["speed"] = 0


    def get(self):
        return self.data
    
state = StateManager("EV")
