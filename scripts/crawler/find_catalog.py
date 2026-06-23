from scripts.database.db_config import get_connection

def find_appliance_in_catalog(category: str, brand: str, model: str):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT appliance_id, category, brand, model, rated_power, source_type, source_url
    FROM appliance_catalog
    WHERE category = %s AND brand = %s AND model = %s
    LIMIT 1
    """

    cursor.execute(sql, (category, brand, model))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result