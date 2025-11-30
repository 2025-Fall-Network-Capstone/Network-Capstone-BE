class StateManager:
    def __init__(self, role):
        self.role = role
        
        self.data = {
            "id": "AV2",
            "speed": 35,              # 초기값
            "lane_change": False,
            "position": [0, 0],
            "direction": "left_turn",
            "stage": 0,
            #"ev_info": None,          # 관제에서 받는 EV 상태
            #"from_ev": None,          # EV → AV2
        }

    # 관제가 stage 업데이트
    def update_stage(self, stage):
        self.data["stage"] = stage
        self.apply_stage_rules(stage)

    # 단계별 동작 정의 (AV2 버전)
    def apply_stage_rules(self, stage):

        if stage == 0:
            self.data["speed"] = 0
            self.data["lane_change"] = False
            self.data["direction"] = "left_turn"

        elif stage == 1:
            self.data["speed"] = 20
            self.data["direction"] = "STRAIGHT"

        elif stage == 2:
            self.data["lane_change"] = True
            self.data["direction"] = "RIGHT"

        elif stage == 3:
            self.data["speed"] = 10

        elif stage == 4:
            self.data["speed"] = 0

    

    def get_data(self):
        return self.data

'''# EV → AV2
    def update_from_ev(self, data):
        self.data["from_ev"] = data


    # 관제에서 EV info 전달
    def update_ev_info(self, ev_info):
        self.data["ev_info"] = ev_info'''