# utils/stage_logic.py
from logger import log
from state_manager import state
from communication_ws import comm


def change_stage(stage: int):
    """
    CT의 전역 stage 변경 진입점.
    - CT 내부 global_stage 업데이트
    - EV/AV1/AV2 에 stage_update 전파
    - stage 1~4 에 대해서는 시나리오 함수 호출
    """
    log.write(f"[STAGE] → {stage}")

    # 1) CT 내부 상태
    state.update_global_stage(stage)

    # 2) 차량 3대에 stage 정보 전파
    #    각 차량의 app.py 에서 @socketio.on("stage_update") 로 받는다.
    comm.broadcast("stage_update", {"stage": stage})
    log.write(f"[STAGE] broadcast stage_update to vehicles: {stage}")

    # 3) 단계별 추가 로직
    if stage == 1:
        stage1()
    elif stage == 2:
        stage2()
    elif stage == 3:
        stage3()
    elif stage == 4:
        stage4()
    # stage == 0 (종료) 나 기타 값은 시나리오 없이 상태/브로드캐스트만 수행


def stage1():
    log.write("[STAGE1] 시작")
    # 필요하면 추가 control_msg 유지
    comm.broadcast("control_msg", {"stage": 1, "msg": "stage_1_start"})


def stage2():
    log.write("[STAGE2] 시작")
    # AV1의 좌회전 → AV2에 통보
    comm.emit("AV2", "control_msg", {"from": "AV1", "msg": "좌회전 변경", "stage": 2})
    # EV 직진 → AV1에 통보
    comm.emit("AV1", "control_msg", {"from": "EV", "msg": "EV 직진", "stage": 2})


def stage3():
    log.write("[STAGE3] 시작")
    # EV 한 대만이 아니라 전체 차량 상태를 가져와서 방송
    all_state = state.get_all()
    comm.broadcast(
        "control_msg",
        {
            "msg": "전체 차량 상태",
            "vehicles": all_state,
            "stage": 3,
        },
    )


def stage4():
    log.write("[STAGE4] 정상 주행")
    comm.broadcast("control_msg", {"msg": "정상 주행 상태", "stage": 4})
