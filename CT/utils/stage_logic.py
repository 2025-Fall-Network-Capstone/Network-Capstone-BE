# utils/stage_logic.py
from logger import log
from state_manager import state
from communication_ws import comm

def change_stage(stage):
    log.write(f"[STAGE] → {stage}")
    state.update_global_stage(stage)

    if stage == 1: stage1()
    elif stage == 2: stage2()
    elif stage == 3: stage3()
    elif stage == 4: stage4()

def stage1():
    log.write("[STAGE1] 시작")
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
