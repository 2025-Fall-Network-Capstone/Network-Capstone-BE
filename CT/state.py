# state.py
from state_manager import state as base_state

class ControlState:
    """
    CT(app.py)에서 사용하는 인터페이스를
    state_manager.py의 전역 state 인스턴스에 연결해 주는 래퍼.
    """

    def __init__(self):
        # 실제 데이터는 state_manager.py 안의 전역 state 에 저장됨
        self._state = base_state

    def update_stage(self, stage: int):
        """
        app.py 에서 쓰는 이름: update_stage
        내부에서는 global_stage 를 업데이트하는 함수로 연결
        """
        self._state.update_global_stage(stage)

    def update_vehicle(self, vid, data: dict):
        """
        app.py 에서 쓰는 이름 그대로 전달
        """
        self._state.update_vehicle(vid, data)

    def get_all(self):
        """
        전체 차량 상태 반환
        """
        return self._state.get_all()
