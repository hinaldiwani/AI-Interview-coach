import os
import pymysql
from pymysql.cursors import DictCursor
from .config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

def get_raw_mysql_connection(select_db=True):
    """Establishes raw MySQL connection using PyMySQL."""
    kwargs = {
        "host": DB_HOST,
        "port": DB_PORT,
        "user": DB_USER,
        "password": DB_PASSWORD,
        "charset": "utf8mb4",
        "cursorclass": DictCursor,
        "autocommit": True
    }
    if select_db:
        kwargs["database"] = DB_NAME
    return pymysql.connect(**kwargs)

def init_db():
    """Initializes and tests MySQL connection on backend startup."""
    print("\nAI Interview Coach Backend")
    print("--------------------------")
    print("Connecting to MySQL...")
    print(f"Database: {DB_NAME}")

    try:
        # 1. Test / ensure target database exists on MySQL server
        conn_root = get_raw_mysql_connection(select_db=False)
        with conn_root.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn_root.close()

        # 2. Connect to target database
        conn = get_raw_mysql_connection(select_db=True)
        
        # 3. Execute setup script if tables don't exist
        schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "database_setup.sql")
        if os.path.exists(schema_path):
            with open(schema_path, "r", encoding="utf-8") as f:
                sql_script = f.read()
            statements = [stmt.strip() for stmt in sql_script.split(";") if stmt.strip()]
            with conn.cursor() as cursor:
                for stmt in statements:
                    if stmt.lower().startswith("create database") or stmt.lower().startswith("use") or stmt.lower().startswith("truncate"):
                        continue
                    try:
                        cursor.execute(stmt)
                    except Exception:
                        pass
        conn.close()

        print("MySQL Connected Successfully")
        print("Backend Started Successfully\n")
    except Exception as mysql_err:
        print("MySQL Connection Failed")
        print(f"Please make sure MySQL is running and the credentials in .env are correct ({mysql_err}).\n")

def get_db():
    """Returns a MySQL database connection object."""
    return get_raw_mysql_connection(select_db=True)
