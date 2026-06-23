# /home/pi/Roommatic/scripts/database/save_control_log.py

from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime

CONTROL_LOG_FILE = Path("/home/pi/Roommatic/data/control_log.jsonl")


def save_control_log(
    people_num: int,
    pmv: float,
    light_action: str | None,
    fan_action: str | None,
    ac_action: str | None,
    ac_temp: int | None,
    execute_mode: str = "mock",
    result: str = "simulated",
    note: str | None = None,
) -> None:
    """
    將每輪控制決策寫入 JSONL 檔案
    """

    CONTROL_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "people_num": people_num,
        "pmv": pmv,
        "light_action": light_action,
        "fan_action": fan_action,
        "ac_action": ac_action,
        "ac_temp": ac_temp,
        "execute_mode": execute_mode,
        "result": result,
        "note": note,
    }

    with CONTROL_LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")