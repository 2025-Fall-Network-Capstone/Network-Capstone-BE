# state.py
"""
ControlTower(CT) 쪽에서 사용하는 상태 래퍼.

내부적으로는 state_manager.py 의 전역 state(StateManager 인스턴스)를 사용하고,
app.py 에서는 ControlState 만 import 해서 쓰도록 정리.
"""

from state_manager import state as global_state


class ControlState:
    def __init__(self):
        # 실제 데이터 저장소는 state_manager.state
        self._state = global_state

    # 차량별 상태 업데이트
    def update_vehicle(self, vid, data: dict):
        self._state.update_vehicle(vid, data)

    # 전체 차량 상태 조회 { "EV": {...}, "AV1": {...}, "AV2": {...} }
    def get_all(self):
        return self._state.get_all()

    # 전역 stage 읽기/쓰기 (state_manager.StateManager 의 global_stage 사용)
    def update_stage(self, stage: int):
        self._state.update_global_stage(stage)

    def get_stage(self) -> int:
        return self._state.get_global_stage()
