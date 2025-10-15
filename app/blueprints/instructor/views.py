# app/blueprints/instructor/views.py
from flask import render_template, request, redirect, url_for, session
from flask.views import MethodView

from app.utils.uow import UnitOfWork
from app.repositories.rent_request_repository import RentRequestRepository
from app.services.instructor_service import InstructorService, ImageResolver



class InstructorRequestsView(MethodView):
    """/instructor/requests – งานที่ต้องอนุมัติ (pending + ต้องยืนยันโดยอาจารย์)"""
    def get(self):
        uid = session.get("user_id")
        email = session.get("user_email")
        with UnitOfWork() as s:
            repo = RentRequestRepository(s)
            svc = InstructorService(repo, s)
            reqs = svc.list_requests(["pending"], True, uid, email)
            images = {r.equipment_id: r.equipment.image_url if r.equipment else "" for r in reqs}
        return render_template("instructor/requests.html", reqs=reqs, images=images)

class InstructorPendingView(MethodView):
    """/instructor/pending – ภาพรวม/ประวัติ ของอาจารย์คนนี้"""
    def get(self):
        uid = session.get("user_id")
        email = session.get("user_email")
        with UnitOfWork() as s:
            repo = RentRequestRepository(s)
            svc = InstructorService(repo, s)
            reqs = svc.list_requests(
                ["pending", "approved", "rejected", "returned"], None, uid, email
            )
        return render_template("instructor/pending.html", reqs=reqs)

class InstructorPendingDecideView(MethodView):
    """/instructor/pending/decide/<req_id> – POST อนุมัติ/ปฏิเสธ"""
    def post(self, req_id: int):
        action = request.form.get("action", "").strip()
        next_status = "approved" if action == "approve" else "rejected"
        with UnitOfWork() as s:
            repo = RentRequestRepository(s)
            svc = InstructorService(repo, s)
            svc.decide(req_id, next_status)
            # commit จาก UoW อัตโนมัติ
        return redirect(url_for("instructor.requests"))

class RequestDetailView(MethodView):
    """/instructor/requests/<req_id> – รายละเอียดคำขอ"""
    def get(self, req_id: int):
        from sqlalchemy import select
        from sqlalchemy.orm import joinedload
        from app.db.models import RentReturn

        with UnitOfWork() as s:
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
                return redirect(url_for("instructor.requests"))

            img_url = ImageResolver.first_image_for_equipment(s, r.equipment_id)

        # (subject_name / clazz_info – ใส่ตามที่คุณมีใน template ได้เลย)
        return render_template(
            "instructor/request_detail.html",
            r=r, req=r,
            img_url=img_url,
            subject_name="-", clazz_info="",
            back_to=url_for("instructor.pending"),
        )