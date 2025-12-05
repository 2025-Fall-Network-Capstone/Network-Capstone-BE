# utils/stage_logic.py

from logger import log
from state_manager import state
from communication_ws import comm   # CT 측 CommunicationWS (EV/AV1/AV2 소켓 클라이언트)

def change_stage(stage: int):
    """
    단계 변경 공통 진입점
    - CT 내부 global_stage 업데이트
    - 차량 3대에 stageUpdate 전파
    - 단계별 시나리오(stage1~4) 실행
    """
    log.write(f"[STAGE] → {stage}")

    # 1) CT 내부 상태 업데이트
    state.update_global_stage(stage)

    # 2) EV / AV1 / AV2 에 단계 정보 전파
    #    각 차량 app.py 의 @socketio.on("stage_update") 에서 받는다.
    comm.broadcast("stage_update", {"stage": stage})
    log.write(f"[STAGE] broadcast stage_update to vehicles: {stage}")

    # 3) 단계별 추가 시나리오 실행 (필요시 유지)
    if stage == 1: stage1()
    elif stage == 2: stage2()
    elif stage == 3: stage3()
    elif stage == 4: stage4()


def stage1():
    log.write("[STAGE1] 시작")
    # 기존 control_msg 시나리오가 있다면 그대로 유지
    # 차량 app.py 에 control_msg 핸들러 없으면,
    # CommunicationWS(state) 쪽에서 처리하고 있을 가능성 있음.
    comm.broadcast("control_msg", {"stage": 1, "msg": "stage_1_start"})

def stage2():
    log.write("[STAGE2] 시작")
    comm.emit("AV2", "control_msg", {"from": "AV1", "msg": "좌회전 변경", "stage": 2})
    comm.emit("AV1", "control_msg", {"from": "EV", "msg": "EV 직진", "stage": 2})

def stage3():
    log.write("[STAGE3] 시작")
    ev_state = state.get_vehicle("EV")
    comm.broadcast("control_msg", {"msg": "EV 상태", "ev": ev_state, "stage": 3})

def stage4():
    log.write("[STAGE4] 정상 주행")
    comm.broadcast("control_msg", {"msg": "정상 주행 상태", "stage": 4})
