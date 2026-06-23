from scripts.database.db_config import get_connection

def list_room_appliances(room_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT
        ra.room_appliance_id,
        ra.room_id,
        ra.appliance_id,
        ra.appliance_name,
        ra.quantity,
        ra.custom_power,
        ra.control_method,
        ra.created_at,

        ac.category,
        ac.brand,
        ac.model,
        ac.rated_power,
        ac.source_type,
        ac.source_url,

        COUNT(dic.ir_code_id) AS ir_count,
        SUM(CASE WHEN dic.is_verified = 1 THEN 1 ELSE 0 END) AS ir_verified_count

    FROM room_appliances ra
    LEFT JOIN appliance_catalog ac
        ON ra.appliance_id = ac.appliance_id
    LEFT JOIN device_ir_codes dic
        ON ra.room_appliance_id = dic.room_appliance_id
    WHERE ra.room_id = %s
    GROUP BY
        ra.room_appliance_id,
        ra.room_id,
        ra.appliance_id,
        ra.appliance_name,
        ra.quantity,
        ra.custom_power,
        ra.control_method,
        ra.created_at,
        ac.category,
        ac.brand,
        ac.model,
        ac.rated_power,
        ac.source_type,
        ac.source_url
    ORDER BY ra.created_at DESC
    """

    cursor.execute(sql, (room_id,))
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results