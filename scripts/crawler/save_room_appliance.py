from scripts.database.db_config import get_connection

def save_room_appliance(data: dict) -> int:
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO room_appliances
    (room_id, appliance_id, appliance_name, quantity, custom_power, control_method)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    values = (
        data.get("room_id"),
        data.get("appliance_id"),
        data.get("appliance_name"),
        data.get("quantity", 1),
        data.get("custom_power"),
        data.get("control_method", "none")
    )

    cursor.execute(sql, values)
    conn.commit()

    room_appliance_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return room_appliance_id