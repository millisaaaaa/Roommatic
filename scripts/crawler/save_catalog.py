from scripts.database.db_config import get_connection

def save_appliance_to_catalog(data: dict) -> int:
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO appliance_catalog
    (category, brand, model, rated_power, source_type, source_url)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        rated_power = VALUES(rated_power),
        source_type = VALUES(source_type),
        source_url = VALUES(source_url)
    """

    values = (
        data.get("category"),
        data.get("brand"),
        data.get("model"),
        data.get("rated_power"),
        data.get("source_type", "crawler"),
        data.get("source_url")
    )

    cursor.execute(sql, values)
    conn.commit()
    appliance_id = cursor.lastrowid

    cursor.close()
    conn.close()
    return appliance_id