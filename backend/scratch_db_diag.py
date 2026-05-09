import sqlite3
import os

db_path = 'data/bookingme.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cur.fetchall()
    print("Tables:", tables)
    for table in tables:
        t_name = table[0]
        try:
            cur.execute(f"SELECT COUNT(*) FROM {t_name}")
            count = cur.fetchone()[0]
            print(f"Table {t_name}: {count} rows")
            if t_name.lower() in ['booking', 'bookings']:
                cur.execute(f"SELECT start_time, end_time FROM {t_name} LIMIT 3")
                print("Sample data:", cur.fetchall())
        except Exception as e:
            print(f"Error reading table {t_name}: {e}")
    conn.close()
else:
    print("DB not found at", os.path.abspath(db_path))
