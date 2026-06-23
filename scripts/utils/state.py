# /home/pi/Roommatic/scripts/utils/state.py

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime


STATE_FILE = Path("/home/pi/Roommatic/data/runtime_state.json")


def default_state() -> dict:
    return {
        "current_step": 0,
        "occupied_count": 0,
        "vacant_count": 0,
        "light_status": "off",
        "fan_status": "off",
        "ac_status": "off",
        "ac_temp": None,
        "last_people_num": 0,

        # 舊版時間欄位保留，方便你追查
        "last_light_action_time": None,
        "last_fan_action_time": None,
        "last_ac_action_time": None,

        # 新版 decision.py 需要的 step 欄位
        "light_last_action_step": None,
        "fan_last_action_step": None,
        "ac_last_action_step": None,
    }


def load_state() -> dict:
    if not STATE_FILE.exists():
        state = default_state()
        save_state(state)
        return state

    try:
        with STATE_FILE.open("r", encoding="utf-8") as f:
            state = json.load(f)
    except Exception:
        state = default_state()
        save_state(state)
        return state

    # 補齊缺少欄位，避免舊 state.json 壞掉
    defaults = default_state()
    for key, value in defaults.items():
        if key not in state:
            state[key] = value

    return state


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with STATE_FILE.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def update_occupancy_counts(state: dict, people_num: int) -> dict:
    if people_num > 0:
        state["occupied_count"] += 1
        state["vacant_count"] = 0
    else:
        state["vacant_count"] += 1
        state["occupied_count"] = 0

    state["last_people_num"] = people_num
    return state


def mark_action_time(state: dict, device: str) -> dict:
    """
    同時記錄：
    1. 最後動作時間
    2. 最後動作 step
    """
    now_iso = datetime.now().isoformat(timespec="seconds")
    current_step = state.get("current_step", 0)

    if device == "light":
        state["last_light_action_time"] = now_iso
        state["light_last_action_step"] = current_step

    elif device == "fan":
        state["last_fan_action_time"] = now_iso
        state["fan_last_action_step"] = current_step

    elif device == "ac":
        state["last_ac_action_time"] = now_iso
        state["ac_last_action_step"] = current_step

    return state