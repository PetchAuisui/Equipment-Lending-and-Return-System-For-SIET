# app/services/image_resolver.py
from flask import url_for
from typing import Optional
from sqlalchemy import select
# ถ้าคอมไพล์ type hints แล้วหา Equipment ไม่เจอ ให้ลบ import นี้ออกได้ ไม่บังคับ
try:
    from app.db.models import Equipment, EquipmentImage
except Exception:
    Equipment = object  # type: ignore
    EquipmentImage = object  # type: ignore


class ImageResolver:
    DEFAULT_PATH = "images/device/default.png"

    @staticmethod
    def to_static_url(path: Optional[str]) -> str:
        """
        แปลง path จาก DB ให้เป็น URL ใต้ /static แบบ robust
        """
        if not path:
            return url_for("static", filename=ImageResolver.DEFAULT_PATH)

        p = str(path).replace("\\", "/").lstrip("/")
        if p.startswith("static/"):
            # กรณี DB เก็บเริ่มต้นด้วย static/ อยู่แล้ว
            return "/" + p
        # กรณี DB เก็บเป็น images/... หรือ uploads/... หรือชื่อไฟล์
        return url_for("static", filename=p)

    @staticmethod
    def equip_image_url(eq) -> str:
        """
        คืน URL รูปของอุปกรณ์:
        - ถ้ามี eq.image -> ใช้เลย
        - ถ้ามีตาราง EquipmentImage -> เอารูปแรก (ถ้าอยากใช้ logic นี้ภายหลัง)
        - ถ้าไม่มี -> default.png
        """
        if not eq:
            return url_for("static", filename=ImageResolver.DEFAULT_PATH)

        # 1) ลองจากฟิลด์หลักบน Equipment ก่อน
        image_attr = getattr(eq, "image", None)
        if image_attr:
            return ImageResolver.to_static_url(image_attr)

        # 2) (ออปชัน) ลองจากความสัมพันธ์ images ถ้ามีโหลดมาด้วย
        try:
            imgs = getattr(eq, "images", None)  # ถ้ามี relationship ตั้งชื่อไว้
            if imgs:
                first_path = getattr(imgs[0], "image_path", None)
                if first_path:
                    return ImageResolver.to_static_url(first_path)
        except Exception:
            pass

        # 3) fallback
        return url_for("static", filename=ImageResolver.DEFAULT_PATH)
    
    @staticmethod
    def first_image_for_equipment(session, equipment_id: int) -> str:
        """ดึงรูปแรกของอุปกรณ์จากตาราง equipment_images แล้วแปลงเป็น static URL"""
        img_path = session.execute(
            select(EquipmentImage.image_path)
            .where(EquipmentImage.equipment_id == equipment_id)
            .order_by(EquipmentImage.created_at.asc())
        ).scalar_one_or_none()
        return ImageResolver.to_static_url(img_path)