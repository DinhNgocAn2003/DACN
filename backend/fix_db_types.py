# fix_db_types.py
# Fix datetime columns that are stored as integers (e.g., 0) by setting them to NULL
import sqlite3
import os
DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')
print('DB path:', DB_PATH)
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
try:
    # Show counts before
    c.execute("SELECT COUNT(*) FROM events WHERE typeof(end_time)='integer' OR end_time=0")
    print('bad end_time rows before:', c.fetchone()[0])
    # Update rows
    c.execute("UPDATE events SET end_time=NULL WHERE typeof(end_time)='integer' OR end_time=0")
    conn.commit()
    c.execute("SELECT COUNT(*) FROM events WHERE typeof(end_time)='integer' OR end_time=0")
    print('bad end_time rows after:', c.fetchone()[0])

    # Also ensure start_time and created_at are text or null; optionally fix numeric zeros
    c.execute("SELECT COUNT(*) FROM events WHERE typeof(start_time)='integer' OR typeof(created_at)='integer'")
    print('bad start/created rows before:', c.fetchone()[0])

except Exception as e:
    print('Error:', e)
finally:
    conn.close()
