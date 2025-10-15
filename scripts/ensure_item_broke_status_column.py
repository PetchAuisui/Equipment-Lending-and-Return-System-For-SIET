"""Small helper to ensure item_brokes.status column exists in SQLite DB.
Run this script from project root with the same Python environment used by the app.
"""
import sqlite3
import os

DB = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.db')
if not os.path.exists(DB):
    print('Database file not found:', DB)
    raise SystemExit(1)

con = sqlite3.connect(DB)
cur = con.cursor()

# check if column exists
cur.execute("PRAGMA table_info(item_brokes);")
cols = [r[1] for r in cur.fetchall()]
if 'status' in cols:
    print('Column status already exists in item_brokes')
else:
    print('Adding column status to item_brokes')
    cur.execute("ALTER TABLE item_brokes ADD COLUMN status TEXT DEFAULT 'pending';")
    con.commit()
    print('Done')

con.close()
