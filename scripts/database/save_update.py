# /home/pi/Roommatic/scripts/database/save_update.py

from __future__ import annotations
import mysql.connector
from scripts.database.db_config import DB_CONFIG


def save_update(
    room_id: int,
    ta: float,
    rh: float,
    people_num: int,
    pmv: float,
    ppd: float,
    light_status: str,
    ac_status: str,
    ac_temp: float | None,
) -> None:
    conn = None
    cursor = None

    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
        )
        cursor = conn.cursor()

        sql = """
        INSERT INTO updates
        (room_id, update_time, ta, Rh, people_num, PMV, PPD, light_status, con_status, con_temp)
        VALUES
        (%s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            room_id,
            ta,
            rh,
            people_num,
            pmv,
            ppd,
            light_status,
            ac_status,
            ac_temp,
        )

        cursor.execute(sql, values)
        conn.commit()
        print("[DB] updates insert success")

    except mysql.connector.Error as e:
        print(f"[DB ERROR] {e}")

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()