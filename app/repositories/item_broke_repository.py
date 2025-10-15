from app.db.db import SessionLocal, engine
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from app.db.models import ItemBroke, RentReturn, ItemBrokeImage
from sqlalchemy.orm import joinedload
import os
import time
from werkzeug.utils import secure_filename
from flask import current_app
from datetime import datetime


DEFAULT_SELECT_COLS = [
    'item_broke_id', 'rent_id', 'type', 'detail', 'status', 'created_at'
]


class ItemBrokeRepository:
    """Repository for ItemBroke that tolerates older SQLite DBs missing
    recently-added columns (equipment_name, contact_phone).

    Read operations try a normal SQLAlchemy query and fall back to a raw
    SELECT when the DB schema is missing columns (to avoid OperationalError).
    Writes inspect the current table columns and only set values for columns
    that exist.
    """

    def __init__(self):
        self.db = SessionLocal()

    def _table_columns(self):
        with engine.connect() as conn:
            res = conn.execute(text("PRAGMA table_info('item_brokes')"))
            from app.db.db import SessionLocal, engine
            from sqlalchemy import text
            from sqlalchemy.exc import OperationalError
            from app.db.models import ItemBroke, RentReturn, ItemBrokeImage
            from sqlalchemy.orm import joinedload
            import os
            import time
            from werkzeug.utils import secure_filename
            from flask import current_app
            from datetime import datetime


            DEFAULT_SELECT_COLS = [
                'item_broke_id', 'rent_id', 'type', 'detail', 'status', 'created_at'
            ]


            class ItemBrokeRepository:
                """Repository for ItemBroke that tolerates older SQLite DBs missing
                recently-added columns (equipment_name, contact_phone).

                Read operations try a normal SQLAlchemy query and fall back to a raw
                SELECT when the DB schema is missing columns (to avoid OperationalError).
                Writes inspect the current table columns and only set values for columns
                that exist.
                """

                def __init__(self):
                    self.db = SessionLocal()

                def _table_columns(self):
                    with engine.connect() as conn:
                        res = conn.execute(text("PRAGMA table_info('item_brokes')"))
                        return [r[1] for r in res.fetchall()]

                def list_all(self):
                    """Return list of dicts suitable for templates.

                    Tries ORM joinedload path first; on OperationalError (missing columns)
                    falls back to raw SQL + enrichment of related data.
                    """
                    try:
                        q = (
                            self.db.query(ItemBroke)
                            .options(
                                joinedload(ItemBroke.rent_return).joinedload(RentReturn.equipment),
                                joinedload(ItemBroke.item_broke_images),
                            )
                            .order_by(ItemBroke.created_at.desc())
                        )
                        rows = q.all()
                        return [self._row_to_dict(r) for r in rows]
                    except OperationalError:
                        cols = self._table_columns()
                        select_cols = [c for c in DEFAULT_SELECT_COLS if c in cols]
                        if 'equipment_name' in cols:
                            select_cols.append('equipment_name')
                        if 'contact_phone' in cols:
                            select_cols.append('contact_phone')

                        sql = f"SELECT {', '.join(select_cols)} FROM item_brokes ORDER BY created_at DESC"
                        with engine.connect() as conn:
                            res = conn.execute(text(sql))
                            out = []
                            for row in res.fetchall():
                                # SQLAlchemy Row may expose _mapping on modern versions
                                d = dict(row._mapping) if hasattr(row, '_mapping') else dict(row)

                                # enrich equipment info if missing and rent_id is present
                                if not d.get('equipment_name') and d.get('rent_id'):
                                    try:
                                        rr = (
                                            self.db.query(RentReturn)
                                            .options(joinedload(RentReturn.equipment))
                                            .filter(RentReturn.rent_id == d.get('rent_id'))
                                            .first()
                                        )
                                        if rr and getattr(rr, 'equipment', None):
                                            d['equipment_name'] = getattr(rr.equipment, 'name', None)
                                            d['equipment_code'] = getattr(rr.equipment, 'code', None)
                                    except Exception:
                                        pass

                                # load images if possible
                                try:
                                    imgs = self.db.query(ItemBrokeImage).filter(ItemBrokeImage.item_broke_id == d.get('item_broke_id')).all()
                                    d['images'] = [i.image_path for i in imgs]
                                except Exception:
                                    d['images'] = []

                                # coerce created_at to datetime where possible so templates can use strftime
                                if 'created_at' in d and isinstance(d['created_at'], str):
                                    raw = d['created_at']
                                    parsed = None
                                    # try ISO first
                                    try:
                                        parsed = datetime.fromisoformat(raw)
                                    except Exception:
                                        # common SQLite formats
                                        for fmt in ('%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
                                            try:
                                                parsed = datetime.strptime(raw, fmt)
                                                break
                                            except Exception:
                                                continue
                                    d['created_at'] = parsed

                                out.append(d)
                            return out

                def _row_to_dict(self, r):
                    rr = getattr(r, 'rent_return', None)
                    equip = getattr(rr, 'equipment', None) if rr else None
                    images = [img.image_path for img in getattr(r, 'item_broke_images', [])] if getattr(r, 'item_broke_images', None) else []
                    return {
                        'item_broke_id': r.item_broke_id,
                        'rent_id': r.rent_id,
                        'type': r.type,
                        'detail': r.detail,
                        'status': r.status,
                        'created_at': r.created_at,
                        'equipment_name': getattr(r, 'equipment_name', None) or (getattr(equip, 'name', None) if equip else None),
                        'contact_phone': getattr(r, 'contact_phone', None),
                        'equipment_code': getattr(equip, 'code', None) if equip else None,
                        'images': images,
                    }

                def get(self, item_broke_id):
                    return (
                        self.db.query(ItemBroke)
                        .options(joinedload(ItemBroke.rent_return).joinedload(RentReturn.equipment), joinedload(ItemBroke.item_broke_images))
                        .filter(ItemBroke.item_broke_id == item_broke_id)
                        .first()
                    )

                def update_status(self, item_broke_id, new_status):
                    it = self.db.query(ItemBroke).filter(ItemBroke.item_broke_id == item_broke_id).first()
                    if not it:
                        return False
                    it.status = new_status
                    self.db.add(it)
                    self.db.commit()
                    return True

                def create(self, rent_id=None, type='lost', detail='', images=None, equipment_name=None, phone=None):
                    images = images or []
                    cols = self._table_columns()
                    kwargs = {'rent_id': rent_id or 0, 'type': type or 'lost', 'detail': detail or '', 'status': 'pending'}
                    if 'equipment_name' in cols and equipment_name is not None:
                        kwargs['equipment_name'] = equipment_name
                    if 'contact_phone' in cols and phone is not None:
                        kwargs['contact_phone'] = phone

                    it = ItemBroke(**kwargs)
                    self.db.add(it)
                    self.db.commit()
                    self.db.refresh(it)

                    # save uploaded images to static/uploads and create ItemBrokeImage rows
                    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
                    os.makedirs(upload_dir, exist_ok=True)

                    for f in images:
                        # accept Werkzeug FileStorage-like objects
                        if not f or getattr(f, 'filename', '') == '':
                            continue
                        try:
                            fname = secure_filename(f.filename)
                            uniq = f"itembroke_{it.item_broke_id}_{int(time.time())}_{fname}"
                            dest = os.path.join(upload_dir, uniq)
                            f.save(dest)
                            rel = os.path.join('uploads', uniq).replace('\\', '/')
                            img = ItemBrokeImage(item_broke_id=it.item_broke_id, image_path=rel)
                            self.db.add(img)
                        except Exception:
                            # non-fatal: skip problematic images
                            continue

                    self.db.commit()
                    return it.item_broke_id

                def close(self):
                    try:
                        self.db.close()
                    except Exception:
                        pass
        it = ItemBroke(**kwargs)
        self.db.add(it)
        self.db.commit()
        self.db.refresh(it)

        # save uploaded images to static/uploads and create ItemBrokeImage rows
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)

        for f in images:
            # accept Werkzeug FileStorage-like objects
            if not f or getattr(f, 'filename', '') == '':
                continue
            try:
                fname = secure_filename(f.filename)
                uniq = f"itembroke_{it.item_broke_id}_{int(time.time())}_{fname}"
                dest = os.path.join(upload_dir, uniq)
                f.save(dest)
                rel = os.path.join('uploads', uniq).replace('\\', '/')
                img = ItemBrokeImage(item_broke_id=it.item_broke_id, image_path=rel)
                self.db.add(img)
            except Exception:
                # non-fatal: skip problematic images
                continue

        self.db.commit()
        return it.item_broke_id

    def close(self):
        try:
            self.db.close()
        except Exception:
            pass

    def delete(self, item_broke_id: int):
        """Delete an ItemBroke and its associated images (both DB rows and files).

        Returns True if deleted, False if not found or error.
        """
        try:
            it = self.db.query(ItemBroke).filter(ItemBroke.item_broke_id == item_broke_id).first()
            if not it:
                return False

            # collect image paths
            imgs = self.db.query(ItemBrokeImage).filter(ItemBrokeImage.item_broke_id == item_broke_id).all()
            paths = [i.image_path for i in imgs if getattr(i, 'image_path', None)]

            # delete image rows
            for i in imgs:
                try:
                    self.db.delete(i)
                except Exception:
                    continue

            # delete the item_broke row
            try:
                self.db.delete(it)
            except Exception:
                pass

            self.db.commit()

            # remove files from disk (best-effort)
            try:
                upload_dir = os.path.join(current_app.root_path, 'static')
                for p in paths:
                    # path is relative like 'uploads/filename'
                    full = os.path.join(upload_dir, p.replace('/', os.sep))
                    if os.path.exists(full):
                        try:
                            os.remove(full)
                        except Exception:
                            continue
            except Exception:
                pass

            return True
        except Exception:
            try:
                self.db.rollback()
            except Exception:
                pass
            return False
"""ItemBroke repository (defensive implementation).

Provides defensive reads so older SQLite databases without new columns
don't cause OperationalError. Writes still use the ORM; startup migrations
should add missing columns but code will tolerate their absence when
reading.
"""

from app.db.db import SessionLocal, engine
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from app.db.models import ItemBroke, RentReturn, ItemBrokeImage
from sqlalchemy.orm import joinedload
import os
import time
from app.db.db import SessionLocal, engine
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from app.db.models import ItemBroke, RentReturn, ItemBrokeImage
from sqlalchemy.orm import joinedload
import os
import time
from werkzeug.utils import secure_filename
from flask import current_app


DEFAULT_SELECT_COLS = [
    'item_broke_id', 'rent_id', 'type', 'detail', 'status', 'created_at'
]


class ItemBrokeRepository:
    """Repository for ItemBroke that tolerates older SQLite DBs missing
    recently-added columns (equipment_name, contact_phone).

    read operations try a normal SQLAlchemy query and fall back to a raw
    SELECT when the DB schema is missing columns (to avoid OperationalError).
    Writes inspect the current table columns and only set values for columns
    that exist.
    """

    def __init__(self):
        self.db = SessionLocal()

    def _table_columns(self):
        with engine.connect() as conn:
            res = conn.execute(text("PRAGMA table_info('item_brokes')"))
            return [r[1] for r in res.fetchall()]

    def list_all(self):
        """Return list of dicts suitable for templates.

        Tries ORM joinedload path first; on OperationalError (missing columns)
        falls back to raw SQL + enrichment of related data.
        """
        try:
            q = (
                self.db.query(ItemBroke)
                .options(
                    joinedload(ItemBroke.rent_return).joinedload(RentReturn.equipment),
                    joinedload(ItemBroke.item_broke_images),
                )
                .order_by(ItemBroke.created_at.desc())
            )
            rows = q.all()
            return [self._row_to_dict(r) for r in rows]
        except OperationalError:
            cols = self._table_columns()
            select_cols = [c for c in DEFAULT_SELECT_COLS if c in cols]
            if 'equipment_name' in cols:
                select_cols.append('equipment_name')
            if 'contact_phone' in cols:
                select_cols.append('contact_phone')

            sql = f"SELECT {', '.join(select_cols)} FROM item_brokes ORDER BY created_at DESC"
            with engine.connect() as conn:
                res = conn.execute(text(sql))
                out = []
                for row in res.fetchall():
                    # SQLAlchemy Row may expose _mapping on modern versions
                    d = dict(row._mapping) if hasattr(row, '_mapping') else dict(row)

                    # enrich equipment info if missing and rent_id is present
                    if not d.get('equipment_name') and d.get('rent_id'):
                        try:
                            rr = (
                                self.db.query(RentReturn)
                                .options(joinedload(RentReturn.equipment))
                                .filter(RentReturn.rent_id == d.get('rent_id'))
                                .first()
                            )
                            if rr and getattr(rr, 'equipment', None):
                                d['equipment_name'] = getattr(rr.equipment, 'name', None)
                                d['equipment_code'] = getattr(rr.equipment, 'code', None)
                        except Exception:
                            pass

                    # load images if possible
                    try:
                        imgs = self.db.query(ItemBrokeImage).filter(ItemBrokeImage.item_broke_id == d.get('item_broke_id')).all()
                        d['images'] = [i.image_path for i in imgs]
                    except Exception:
                        d['images'] = []

                    out.append(d)
                return out

    def _row_to_dict(self, r):
        rr = getattr(r, 'rent_return', None)
        equip = getattr(rr, 'equipment', None) if rr else None
        images = [img.image_path for img in getattr(r, 'item_broke_images', [])] if getattr(r, 'item_broke_images', None) else []
        return {
            'item_broke_id': r.item_broke_id,
            'rent_id': r.rent_id,
            'type': r.type,
            'detail': r.detail,
            'status': r.status,
            'created_at': r.created_at,
            'equipment_name': getattr(r, 'equipment_name', None) or (getattr(equip, 'name', None) if equip else None),
            'contact_phone': getattr(r, 'contact_phone', None),
            'equipment_code': getattr(equip, 'code', None) if equip else None,
            'images': images,
        }

    def get(self, item_broke_id):
        return (
            self.db.query(ItemBroke)
            .options(joinedload(ItemBroke.rent_return).joinedload(RentReturn.equipment), joinedload(ItemBroke.item_broke_images))
            .filter(ItemBroke.item_broke_id == item_broke_id)
            .first()
        )

    def update_status(self, item_broke_id, new_status):
        it = self.db.query(ItemBroke).filter(ItemBroke.item_broke_id == item_broke_id).first()
        if not it:
            return False
        it.status = new_status
        self.db.add(it)
        self.db.commit()
        return True

    def update_type(self, item_broke_id, new_type):
        it = self.db.query(ItemBroke).filter(ItemBroke.item_broke_id == item_broke_id).first()
        if not it:
            return False
        try:
            it.type = new_type
            self.db.add(it)
            self.db.commit()
            return True
        except Exception:
            try:
                self.db.rollback()
            except Exception:
                pass
            return False

    def create(self, rent_id=None, type='lost', detail='', images=None, equipment_name=None, phone=None):
        images = images or []
        cols = self._table_columns()
        kwargs = {'rent_id': rent_id or 0, 'type': type or 'lost', 'detail': detail or '', 'status': 'pending'}
        if 'equipment_name' in cols and equipment_name is not None:
            kwargs['equipment_name'] = equipment_name
        if 'contact_phone' in cols and phone is not None:
            kwargs['contact_phone'] = phone

        it = ItemBroke(**kwargs)
        self.db.add(it)
        self.db.commit()
        self.db.refresh(it)

        # save uploaded images to static/uploads and create ItemBrokeImage rows
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)

        for f in images:
            # accept Werkzeug FileStorage-like objects
            if not f or getattr(f, 'filename', '') == '':
                continue
            try:
                fname = secure_filename(f.filename)
                uniq = f"itembroke_{it.item_broke_id}_{int(time.time())}_{fname}"
                dest = os.path.join(upload_dir, uniq)
                f.save(dest)
                rel = os.path.join('uploads', uniq).replace('\\', '/')
                img = ItemBrokeImage(item_broke_id=it.item_broke_id, image_path=rel)
                self.db.add(img)
            except Exception:
                # non-fatal: skip problematic images
                continue

        self.db.commit()
        return it.item_broke_id

    def close(self):
        try:
            self.db.close()
        except Exception:
            pass

