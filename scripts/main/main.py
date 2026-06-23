# /home/pi/Roommatic/scripts/main/main.py

from __future__ import annotations

import json
import time
from pathlib import Path
from datetime import datetime

from scripts.comfort.pmv import calculate_pmv_ppd
from scripts.control.decision import decide_all
from scripts.control.actuator import apply_all
from scripts.utils.state import (
    load_state,
    save_state,
    update_occupancy_counts,
    mark_action_time,
)
from scripts.database.save_update import save_update
from scripts.database.save_control_log import save_control_log
from scripts.control.demo_actuator import send_demo_status
from scripts.display.lcd_display import show_roommatic_status, show_startup, show_error

ROOM_ID = 2
INTERVAL_SEC = 600  # 正式版每 10 分鐘跑一次


# =========================================================
# 實體硬體控制設定
# =========================================================
USE_REAL_AC_IR = True      # True = 真的透過 D1 mini 發 IR 控制冷氣
AC_BRAND = "GREE"         # 目前使用 GREE；若之後要 Kelvinator 可改成 "KEL"
DEFAULT_AC_TEMP = 26
USE_DEMO_DISPLAY = False


# =========================================================
# DHT22 讀取：優先讀 D1 mini
# =========================================================
def read_dht_data() -> dict:
    """
    回傳格式:
    {"ta": float, "rh": float}

    目前正式架構:
    DHT22 -> D1 mini -> USB Serial -> Raspberry Pi
    """

    # 1. 正式來源：D1 mini
    try:
        from scripts.sensors.d1mini import read_dht22_processed

        result = read_dht22_processed(samples=10, interval=2.0)
        return {
            "ta": float(result["ta"]),
            "rh": float(result["rh"]),
        }
    except Exception as e:
        print(f"[DHT] D1 mini read failed: {e}")


    # 3. 最後 fallback：讀本地 json
    dht_json = Path("/home/pi/Roommatic/data/dht_latest.json")

    if dht_json.exists():
        try:
            with dht_json.open("r", encoding="utf-8") as f:
                data = json.load(f)

            return {
                "ta": float(data["ta"]),
                "rh": float(data["rh"]),
            }
        except Exception as e:
            print(f"[DHT] dht_latest.json read failed: {e}")

    raise RuntimeError(
        "無法取得 DHT22 資料。請確認 D1 mini 已連接 Raspberry Pi，"
        "且 scripts/sensors/d1mini.py 可正常 read_dht22()。"
    )


# =========================================================
# 人數讀取
# =========================================================
def read_people_count() -> int:
    """
    正式主流程用：
    每次 main.py 執行一輪時，重新啟動 Pi Camera + YOLO 做一次人數辨識，
    避免只讀到上一次手動執行 people_counter.py 留下的 count.json。
    """

    try:
        from scripts.vision.people_counter import run_and_get_people_count  # type: ignore

        people_num = int(run_and_get_people_count())
        print(f"[VISION] fresh YOLO people_count={people_num}")
        return people_num

    except Exception as e:
        print(f"[VISION] fresh YOLO detection failed: {e}")

    # fallback：如果相機或 YOLO 臨時失敗，才讀舊的 count.json
    count_json = Path("/home/pi/Roommatic/scripts/vision/count.json")

    if count_json.exists():
        try:
            with count_json.open("r", encoding="utf-8") as f:
                data = json.load(f)

            if "count" in data:
                return int(data["count"])
            if "people_num" in data:
                return int(data["people_num"])
            if "people_count" in data:
                return int(data["people_count"])

        except Exception as e:
            print(f"[VISION] count.json fallback read failed: {e}")

    raise RuntimeError("無法取得 people count，請確認 people_counter.py、Pi Camera 或 count.json。")


# =========================================================
# 確保新版 decision.py 需要的 state 欄位存在
# =========================================================
def ensure_state_fields(state: dict) -> dict:
    defaults = {
        "current_step": 0,
        "occupied_count": 0,
        "vacant_count": 0,
        "light_status": "off",
        "fan_status": "off",
        "ac_status": "off",
        "ac_temp": None,
        "light_last_action_step": None,
        "fan_last_action_step": None,
        "ac_last_action_step": None,
    }

    for key, value in defaults.items():
        if key not in state:
            state[key] = value

    return state


# =========================================================
# 根據 decision 更新 state
# =========================================================
def update_state_from_decisions(state: dict, decisions: dict) -> dict:
    light_decision = decisions.get("light_decision", {})
    fan_decision = decisions.get("fan_decision", {})
    ac_decision = decisions.get("ac_decision", {})

    light_action = light_decision.get("action")
    fan_action = fan_decision.get("action")
    ac_action = ac_decision.get("action")
    ac_temp = ac_decision.get("temp")

    # ---- light ----
    if light_action == "on":
        state["light_status"] = "on"
        state = mark_action_time(state, "light")

    elif light_action == "off":
        state["light_status"] = "off"
        state = mark_action_time(state, "light")

    # ---- fan ----
    if fan_action == "on":
        state["fan_status"] = "on"
        state = mark_action_time(state, "fan")

    elif fan_action == "off":
        state["fan_status"] = "off"
        state = mark_action_time(state, "fan")

    # ---- ac ----
    if ac_action == "on":
        state["ac_status"] = "on"
        state["ac_temp"] = ac_temp
        state = mark_action_time(state, "ac")

    elif ac_action == "off":
        state["ac_status"] = "off"
        state["ac_temp"] = None
        state = mark_action_time(state, "ac")

    elif ac_action == "set_temp":
        state["ac_temp"] = ac_temp
        state = mark_action_time(state, "ac")

    return state


# =========================================================
# 將 decision 轉成 D1 mini 可接受的 IR 指令
# =========================================================
def build_ac_ir_command(ac_decision: dict, state: dict) -> str | None:
    """
    依照 ac_decision 產生要送給 D1 mini 的指令。

    需要 D1 mini .ino 支援：
    GREE24, GREE25, GREE26, GREE27, GREE28, GREE_OFF
    """

    action = ac_decision.get("action")
    temp = ac_decision.get("temp")

    if action is None or action == "none":
        return None

    brand = AC_BRAND.upper().strip()

    if action == "off":
        if brand == "KEL":
            return "KEL_OFF"
        return "GREE_OFF"

    if action in ("on", "set_temp"):
        if temp is None:
            temp = state.get("ac_temp") or DEFAULT_AC_TEMP

        temp = int(temp)

        if brand == "KEL":
            return f"KEL{temp}"

        return f"GREE{temp}"

    return None


# =========================================================
# 真的透過 D1 mini 發 IR 控制冷氣
# =========================================================
def execute_real_ac_ir(decisions: dict, state: dict) -> str:
    if not USE_REAL_AC_IR:
        return "real AC IR disabled"

    ac_decision = decisions.get("ac_decision", {})
    command = build_ac_ir_command(ac_decision, state)

    if command is None:
        return "no AC IR command needed"

    try:
        from scripts.sensors.d1mini import send_ir_command  # type: ignore

        result = send_ir_command(command)
        return f"{command} -> {result}"

    except Exception as e:
        # 不讓主流程整個死掉，避免 D1 mini 暫時斷線時資料庫也不能存
        return f"{command} -> IR_ERROR: {e}"


# =========================================================
# 單輪執行
# =========================================================
def run_once() -> None:
    show_startup()
    print("\n" + "=" * 60)
    print(f"[MAIN] start cycle @ {datetime.now().isoformat(timespec='seconds')}")

    # 1. 讀感測資料
    dht = read_dht_data()
    ta = float(dht["ta"])
    rh = float(dht["rh"])
    people_num = int(read_people_count())

    print(f"[SENSOR] Ta={ta}, RH={rh}, people_num={people_num}")

    # 2. 算 PMV / PPD
    comfort = calculate_pmv_ppd(ta=ta, rh=rh)
    pmv = comfort["pmv"]
    ppd = comfort["ppd"]

    print(f"[COMFORT] PMV={pmv}, PPD={ppd}%")

    # 3. 讀 state + 補齊欄位 + step + 更新 occupancy
    state = load_state()
    state = ensure_state_fields(state)

    state["current_step"] += 1
    state = update_occupancy_counts(state, people_num)

    print(
        f"[STATE BEFORE] step={state['current_step']}, "
        f"occupied_count={state['occupied_count']}, "
        f"vacant_count={state['vacant_count']}, "
        f"light={state['light_status']}, "
        f"fan={state['fan_status']}, "
        f"ac={state['ac_status']}, "
        f"ac_temp={state['ac_temp']}"
    )

    # 4. 決策
    decisions = decide_all(
        people_num=people_num,
        pmv=pmv,
        ppd=ppd,
        state=state,
    )

    print("[DECISION]")
    print(f"  light: {decisions.get('light_decision')}")
    print(f"  fan:   {decisions.get('fan_decision')}")
    print(f"  ac:    {decisions.get('ac_decision')}")

    # 5. mock actuator 執行：保留原本 light/fan/demo 模擬邏輯
    execution_results = apply_all(decisions)
    print(f"[EXECUTION MOCK] {execution_results}")

    # 5-1. real AC IR 執行：只有冷氣會真的發 IR
    ac_ir_result = execute_real_ac_ir(decisions, state)
    print(f"[EXECUTION REAL AC IR] {ac_ir_result}")

    # 6. 更新 state
    state = update_state_from_decisions(state, decisions)
    save_state(state)

    print(
        f"[STATE AFTER] step={state['current_step']}, "
        f"occupied_count={state['occupied_count']}, "
        f"vacant_count={state['vacant_count']}, "
        f"light={state['light_status']}, "
        f"fan={state['fan_status']}, "
        f"ac={state['ac_status']}, "
        f"ac_temp={state['ac_temp']}"
    )

    # 6-1. 傳送狀態給展場 demo 裝置
    if USE_DEMO_DISPLAY:
        try:
            demo_result = send_demo_status(
                light_status=state["light_status"],
                ac_status=state["ac_status"],
                ac_temp=state["ac_temp"],
            )
        except Exception as e:
            demo_result = f"DEMO_ERROR: {e}"
    else:
        demo_result = "demo display disabled"

    #6-2 更新LCD
    print(f"[DEMO DISPLAY] {demo_result}")
    try:
            show_roommatic_status(
                system_status="ON",
                people_num=people_num,
                pmv=pmv
            )
    except Exception as e:
            print(f"[LCD ERROR] {e}")

    # 7. 存 updates
    save_update(
        room_id=ROOM_ID,
        ta=ta,
        rh=rh,
        people_num=people_num,
        pmv=pmv,
        ppd=ppd,
        light_status=state["light_status"],
        ac_status=state["ac_status"],
        ac_temp=state["ac_temp"],
    )

    # 8. 存 control log
    light_decision = decisions.get("light_decision", {})
    fan_decision = decisions.get("fan_decision", {})
    ac_decision = decisions.get("ac_decision", {})

    light_action = light_decision.get("action")
    fan_action = fan_decision.get("action")
    ac_action = ac_decision.get("action")
    ac_temp = ac_decision.get("temp")

    light_reason = light_decision.get("reason")
    fan_reason = fan_decision.get("reason")
    ac_reason = ac_decision.get("reason")

    note = (
        f"ppd={ppd}; "
        f"light_reason={light_reason}; "
        f"fan_reason={fan_reason}; "
        f"ac_reason={ac_reason}; "
        f"real_ac_ir={ac_ir_result}"
    )

    save_control_log(
        people_num=people_num,
        pmv=pmv,
        light_action=light_action,
        fan_action=fan_action,
        ac_action=ac_action,
        ac_temp=ac_temp,
        execute_mode="mock+real_ac_ir" if USE_REAL_AC_IR else "mock",
        result="simulated+real_ac_ir" if USE_REAL_AC_IR else "simulated",
        note=note,
    )

    print("[MAIN] cycle complete")


# =========================================================
# 持續排程
# =========================================================
def main() -> None:
    print("[MAIN] Roommatic control loop started")
    print(f"[MAIN] interval = {INTERVAL_SEC} sec")
    print(f"[MAIN] real AC IR = {USE_REAL_AC_IR}, brand = {AC_BRAND}")

    while True:
        try:
            start = time.time()
            run_once()
            elapsed = time.time() - start
            sleep_sec = max(1, INTERVAL_SEC - int(elapsed))
            print(f"[MAIN] sleeping {sleep_sec} sec ...")
            time.sleep(sleep_sec)

        except KeyboardInterrupt:
            print("\n[MAIN] stopped by user")
            break

        except Exception as e:
            print(f"[MAIN ERROR] {e}")
            print("[MAIN] wait 10 sec and retry...")
            time.sleep(10)


if __name__ == "__main__":
    main()