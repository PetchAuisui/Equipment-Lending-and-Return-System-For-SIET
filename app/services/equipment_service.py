# app/services/equipment_service.py
import os, uuid
from typing import Optional, List
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app
from app.db.models import Equipment, EquipmentImage
from app.repositories.equipment_repository import EquipmentRepository

class EquipmentService:
    def __init__(self, repo: Optional[EquipmentRepository] = None):
        self.repo = repo or EquipmentRepository()
        # เลือกชื่อ relationship ของรูปให้ตรงกับ ORM (images หรือ equipment_images)
        self._img_rel = "images" if hasattr(Equipment, "images") else "equipment_images"

    # ---------- List / Get ----------
    def list(self, q: str = "", category: str = ""):
        return self.repo.list(q, category)

    def get(self, equipment_id: int):
        return self.repo.get(equipment_id)

    # ---------- Create ----------
    def create(
        self,
        *,
        name: str,
        code: str,
        category: Optional[str],
        brand: Optional[str],
        detail: Optional[str],
        buy_date,     # date or None (แปลงก่อนส่งเข้ามา)
        status: str,
        confirm: bool,              # ไม่บังคับใช้ หาก schema ไม่มีฟิลด์นี้
        actor_id: Optional[int],
        image_file=None,            # FileStorage | None
    ):
        if not name or not code:
            return False, "กรุณากรอกชื่อและรหัสอุปกรณ์", None

        if self.repo.code_exists(code):
            return False, f"รหัสอุปกรณ์ '{code}' ถูกใช้ไปแล้ว", None

        equipment = Equipment(
            name=name,
            code=code,
            category=category,
            brand=brand,
            detail=detail,
            buy_date=buy_date,
            status=status or "available",
            # ถ้ามีคอลัมน์ confirm ในโมเดลจริง ค่อยเปิดใช้
            # confirm=confirm,
            created_at=datetime.utcnow(),
        )
        self.repo.add_equipment(equipment)

        # ✅ อัปโหลดรูปตั้งแต่ตอนสร้าง
        if image_file and image_file.filename:
            image_rel_path = self._save_image(image_file)
            self.repo.add_image(equipment.equipment_id, image_rel_path)

        # ✅ บันทึก movement
        if actor_id:
            self.repo.add_movement(
                equipment_id=equipment.equipment_id,
                actor_id=actor_id,
                history=f"[ADDED] เพิ่มอุปกรณ์ '{name}' (รหัส: {code})",
            )

        self.repo.commit()
        return True, None, equipment

    # ---------- Update (อัปโหลดภาพใหม่ทับของเดิม) ----------
    def update(
        self,
        equipment_id: int,
        *,
        name: str,
        code: str,
        category: Optional[str],
        brand: Optional[str],
        detail: Optional[str],
        buy_date,
        status: str,
        confirm: bool,              # ไม่บังคับใช้ หาก schema ไม่มีฟิลด์นี้
        image_file=None,
    ):
        eq = self.repo.get(equipment_id)
        if not eq:
            return False, "ไม่พบอุปกรณ์", None

        eq.name = (name or "").strip()
        eq.code = (code or "").strip()
        eq.category = (category or "").strip()
        eq.brand = (brand or "").strip()
        eq.detail = (detail or "").strip()
        eq.status = (status or eq.status or "").strip()
        if buy_date:
            eq.buy_date = buy_date

        # if hasattr(eq, "confirm"):
        #     eq.confirm = bool(confirm)

        # อัปเดตรูป: ลบเก่า เพิ่มใหม่
        if image_file and image_file.filename:
            for im in list(self._images_of(eq)):
                try:
                    old_path = self._abs_image_path(im.image_path)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                except Exception as e:
                    current_app.logger.warning("remove old image failed: %s", e)
                self.repo.delete_image_row(im)

            rel_path = self._save_image(image_file)
            self.repo.add_image(eq.equipment_id, rel_path)

        self.repo.commit()
        return True, None, eq

    # ---------- Soft Delete (ไม่แตะตาราง/ไม่มี is_active) ----------
    def soft_delete(self, equipment_id: int, actor_id: Optional[int]):
        eq = self.repo.get(equipment_id)
        if not eq:
            return False, "ไม่พบอุปกรณ์", None

        # ลบไฟล์รูปจริง + ลบ row image
        for im in list(self._images_of(eq)):
            try:
                abs_path = self._abs_image_path(im.image_path)
                if os.path.exists(abs_path):
                    os.remove(abs_path)
            except Exception as e:
                current_app.logger.warning("delete file failed: %s", e)
            self.repo.delete_image_row(im)

        # บันทึก movement ว่า [DELETED] เพื่อใช้เป็นเงื่อนไขกรอง
        if actor_id:
            self.repo.add_movement(
                equipment_id=eq.equipment_id,
                actor_id=actor_id,
                history=f"[DELETED] อุปกรณ์ '{eq.name}' (รหัส: {eq.code}) ถูกลบออกจากระบบ",
            )

        # ❌ ไม่เรียก repo.soft_delete_equipment / ไม่แตะ is_active
        self.repo.commit()
        return True, None, eq

    # ---------- Helpers ----------
    def _images_of(self, eq) -> List[EquipmentImage]:
        return getattr(eq, self._img_rel, []) or []

    def _save_image(self, image_file) -> str:
        """
        เซฟไฟล์ลง /static/uploads/equipment/<uuid>.<ext>
        และคืน 'uploads/equipment/<file>'
        """
        upload_dir = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_dir, exist_ok=True)
        ext = secure_filename(image_file.filename).rsplit(".", 1)[-1].lower()
        fname = f"{uuid.uuid4().hex}.{ext}"
        abs_path = os.path.join(upload_dir, fname)
        image_file.save(abs_path)
        return f"uploads/equipment/{fname}"

    def _abs_image_path(self, rel_path: str) -> str:
        """
        รับ 'uploads/equipment/xxx.png' -> คืน absolute path ใต้ static/
        """
        if rel_path.startswith("uploads/"):
            return os.path.join(current_app.static_folder, rel_path.replace("/", os.sep))
        # fallback กรณีเก่า
        return os.path.join(current_app.config["UPLOAD_FOLDER"], os.path.basename(rel_path))
