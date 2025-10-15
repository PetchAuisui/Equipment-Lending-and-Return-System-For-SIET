# app/blueprints/instructor/instructor.py
from flask import Blueprint, render_template, url_for, request, redirect, session
# ไม่ต้องใช้ current_user แล้ว (ระบบนี้ใช้ session อยู่แล้ว)
# from flask_login import current_user
from sqlalchemy import select, func, or_, false
from sqlalchemy.orm import joinedload, aliased

from app.db.db import SessionLocal
from app.db.models import RentReturn, Equipment, User, StatusRent, EquipmentImage

bp = Blueprint("instructor", __name__)

# --- status map ---
_STATUS_MAP = {
    "pending":  "PENDING",
    "approved": "APPROVED",
    "rejected": "REJECTED",
    "returned": "RETURNED",
}

# --- helpers ---
def _get_or_create_status(s, name: str) -> StatusRent:
    norm = _STATUS_MAP.get(name, name).upper()
    st = s.execute(
        select(StatusRent).where(func.upper(StatusRent.name) == norm)
    ).scalar_one_or_none()
    if not st:
        st = StatusRent(name=norm, color_code="#888888")
        s.add(st)
        s.commit()
    return st


def _equip_image_url(eq) -> str:
    if not eq or not getattr(eq, "image", None):
        return url_for("static", filename="images/device/default.png")
    raw = str(eq.image).replace("\\", "/").lstrip("/")
    if raw.startswith("static/"):
        return "/" + raw
    if raw.startswith(("images/", "uploads/")):
        return url_for("static", filename=raw)
    return url_for("static", filename=f"images/device/{raw}")


def _only_my_requests(stmt):
    """
    แสดงเฉพาะคำขอที่ 'ส่งถึงอาจารย์ที่ล็อกอินอยู่'
    ใช้ session['user_id'] / session['user_email'] (ไม่พึ่ง flask-login)
    map: RentReturn.teacher_confirmed -> users.user_id
    """
    uid = session.get("user_id")            # <-- สำคัญ: user_id จาก session ตอน login
    email = session.get("user_email")

    # กันหลุดข้อมูล: ถ้าไม่รู้ว่าเป็นใคร -> ไม่แสดง
    if not uid and not email:
        return stmt.where(false())

    Teacher = aliased(User)
    stmt = stmt.join(Teacher, RentReturn.teacher_confirmed == Teacher.user_id)

    conditions = []
    if uid:
        try:
            conditions.append(Teacher.user_id == int(uid))
        except Exception:
            pass
    if email:
        conditions.append(Teacher.email == str(email))

    if not conditions:
        return stmt.where(false())

    return stmt.where(or_(*conditions))


def _query_requests(statuses: list[str] | None = None, require_confirm: bool | None = None):
    """
    - statuses: รายชื่อสถานะที่ต้องการกรอง (เช่น ["pending"])
    - require_confirm=True  -> เฉพาะอุปกรณ์ที่ Equipment.confirm == 1
      require_confirm=False/None -> ไม่แตะเรื่อง confirm
    - จะกรองให้เห็นเฉพาะของอาจารย์คนที่ล็อกอินโดยอัตโนมัติ (ผ่าน _only_my_requests)
    """
    with SessionLocal() as s:
        stmt = (
            select(RentReturn)
            .options(
                joinedload(RentReturn.equipment),
                joinedload(RentReturn.user),
                joinedload(RentReturn.status),
            )
            .order_by(RentReturn.created_at.desc())
        )

        if statuses:
            norm = [(_STATUS_MAP.get(x, x)).lower() for x in statuses]
            stmt = stmt.join(StatusRent).where(func.lower(StatusRent.name).in_(norm))

        # ✅ ฟิลเตอร์ให้เหลือเฉพาะคำขอที่ส่งถึงอาจารย์คนนี้
        stmt = _only_my_requests(stmt)

        # ✅ ถ้าต้องบังคับเฉพาะอุปกรณ์ที่ต้องให้อาจารย์อนุมัติ
        if require_confirm is True and hasattr(Equipment, "confirm"):
            stmt = stmt.join(Equipment).where(Equipment.confirm == 1)

        rows = s.execute(stmt).unique().scalars().all()

        # เติม URL รูป
        for r in rows:
            if r.equipment:
                r.equipment.image_url = _equip_image_url(r.equipment)

        return rows


def _to_static_url(path: str) -> str:
    if not path:
        return url_for("static", filename="images/device/default.png")
    p = str(path).replace("\\", "/").lstrip("/")
    if p.startswith("static/"):
        return "/" + p
    return url_for("static", filename=p)


def _images_map_for(reqs: list[RentReturn]) -> dict[int, str]:
    eq_ids = [r.equipment_id for r in reqs if r.equipment_id]
    if not eq_ids:
        return {}
    with SessionLocal() as s:
        rows = s.execute(
            select(EquipmentImage.equipment_id, EquipmentImage.image_path)
            .where(EquipmentImage.equipment_id.in_(eq_ids))
            .order_by(EquipmentImage.created_at.asc())
        ).all()

    first_by_eq: dict[int, str] = {}
    for eq_id, img_path in rows:
        if eq_id not in first_by_eq:
            first_by_eq[eq_id] = _to_static_url(img_path)
    return first_by_eq


# --- routes ---
@bp.get("/home", endpoint="teacher_home")
def home():
    return redirect(url_for("instructor.pending"))


@bp.get("/requests")  # งานที่ต้องอนุมัติ
def requests_cards():
    reqs = _query_requests(["pending"], require_confirm=True)
    images = _images_map_for(reqs)
    return render_template("instructor/requests.html", reqs=reqs, images=images)


@bp.get("/pending")  # ประวัติ/ภาพรวมของอาจารย์คนนี้
def pending():
    reqs = _query_requests(
        ["pending", "approved", "rejected", "returned"],
        require_confirm=None,
    )
    return render_template("instructor/pending.html", reqs=reqs)


@bp.post("/pending/decide/<int:req_id>", endpoint="pending_decide")
def pending_decide(req_id: int):
    action = request.form.get("action", "").strip()
    next_status = "approved" if action == "approve" else "rejected"
    with SessionLocal() as s:
        r = s.get(RentReturn, req_id)
        if not r:
            return redirect(url_for("instructor.requests_cards"))
        st = _get_or_create_status(s, next_status)
        r.status_id = st.status_id
        s.commit()
    return redirect(url_for("instructor.requests_cards"))


@bp.get("/requests/<int:req_id>", endpoint="request_detail")
def request_detail(req_id: int):
    with SessionLocal() as s:
        r = (
            s.execute(
                select(RentReturn)
                .options(
                    joinedload(RentReturn.equipment),
                    joinedload(RentReturn.user),
                    joinedload(RentReturn.status),
                )
                .where(RentReturn.rent_id == req_id)
            )
            .scalars()
            .first()
        )
        if not r:
            return redirect(url_for("instructor.requests_cards"))

        # วิชา
        try:
            if getattr(r, "subject", None) and getattr(r.subject, "name", None):
                subject_name = r.subject.name
            elif getattr(r, "clazz", None) and getattr(r.clazz, "subject", None) and getattr(r.clazz.subject, "name", None):
                subject_name = r.clazz.subject.name
            else:
                subject_name = "-"
        except Exception:
            subject_name = "-"

        # คลาส/เซกชัน
        try:
            clazz_bits = []
            if getattr(r, "clazz", None):
                if getattr(r.clazz, "name", None):
                    clazz_bits.append(r.clazz.name)
                if getattr(r.clazz, "section", None):
                    clazz_bits.append(str(r.clazz.section))
            clazz_info = " ".join(clazz_bits) if clazz_bits else ""
        except Exception:
            clazz_info = ""

        img_path = s.execute(
            select(EquipmentImage.image_path)
            .where(EquipmentImage.equipment_id == r.equipment_id)
            .order_by(EquipmentImage.created_at.asc())
        ).scalar_one_or_none()

    img_url = _to_static_url(img_path)
    return render_template(
        "instructor/request_detail.html",
        r=r,
        req=r,
        img_url=img_url,
        subject_name=subject_name,
        clazz_info=clazz_info,
        back_to=url_for("instructor.pending"),
    )