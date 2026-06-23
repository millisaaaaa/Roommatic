# /home/pi/Roommatic/scripts/control/actuator.py

from __future__ import annotations

from datetime import datetime


EXECUTE_MODE = "mock"


def _build_result(
    device: str,
    action: str,
    success: bool = True,
    temp: int | None = None,
    reason: str | None = None,
) -> dict:
    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "device": device,
        "action": action,
        "temp": temp,
        "mode": EXECUTE_MODE,
        "success": success,
        "reason": reason,
        "message": _build_message(device, action, temp, reason),
    }


def _build_message(
    device: str,
    action: str,
    temp: int | None = None,
    reason: str | None = None,
) -> str:
    base = f"[MOCK] {device} -> {action}"

    if device == "light":
        if action == "on":
            base = "[MOCK] Light -> ON"
        elif action == "off":
            base = "[MOCK] Light -> OFF"

    elif device == "fan":
        if action == "on":
            base = "[MOCK] Fan -> ON"
        elif action == "off":
            base = "[MOCK] Fan -> OFF"

    elif device == "ac":
        if action == "on":
            base = f"[MOCK] AC -> ON, set temp = {temp}"
        elif action == "off":
            base = "[MOCK] AC -> OFF"
        elif action == "set_temp":
            base = f"[MOCK] AC -> SET TEMP {temp}"

    if reason:
        return f"{base} | reason: {reason}"
    return base


def apply_light(action: str | None, reason: str | None = None) -> dict | None:
    if action is None:
        return None

    result = _build_result(device="light", action=action, reason=reason)
    print(result["message"])
    return result


def apply_fan(action: str | None, reason: str | None = None) -> dict | None:
    if action is None:
        return None

    result = _build_result(device="fan", action=action, reason=reason)
    print(result["message"])
    return result


def apply_ac(
    action: str | None,
    temp: int | None = None,
    reason: str | None = None,
) -> dict | None:
    if action is None:
        return None

    result = _build_result(device="ac", action=action, temp=temp, reason=reason)
    print(result["message"])
    return result


def apply_all(decisions: dict) -> dict:
    """
    接收新版 decision.py 的輸出，執行 mock 控制並回傳執行結果
    回傳格式：
    {
        "light_result": ...,
        "fan_result": ...,
        "ac_result": ...
    }
    """

    light_decision = decisions.get("light_decision", {})
    fan_decision = decisions.get("fan_decision", {})
    ac_decision = decisions.get("ac_decision", {})

    light_result = apply_light(
        action=light_decision.get("action"),
        reason=light_decision.get("reason"),
    )

    fan_result = apply_fan(
        action=fan_decision.get("action"),
        reason=fan_decision.get("reason"),
    )

    ac_result = apply_ac(
        action=ac_decision.get("action"),
        temp=ac_decision.get("temp"),
        reason=ac_decision.get("reason"),
    )

    return {
        "light_result": light_result,
        "fan_result": fan_result,
        "ac_result": ac_result,
    }