from __future__ import annotations

from datetime import datetime


# =========================================================
# 可調參數：Occupancy 類
# =========================================================
LIGHT_FAN_OFF_NO_PERSON_COUNT = 2
AC_OFF_NO_PERSON_COUNT = 3
AC_ON_OCCUPIED_COUNT = 2
FAN_ON_OCCUPIED_COUNT = 1


# =========================================================
# 可調參數：Comfort 類
# =========================================================
PMV_FAN_ON = 0.3
PMV_AC_ON = 0.8
PMV_AC_STRONG_HOT = 1.0
PMV_AC_TOO_COLD = -0.3
PMV_COMFORT_LOW = -0.5
PMV_COMFORT_HIGH = 0.3
PPD_DISCOMFORT = 10.0


# =========================================================
# 可調參數：Actuation 類
# =========================================================
AC_DEFAULT_TEMP = 26
AC_SETPOINT_STEP = 1
AC_MIN_SETPOINT = 24
AC_MAX_SETPOINT = 28


# =========================================================
# 可調參數：最小動作間隔（以「輪」為單位）
# 若正式版 10 分鐘一輪：
# 1 = 10 分鐘
# 2 = 20 分鐘
# =========================================================
LIGHT_MIN_ACTION_GAP_STEPS = 1
FAN_MIN_ACTION_GAP_STEPS = 1
AC_MIN_ACTION_GAP_STEPS = 2


# =========================================================
# 工具函式
# =========================================================
def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _build_action(action: str | None, reason: str | None = None) -> dict:
    return {
        "action": action,
        "reason": reason,
        "decision_time": _now_iso(),
    }


def _build_ac_action(
    action: str | None,
    temp: int | None = None,
    reason: str | None = None,
) -> dict:
    return {
        "action": action,
        "temp": temp,
        "reason": reason,
        "decision_time": _now_iso(),
    }


def _get_steps_since_last_action(state: dict, device_key: str) -> int:
    """
    預期 state 裡有類似：
    state["light_last_action_step"]
    state["fan_last_action_step"]
    state["ac_last_action_step"]

    以及：
    state["current_step"]

    若還沒實作，也會安全 fallback。
    """
    current_step = state.get("current_step", 0)
    last_step = state.get(f"{device_key}_last_action_step")

    if last_step is None:
        return 999999

    return current_step - last_step


def _can_take_action(state: dict, device_key: str, min_gap_steps: int) -> bool:
    return _get_steps_since_last_action(state, device_key) >= min_gap_steps


def _is_comfort_zone(pmv: float, ppd: float | None = None) -> bool:
    """
    Roommatic 控制用舒適區：
    - PMV 要落在你們設定的控制舒適區
    - 若有 PPD，PPD 也要低於不舒適風險門檻
    """
    pmv_ok = PMV_COMFORT_LOW <= pmv <= PMV_COMFORT_HIGH

    if ppd is None:
        return pmv_ok

    ppd_ok = ppd < PPD_DISCOMFORT
    return pmv_ok and ppd_ok


# =========================================================
# 照明決策
# =========================================================
def decide_light(people_num: int, state: dict) -> dict:
    """
    回傳格式：
    {
        "action": "on" / "off" / None,
        "reason": str | None,
        "decision_time": str,
    }
    """

    if not _can_take_action(state, "light", LIGHT_MIN_ACTION_GAP_STEPS):
        return _build_action(None, "light action blocked by min action gap")

    # 有人且燈關著 -> 開燈
    if people_num > 0 and state["light_status"] == "off":
        return _build_action("on", "people_num > 0 and light is off")

    # 連續無人 -> 關燈
    if (
        state["vacant_count"] >= LIGHT_FAN_OFF_NO_PERSON_COUNT
        and state["light_status"] == "on"
    ):
        return _build_action(
            "off",
            f"vacant_count >= {LIGHT_FAN_OFF_NO_PERSON_COUNT} and light is on",
        )

    return _build_action(None, "no light rule triggered")


# =========================================================
# 風扇決策
# =========================================================
def decide_fan(people_num: int, pmv: float, ppd: float | None, state: dict) -> dict:
    """
    回傳格式：
    {
        "action": "on" / "off" / None,
        "reason": str | None,
        "decision_time": str,
    }

    PMV 判斷冷熱方向，PPD 判斷不舒適比例風險。
    """

    if not _can_take_action(state, "fan", FAN_MIN_ACTION_GAP_STEPS):
        return _build_action(None, "fan action blocked by min action gap")

    # 連續無人 -> 關風扇
    if (
        state["vacant_count"] >= LIGHT_FAN_OFF_NO_PERSON_COUNT
        and state["fan_status"] == "on"
    ):
        return _build_action(
            "off",
            f"vacant_count >= {LIGHT_FAN_OFF_NO_PERSON_COUNT} and fan is on",
        )

    # 有人且偏熱，或 PPD 顯示不舒適風險升高 -> 開風扇
    if (
        state["occupied_count"] >= FAN_ON_OCCUPIED_COUNT
        and (
            pmv > PMV_FAN_ON
            or (pmv > 0 and ppd is not None and ppd >= PPD_DISCOMFORT)
        )
        and state["fan_status"] == "off"
    ):
        return _build_action(
            "on",
            f"occupied_count >= {FAN_ON_OCCUPIED_COUNT} and comfort risk triggered "
            f"(pmv={pmv}, ppd={ppd})",
        )

    # 冷氣未開且回到舒適區 -> 關風扇
    if (
        state["fan_status"] == "on"
        and state["ac_status"] == "off"
        and _is_comfort_zone(pmv, ppd)
    ):
        return _build_action(
            "off",
            f"fan is on, ac is off, and pmv/ppd in comfort zone "
            f"(pmv={pmv}, ppd={ppd})",
        )

    # 冷氣未開且偏冷 -> 關風扇
    if (
        state["fan_status"] == "on"
        and state["ac_status"] == "off"
        and pmv < PMV_COMFORT_LOW
    ):
        return _build_action(
            "off",
            f"fan is on, ac is off, and pmv < {PMV_COMFORT_LOW}",
        )

    return _build_action(None, "no fan rule triggered")


# =========================================================
# 冷氣決策
# =========================================================
def decide_ac(people_num: int, pmv: float, ppd: float | None, state: dict) -> dict:
    """
    回傳格式：
    {
        "action": None / "on" / "off" / "set_temp",
        "temp": None / int,
        "reason": str | None,
        "decision_time": str,
    }

    PMV 判斷冷熱方向，PPD 判斷不舒適比例風險。
    """

    if not _can_take_action(state, "ac", AC_MIN_ACTION_GAP_STEPS):
        return _build_ac_action(None, None, "ac action blocked by min action gap")

    # ===== 無人連續幾次 -> 關冷氣 =====
    if state["ac_status"] == "on" and state["vacant_count"] >= AC_OFF_NO_PERSON_COUNT:
        return _build_ac_action(
            "off",
            None,
            f"vacant_count >= {AC_OFF_NO_PERSON_COUNT} and ac is on",
        )

    # ===== 冷氣目前關閉，判斷是否值得啟動 =====
    if state["ac_status"] == "off":
        if state["occupied_count"] >= AC_ON_OCCUPIED_COUNT and (
            pmv > PMV_AC_ON
            or (pmv > 0.5 and ppd is not None and ppd >= PPD_DISCOMFORT)
        ):
            return _build_ac_action(
                "on",
                AC_DEFAULT_TEMP,
                f"occupied_count >= {AC_ON_OCCUPIED_COUNT} and AC comfort risk triggered "
                f"(pmv={pmv}, ppd={ppd})",
            )

        return _build_ac_action(None, None, "ac is off and on-condition not met")

    # ===== 只要目前無人，就不要再調溫 =====
    if people_num == 0:
        return _build_ac_action(None, None, "people_num == 0, skip temp adjustment")

    # ===== 冷氣目前開啟，且有人，判斷是否要調溫 =====
    current_temp = state["ac_temp"] if state["ac_temp"] is not None else AC_DEFAULT_TEMP

    # 明顯偏熱 -> 降 1 度
    if pmv > PMV_AC_STRONG_HOT and current_temp > AC_MIN_SETPOINT:
        return _build_ac_action(
            "set_temp",
            current_temp - AC_SETPOINT_STEP,
            f"pmv > {PMV_AC_STRONG_HOT}, decrease setpoint by {AC_SETPOINT_STEP}",
        )

    # 偏冷 -> 升 1 度
    if pmv < PMV_AC_TOO_COLD and current_temp < AC_MAX_SETPOINT:
        return _build_ac_action(
            "set_temp",
            current_temp + AC_SETPOINT_STEP,
            f"pmv < {PMV_AC_TOO_COLD}, increase setpoint by {AC_SETPOINT_STEP}",
        )

    return _build_ac_action(None, None, "no ac rule triggered")


# =========================================================
# 一次回傳本輪全部設備決策
# =========================================================
def decide_all(
    people_num: int,
    pmv: float,
    state: dict,
    ppd: float | None = None,
) -> dict:
    return {
        "light_decision": decide_light(people_num, state),
        "fan_decision": decide_fan(people_num, pmv, ppd, state),
        "ac_decision": decide_ac(people_num, pmv, ppd, state),
    }