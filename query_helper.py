import sqlite3

def get_db_schema(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    schema = ""
    for (table,) in tables:
        schema += f"\n-- {table}\n"
        columns = cursor.execute(f"PRAGMA table_info({table});").fetchall()
        for col in columns:
            schema += f"{col[1]} {col[2]}\n"
    conn.close()
    return schema

def execute_sql(db_path, query):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        conn.close()
