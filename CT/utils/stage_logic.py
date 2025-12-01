# utils/stage_logic.py
from logger import log
from state_manager import state
from communication_ws import comm

def change_stage(stage):
    log.write(f"[STAGE] change_stage → {stage}")
    if stage == 1:
        stage1_behavior()
    elif stage == 2:
        stage2_behavior()
    elif stage == 3:
        stage3_behavior()
    elif stage == 4:
        stage4_behavior()

def stage1_behavior():
    log.write("[STAGE1] 시작")
    comm.send_to("EV", "control_msg", {"msg": "EV approaching", "stage":1})
    comm.send_to("AV1", "control_msg", {"msg": "AV reporting status", "stage":1})
    comm.send_to("AV2", "control_msg", {"msg": "AV reporting status", "stage":1})

def stage2_behavior():
    log.write("[STAGE2] 시작")
    comm.send_to("AV2", "control_msg", {"from":"AV1","msg":"좌회전 경로 변경"})
    comm.send_to("AV1", "control_msg", {"from":"EV","msg":"EV 방향 직진"})

def stage3_behavior():
    log.write("[STAGE3] 시작")
    ev_state = state.get_vehicle("EV")
    comm.send_to("AV1", "control_msg", {"msg":"EV 현재 상태","ev_state":ev_state})
    comm.send_to("AV2", "control_msg", {"msg":"EV 현재 상태","ev_state":ev_state})
    comm.send_to("AV1", "control_msg", {"msg":"EV 반경 벗어남"})
    comm.send_to("AV2", "control_msg", {"msg":"EV 반경 벗어남"})

def stage4_behavior():
    log.write("[STAGE4] 정상 주행 모드")
    for role in ["EV","AV1","AV2"]:
        comm.send_to(role,"control_msg",{"msg":"정상 주행 상태"})
