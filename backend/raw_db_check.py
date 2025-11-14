# raw_db_check.py
# Run: python backend\raw_db_check.py
import sqlite3
import os
DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')
print('DB path:', DB_PATH)
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
try:
    c.execute("PRAGMA table_info('events')")
    print('table_info events:')
    for row in c.fetchall():
        print(row)
    c.execute("SELECT id, typeof(start_time), start_time, typeof(end_time), end_time FROM events LIMIT 5")
    rows = c.fetchall()
    print('sample rows:')
    for r in rows:
        print(r)
except Exception as e:
    print('Error:', e)
finally:
    conn.close()
