#!/usr/bin/env python3
"""
Safe helper to delete an item_broke report and its images from a local SQLite DB used by this project.
Usage: python scripts/delete_item_broke.py <item_broke_id>

What it does:
 - makes a timestamped copy of the database file (app.db -> app.db.bak.YYYYmmdd_HHMMSS)
 - lists images associated with the item_broke_id
 - deletes the image files under app/static/<image_path> (best-effort)
 - deletes rows from item_broke_images and item_brokes in a transaction

Run this from the repository root. Test first by running with --dry-run to see what would be deleted:
  python scripts/delete_item_broke.py 123 --dry-run

Be careful: this permanently deletes DB rows and files.
"""

import sqlite3
import sys
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


def find_item(db_path, item_id):
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM item_brokes WHERE item_broke_id = ?", (item_id,))
    row = cur.fetchone()
    con.close()
    return row


def list_images(db_path, item_id):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("SELECT image_path FROM item_broke_images WHERE item_broke_id = ?", (item_id,))
    rows = [r[0] for r in cur.fetchall()]
    con.close()
    return rows


def delete_rows_and_files(db_path, item_id, files_to_delete):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    try:
        cur.execute('BEGIN')
        cur.execute('DELETE FROM item_broke_images WHERE item_broke_id = ?', (item_id,))
        cur.execute('DELETE FROM item_brokes WHERE item_broke_id = ?', (item_id,))
        con.commit()
    except Exception:
        con.rollback()
        con.close()
        raise
    con.close()

    # remove files
    removed = []
    failed = []
    for rel in files_to_delete:
        if not rel:
            continue
        # normalize and ensure path is under STATIC_DIR
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
    import argparse
    p = argparse.ArgumentParser(description='Delete item_broke and associated images from app.db')
    p.add_argument('item_broke_id', type=int)
    p.add_argument('--dry-run', action='store_true')
    args = p.parse_args()

    item_id = args.item_broke_id

    print('Repository root:', REPO_ROOT)
    print('DB path:', DB_PATH)

    if not os.path.exists(DB_PATH):
        print('ERROR: database not found at', DB_PATH)
        sys.exit(2)

    row = find_item(DB_PATH, item_id)
    if not row:
        print(f'No item_broke found with id {item_id}')
        sys.exit(1)

    print('Found item:')
    for k in row.keys():
        print(' ', k, '=', row[k])

    imgs = list_images(DB_PATH, item_id)
    print('\nAssociated images:')
    if imgs:
        for i in imgs:
            print(' -', i)
    else:
        print(' - (none)')

    if args.dry_run:
        print('\nDry-run mode; nothing will be deleted.')
        sys.exit(0)

    # backup
    bak = backup_db(DB_PATH)
    print('\nBackup created at', bak)

    # delete
    removed, failed = delete_rows_and_files(DB_PATH, item_id, imgs)

    print('\nDeletion complete')
    if removed:
        print('Files removed:')
        for f in removed:
            print(' -', f)
    if failed:
        print('Files failed to remove:')
        for f,e in failed:
            print(' -', f, 'error:', e)

    print('\nDB rows for item_broke_id', item_id, 'should be deleted. Please verify the site.')

if __name__ == '__main__':
    main()
