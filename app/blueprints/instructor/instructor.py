# app/blueprints/instructor/instructor.py
from flask import Blueprint, render_template, url_for, request, redirect
from sqlalchemy import select, func , or_
from sqlalchemy.orm import joinedload

from app.db.db import SessionLocal
from app.db.models import RentReturn, Equipment, User, StatusRent , EquipmentImage

bp = Blueprint("instructor", __name__)

# --- status map ---
_STATUS_MAP = {
    "pending":  "PENDING",
    "approved": "APPROVED",
    "rejected": "REJECTED",
    "returned": "RETURNED",
}
#--- helper functions ---
def _get_or_create_status(s, name: str) -> StatusRent:
    norm = _STATUS_MAP.get(name, name).upper()
    st = s.execute(select(StatusRent).where(func.upper(StatusRent.name) == norm)).scalar_one_or_none()
    if not st:
        st = StatusRent(name=norm, color_code="#888888")
        s.add(st)
        s.commit()
    return st



def _equip_image_url(eq) -> str:
    """คืน URL รูปของอุปกรณ์แบบ robust + fallback."""
    if not eq or not getattr(eq, "image", None):
        return url_for("static", filename="images/device/default.png")
    raw = str(eq.image).replace("\\", "/").lstrip("/")
    # มี static/ มาแล้ว
    if raw.startswith("static/"):
        return "/" + raw
    # กรณีเก็บใต้ static/images/... หรือ static/uploads/...
    if raw.startswith(("images/", "uploads/")):
        return url_for("static", filename=raw)
    # เก็บมาเป็นชื่อไฟล์อย่างเดียว
    return url_for("static", filename=f"images/device/{raw}")

def _query_requests(statuses: list[str] | None = None):
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
            norm = [ _STATUS_MAP.get(x, x).lower() for x in statuses ]
            stmt = stmt.join(StatusRent).where(func.lower(StatusRent.name).in_(norm))

        rows = s.execute(stmt).unique().scalars().all()

        # >>> ใส่ URL รูปให้ทุกชิ้น
        for r in rows:
            if r.equipment:
                r.equipment.image_url = _equip_image_url(r.equipment)

        return rows
    
def _to_static_url(path: str) -> str:
    """รับ path จาก DB แล้วคืน URL ของ static"""
    if not path:
        return url_for("static", filename="images/device/default.png")
    p = str(path).replace("\\", "/").lstrip("/")
    if p.startswith("static/"):
        return "/" + p
    # DB เก็บแบบ images/device/… -> ครอบด้วย static
    return url_for("static", filename=p)

def _images_map_for(reqs: list[RentReturn]) -> dict[int, str]:
    """ดึงรูปแรกของอุปกรณ์ทุกชิ้นใน reqs ทีเดียว แล้วคืน dict {equipment_id: url}"""
    eq_ids = [r.equipment_id for r in reqs if r.equipment_id]
    if not eq_ids:
        return {}
    with SessionLocal() as s:
        rows = s.execute(
            select(EquipmentImage.equipment_id, EquipmentImage.image_path)
            .where(EquipmentImage.equipment_id.in_(eq_ids))
            .order_by(EquipmentImage.created_at.asc())  # รูปแรก
        ).all()

    first_by_eq: dict[int, str] = {}
    for eq_id, img_path in rows:
        if eq_id not in first_by_eq:          # เก็บรูปแรกเท่านั้น
            first_by_eq[eq_id] = _to_static_url(img_path)
    return first_by_eq
#--- routes ---
@bp.get("/home", endpoint="teacher_home")
def home():
    return redirect(url_for("instructor.pending"))

@bp.get("/requests", endpoint="requests_cards")
def requests_cards():
    reqs = _query_requests(["pending"])      # ดึงเฉพาะ PENDING
    images = _images_map_for(reqs)           # {equipment_id: image_url}
    # ↳ ส่งไปที่ 'requests.html' (หน้า list/การ์ด) ไม่ใช่ 'request_detail.html'
    return render_template(
        "instructor/requests.html",
        reqs=reqs,
        images=images
    )

@bp.get("/pending")
def pending():
    reqs = _query_requests(None)  # ทั้งหมดเป็นประวัติ
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

# app/blueprints/instructor/instructor.py

# app/blueprints/instructor/instructor.py

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
                    # ถ้ามีความสัมพันธ์พวก subject/clazz จริง ๆ แต่อิมพอร์ตชื่อโมเดลลำบาก
                    # ใช้วิธี "แตะ" เพื่อให้โหลดเข้าหน่วยความจำก่อนปิด session ก็ได้:
                )
                .where(RentReturn.rent_id == req_id)
            )
            .scalars()
            .first()
        )
        if not r:
            return redirect(url_for("instructor.requests_cards"))

        # ---- เตรียมข้อมูลแสดงผลให้เป็นสตริง ----
        # วิชา (พยายามดึงจาก r.subject ถ้าไม่มีลอง r.clazz.subject)
        try:
            subject_name = None
            if getattr(r, "subject", None) and getattr(r.subject, "name", None):
                subject_name = r.subject.name
            elif getattr(r, "clazz", None) and getattr(r.clazz, "subject", None) and getattr(r.clazz.subject, "name", None):
                subject_name = r.clazz.subject.name
            else:
                subject_name = "-"
        except Exception:
            subject_name = "-"

        # ข้อมูลคลาส/เซกชัน (ถ้ามี)
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

        # รูปอุปกรณ์ (เหมือนเดิม)
        img_path = s.execute(
            select(EquipmentImage.image_path)
            .where(EquipmentImage.equipment_id == r.equipment_id)
            .order_by(EquipmentImage.created_at.asc())
        ).scalar_one_or_none()

    # นอก session แล้ว: แปลง path -> static url
    img_url = _to_static_url(img_path)

    return render_template(
        "instructor/request_detail.html",
        r=r,           # เผื่อจุดอื่นใช้
        req=r,         # กันเทมเพลตบางจุดอ้าง req
        img_url=img_url,
        subject_name=subject_name,
        clazz_info=clazz_info,
        back_to=url_for("instructor.pending")
    )