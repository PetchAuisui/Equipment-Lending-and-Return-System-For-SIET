#!/usr/bin/env python3
"""
Set type='success' for all item_brokes where status='พร้อมใช้งาน'
Creates a backup of app.db first.
"""
import sqlite3, os, shutil
from datetime import datetime
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(REPO_ROOT, 'app.db')

def backup_db(path):
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    dest = path + f'.bak.{stamp}'
    shutil.copy2(path, dest)
    return dest

if not os.path.exists(DB_PATH):
    print('DB missing',DB_PATH)
    raise SystemExit(2)

bak = backup_db(DB_PATH)
print('Backup at', bak)
con = sqlite3.connect(DB_PATH)
cur = con.cursor()
cur.execute("SELECT item_broke_id, type FROM item_brokes WHERE status='พร้อมใช้งาน'")
rows = cur.fetchall()
print('Found', len(rows), 'rows')
for r in rows:
    print(' -', r)
cur.execute("UPDATE item_brokes SET type='success' WHERE status='พร้อมใช้งาน'")
con.commit()
print('Updated rows')
con.close()
