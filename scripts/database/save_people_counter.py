import mysql.connector
from scripts.database.db_config import DB_CONFIG

def save_people_count(update_time, people_num):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    sql = """
    INSERT INTO updates(update_time, people_num)
    VALUES (%s, %s)
    """
    cursor.execute(sql, (update_time, people_num))

    conn.commit()
    cursor.close()
    conn.close()