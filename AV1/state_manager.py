
class StateManager:
  def __init__(self, role):
    self.role = role
    self.data = {
      "id": "AV1",
      "speed": 35,
      "lane_change": False,
      "position": [0, 0],
      "direction": "left_turn",
      "stage": 0,
      #"ev_info": None,      # 관제에서 전달받은 EV 상태 저장
      #"from_ev": None,      # EV→AV1 직접 송신 데이터
    }
  
  def update_stage(self, stage):
        self.data["stage"] = stage
        self.apply_stage_rules(stage)
  
  def apply_stage_rules(self, stage):

        if stage == 0:
            self.data["speed"] = 0
            self.data["lane_change"] = False

        elif stage == 1:
            # 예: 대기 → 출발
            self.data["speed"] = 8
            self.data["direction"] = "STRAIGHT"

        elif stage == 2:
            # 예: 차선 변경 준비
            self.data["lane_change"] = True
            self.data["direction"] = "RIGHT"

        elif stage == 3:
            # 예: EV와 충돌 방지 → 감속
            self.data["speed"] = 4

        elif stage == 4:
            # 예: 완전 정지
            self.data["speed"] = 0


  def get_data(self):
      return self.data
  

  """    # 🔥 EV에서 전달받은 정보 저장
  def update_from_ev(self, data):
      self.data["from_ev"] = data
  
  # 관제에서 받은 EV 상태..?
  def update_ev_info(self, ev_info):
      self.data["ev_info"] = ev_info"""