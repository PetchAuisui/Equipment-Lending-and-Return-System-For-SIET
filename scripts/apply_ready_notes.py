#!/usr/bin/env python3
"""
Append previous-type notes to item_brokes rows that are already marked 'พร้อมใช้งาน'.
Creates a timestamped backup of app.db before modifying.

Usage: python scripts/apply_ready_notes.py
"""
import sqlite3
import os
import shutil
from datetime import datetime

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(REPO_ROOT, 'app.db')


def backup_db(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"DB file not found at {path}")
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    dest = path + f'.bak.{stamp}'
    shutil.copy2(path, dest)
    return dest


def apply_notes(db_path):
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT item_broke_id, type, detail FROM item_brokes WHERE status = 'พร้อมใช้งาน'")
    rows = cur.fetchall()
    changed = []
    for r in rows:
        rid = r['item_broke_id']
        typ = (r['type'] or '').lower()
        orig = r['detail'] or ''
        prev_text = 'เสียหาย' if ('damaged' in typ) or ('เสียหาย' in typ) else 'สูญหาย'
        note = f" (ประเภทเก่า {prev_text})"
        if note.strip() in orig:
            continue
        new_detail = orig + note
        try:
            cur.execute('UPDATE item_brokes SET detail = ? WHERE item_broke_id = ?', (new_detail, rid))
            changed.append((rid, orig, new_detail))
        except Exception as e:
            print('Failed to update', rid, e)
    con.commit()
    con.close()
    return changed


def main():
    print('DB path:', DB_PATH)
    if not os.path.exists(DB_PATH):
        print('DB not found')
        return 2
    bak = backup_db(DB_PATH)
    print('Backup created at', bak)
    changed = apply_notes(DB_PATH)
    print('Rows updated:', len(changed))
    for c in changed:
        print(' - id', c[0])
    print('Done')
    return 0

if __name__ == '__main__':
    exit(main())
