#!/usr/bin/env python3
"""
Delete all item_brokes with type='lost' and their images from the local app.db.
Creates a timestamped backup (app.db.bak.YYYYmmdd_HHMMSS) before deleting.

Usage: run from repo root:
  python scripts/delete_all_lost.py

This script is destructive. It will delete DB rows and files and does not offer an undo.
"""
import sqlite3
import os
import shutil
from datetime import datetime

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(REPO_ROOT, 'app.db')
STATIC_DIR = os.path.join(REPO_ROOT, 'app', 'static')

def backup_db(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"DB file not found at {path}")
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    dest = path + f'.bak.{stamp}'
    shutil.copy2(path, dest)
    return dest


def collect_lost_reports(db_path):
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT item_broke_id, equipment_name, created_at FROM item_brokes WHERE type='lost'")
    rows = cur.fetchall()
    out = []
    for r in rows:
        rid = r['item_broke_id']
        cur.execute('SELECT image_path FROM item_broke_images WHERE item_broke_id=?', (rid,))
        imgs = [x[0] for x in cur.fetchall()]
        out.append({'id': rid, 'equipment_name': r['equipment_name'], 'created_at': r['created_at'], 'images': imgs})
    con.close()
    return out


def delete_rows_and_files(db_path, report_list):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    try:
        cur.execute('BEGIN')
        ids = [r['id'] for r in report_list]
        if ids:
            q = '(' + ','.join(['?']*len(ids)) + ')'
            cur.execute(f'DELETE FROM item_broke_images WHERE item_broke_id IN {q}', ids)
            cur.execute(f'DELETE FROM item_brokes WHERE item_broke_id IN {q}', ids)
        con.commit()
    except Exception:
        con.rollback()
        con.close()
        raise
    con.close()

    removed = []
    failed = []
    for r in report_list:
        for rel in r['images']:
            if not rel:
                continue
            rel_clean = rel.replace('/', os.sep).lstrip(os.sep)
            full = os.path.join(STATIC_DIR, rel_clean)
            try:
                if os.path.exists(full):
                    os.remove(full)
                    removed.append(full)
            except Exception as e:
                failed.append((full, str(e)))
    return removed, failed


def main():
    print('Repo root:', REPO_ROOT)
    print('DB path:', DB_PATH)
    if not os.path.exists(DB_PATH):
        print('ERROR: database not found at', DB_PATH)
        return 2

    reports = collect_lost_reports(DB_PATH)
    print('Found', len(reports), 'lost reports')
    for r in reports:
        print(' -', r['id'], r['equipment_name'], r['created_at'], 'images=', len(r['images']))

    if not reports:
        print('Nothing to delete.')
        return 0

    # backup
    bak = backup_db(DB_PATH)
    print('Backup created at', bak)

    removed, failed = delete_rows_and_files(DB_PATH, reports)

    print('\nDeletion complete')
    print('Reports deleted:', len(reports))
    print('Files removed:', len(removed))
    if failed:
        print('Files failed to remove:')
        for f,e in failed:
            print(' -', f, 'error:', e)
    print('\nPlease verify the site and static uploads.\n')
    return 0

if __name__ == '__main__':
    exit(main())
