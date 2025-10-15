from sqlalchemy import text
from app.db.db import engine


def ensure_equipment_name_column(backfill: bool = True):
    """Idempotently ensure `equipment_name` exists on item_brokes table.

    If the column is missing the function will ALTER TABLE to add it. If
    backfill=True it will also attempt to populate existing rows by joining
    through rent_returns -> equipments.name.
    """
    try:
        with engine.connect() as conn:
            res = conn.execute(text("PRAGMA table_info('item_brokes')"))
            cols = [row[1] for row in res.fetchall()]
            if 'equipment_name' in cols:
                # Nothing to do
                return False

        # add the column in a transaction
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE item_brokes ADD COLUMN equipment_name TEXT"))

            if backfill:
                # Copy equipment name from joined tables where possible
                # Use a correlated subquery to populate values for rows that have rent_id
                update_sql = text(
                    """
                    UPDATE item_brokes
                    SET equipment_name = (
                        SELECT equipments.name FROM rent_returns
                        JOIN equipments ON rent_returns.equipment_id = equipments.equipment_id
                        WHERE rent_returns.rent_id = item_brokes.rent_id
                        LIMIT 1
                    )
                    WHERE rent_id IS NOT NULL
                    """
                )
                conn.execute(update_sql)

        # ensure contact_phone exists (idempotent)
        with engine.connect() as conn:
            res = conn.execute(text("PRAGMA table_info('item_brokes')"))
            cols = [row[1] for row in res.fetchall()]
        if 'contact_phone' not in cols:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE item_brokes ADD COLUMN contact_phone TEXT"))

        return True
    except Exception:
        # Let caller decide how to react; do not swallow exceptions here
        raise


__all__ = ["ensure_equipment_name_column"]
