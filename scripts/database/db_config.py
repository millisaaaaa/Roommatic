# db_config.py

import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "YOUR_DB_USERNAME"),
    "password": os.getenv("DB_PASSWORD", "YOUR_DB_PASSWORD"),
    "database": os.getenv("DB_NAME", "YOUR_DB_NAME"),
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)