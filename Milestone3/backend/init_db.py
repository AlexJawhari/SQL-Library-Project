"""Initialize database schema from schema.sql"""
from db import get_db

def init_schema():
    conn = get_db()
    try:
        with open('schema.sql', 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        conn.executescript(schema_sql)
        conn.commit()
        print("Database schema created successfully")
    except Exception as e:
        print(f"Error creating schema: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    init_schema()

