# app/blueprints/instructor/instructor.py
from flask import Blueprint, render_template, url_for, request, redirect 
from flask_login import  current_user 
from sqlalchemy import select, func , or_ ,false
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


# app/blueprints/instructor/instructor.py



def _only_my_requests(stmt, employee_id):
    """
    กรองเฉพาะคำขอที่ส่งถึงอาจารย์คนนี้ (ถ้าระบุตัวได้)
    รองรับ 3 เคสตาม schema ที่มีจริงในโปรเจกต์
    """
    if not employee_id:
        return stmt

    # A) ถ้า RentReturn มีฟิลด์ teacher_confirmed (ชี้ไปที่ user.employee_id)
    if hasattr(RentReturn, "teacher_confirmed"):
        return stmt.where(RentReturn.teacher_confirmed == employee_id)

    # B) ถ้ามี subject และ Subject มี instructor_id
    try:
        from app.db.models import Subject
        if hasattr(RentReturn, "subject") and hasattr(Subject, "instructor_id"):
            return stmt.join(Subject, RentReturn.subject)\
                       .where(Subject.instructor_id == employee_id)
    except Exception:
        pass

    # C) ถ้ามี clazz และ Clazz มี teacher_id
    try:
        from app.db.models import Clazz
        if hasattr(RentReturn, "clazz") and hasattr(Clazz, "teacher_id"):
            return stmt.join(Clazz, RentReturn.clazz)\
                       .where(Clazz.teacher_id == employee_id)
    except Exception:
        pass

    return stmt

def _query_requests(statuses: list[str] | None = None, require_confirm: bool | None = None):
    """
    ดึงคำขอ:
      - statuses: รายชื่อสถานะที่ต้องการกรอง (เช่น ["pending"])
      - require_confirm=True  -> กรองเฉพาะอุปกรณ์ที่ Equipment.confirm == 1
        require_confirm=False -> ไม่บังคับ (ดึงทั้งหมด)
        require_confirm=None  -> ไม่แตะเรื่อง confirm เลย
    จะกรองให้เห็นเฉพาะของอาจารย์ปัจจุบันโดยอัตโนมัติ
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

        # กรองตามสถานะ (case-insensitive)
        if statuses:
            norm = [(_STATUS_MAP.get(x, x)).lower() for x in statuses]
            stmt = stmt.join(StatusRent).where(func.lower(StatusRent.name).in_(norm))

        # ✅ กรองเฉพาะรายการของอาจารย์คนนี้
        employee_id = getattr(current_user, "employee_id", None)
        stmt = _only_my_requests(stmt, employee_id)

        # ✅ ถ้าต้องบังคับเฉพาะอุปกรณ์ที่ require confirm
        if require_confirm is True:
            stmt = stmt.join(Equipment).where(Equipment.confirm == 1)
        # ถ้า False หรือ None จะไม่กรองเรื่อง confirm เพิ่มเติม

        rows = s.execute(stmt).unique().scalars().all()

        # ใส่ URL รูปให้ทุกรายการ
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
    # ✅ หน้า Requests = งานที่ต้องอนุมัติ => pending + ต้องยืนยันโดยอาจารย์ (Equipment.confirm==1)
    reqs = _query_requests(["pending"], require_confirm=True)
    images = _images_map_for(reqs)
    return render_template("instructor/requests.html", reqs=reqs, images=images)

@bp.get("/pending")
def pending():
    # ✅ หน้า Pending/History = ทุกสถานะของอาจารย์คนนี้ (ไม่บังคับ confirm)
    reqs = _query_requests(["pending", "approved", "rejected", "returned"], require_confirm=True)
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
# controller ที่รับคำขอยืม (ตัวอย่าง)


@bp.post("/borrow")
def create_borrow():
    # ... รับค่าอื่นๆ มาแล้ว ...
    teacher_empid = request.form.get("teacher_empid")  # เช่น "T001"
    teacher = None
    if teacher_empid:
        teacher = User.query.filter_by(employee_id=teacher_empid, member_type="teacher").first()

    if not teacher:
        # ถ้าไม่เจออาจารย์ → ให้แจ้งเตือนและไม่บันทึก (หรือจะ fallback ก็ได้)
        flash("กรุณาเลือกอาจารย์ผู้อนุมัติให้ถูกต้อง", "error")
        return redirect(url_for("inventory.lend_page"))

    # สร้างคำขอ (ตัวอย่างเรียก service)
    rents = borrow_service.request_borrow(
        student_id=current_user.user_id,
        equipment_id=int(request.form["equipment_id"]),
        qty=int(request.form.get("qty", 1)),
        start_date=..., due_date=..., reason=request.form.get("reason",""),
        instructor_id=teacher.user_id,   # <-- สำคัญ: เก็บ user_id ของอาจารย์ลง teacher_confirmed
    )
    # ...