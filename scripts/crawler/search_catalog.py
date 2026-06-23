from scripts.database.db_config import get_connection

def search_appliances_in_catalog(category=None, brand=None, model=None, limit=20):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT appliance_id, category, brand, model, rated_power, source_type, source_url
    FROM appliance_catalog
    WHERE 1=1
    """
    params = []

    if category:
        sql += " AND category = %s"
        params.append(category)

    if brand:
        sql += " AND brand LIKE %s"
        params.append(f"%{brand}%")

    if model:
        sql += " AND model LIKE %s"
        params.append(f"%{model}%")

    sql += " ORDER BY brand, model LIMIT %s"
    params.append(limit)

    cursor.execute(sql, tuple(params))
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results