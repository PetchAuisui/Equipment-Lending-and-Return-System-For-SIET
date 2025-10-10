// static/js/notif.js
document.addEventListener("DOMContentLoaded", () => {
  const wrap     = document.querySelector(".notif-wrap");
  const bellBtn  = wrap.querySelector(".btn-bell");
  const notifBox = wrap.querySelector("#notif-box");
  const notifList= wrap.querySelector("#notif-list");
  

  function safePayload(p){ try{ return (typeof p==="string") ? JSON.parse(p) : (p||{});}catch{ return {}; } }
  function styleByTpl(tpl){
    if (tpl==="overdue_notice") return {bg:"#FDECEA", title:"#E74C3C", icon:"ri-error-warning-line",  titleText:"อุปกรณ์เกินกำหนดคืน"};
    if (tpl==="due_very_soon" || tpl==="due_soon_30min")
      return {bg:"#FEF9E7", title:"#F39C12", icon:"ri-alarm-warning-line", titleText:"ครบกำหนดในอีก 30 นาที"};
    return {bg:"#FFF8E1", title:"#E67E22", icon:"ri-time-line", titleText:"อุปกรณ์ใกล้ครบกำหนดคืน"};
  }

  async function loadNotifs(debugAll = false) {
    try {
      const res  = await fetch(`/overdue/get-notifications${debugAll ? '?all=1' : ''}`, { headers: { Accept: "application/json" }});
      const data = await res.json().catch(() => []);
      notifList.innerHTML = "";
      if (!res.ok) {
        const msg = (res.status === 401) ? "กรุณาเข้าสู่ระบบก่อน" : `โหลดแจ้งเตือนไม่สำเร็จ (${res.status})`;
        notifList.innerHTML = `<li style="padding:10px; text-align:center; color:#888;">${msg}</li>`;
        return;
      }
      if (!Array.isArray(data) || data.length === 0) {
        notifList.innerHTML = `<li style="padding:10px; text-align:center; color:#888;">ไม่มีแจ้งเตือน</li>`;
        return;
      }

      const frag = document.createDocumentFragment();
      for (const n of data) {
        const id      = n.id ?? n.notification_id;
        const payload = safePayload(n.payload);
        const s       = styleByTpl(n.template);
        const name    = payload?.equipment_name || `อุปกรณ์ #${payload?.equipment_id ?? '-'}`;
        const due     = payload?.due_date || '-';

        let titleText  = n.title;
        let detailText = n.text;
        if (!titleText || !detailText) {
          if (n.template === "overdue_notice") {
            titleText  = "อุปกรณ์ยังไม่คืน";
            detailText = `คุณมี <b>${name}</b> ค้างคืน (ครบกำหนด ${due}) กรุณาคืนวันถัดไปและชำระค่าปรับ`;
          } else if (n.template === "due_very_soon" || n.template === "due_soon_30min") {
            titleText  = "ครบกำหนดในอีกไม่ถึง 30 นาที";
            detailText = `กรุณารีบนำ <b>${name}</b> มาคืน (กำหนด ${due})`;
          } else {
            titleText  = "อุปกรณ์ใกล้ครบกำหนดคืน";
            detailText = `กรุณานำ <b>${name}</b> มาคืนก่อน 18:00 น. (กำหนด ${due})`;
          }
        }

        const li = document.createElement("li");
        li.id = `notif-${id}`;
        li.style = `padding:12px 14px; border-bottom:1px solid #f0f0f0; background:${s.bg}; position:relative; transition:opacity .2s ease;`;
        li.innerHTML = `
          <button class="close-btn" data-id="${id}"
            style="position:absolute; top:8px; right:10px; background:none; border:none; color:#999; cursor:pointer; font-size:16px;">
            <i class="ri-close-line"></i>
          </button>
          <div style="display:flex; gap:10px;">
            <div style="flex-shrink:0;"><i class="${s.icon}" style="color:${s.title}; font-size:24px;"></i></div>
            <div style="flex:1;">
              <div style="font-weight:bold; color:${s.title}; margin-bottom:4px;">${titleText}</div>
              <div style="font-size:13px; color:#333; line-height:1.4;">${detailText}</div>
              <div style="color:#999; font-size:12px; margin-top:4px;">${n.created_at || ""}</div>
            </div>
          </div>`;
        frag.appendChild(li);
      }
      notifList.appendChild(frag);
    } catch (e) {
      console.error("loadNotifs error:", e);
      notifList.innerHTML = `<li style="padding:10px; color:red;">เกิดข้อผิดพลาดในการโหลดข้อมูล</li>`;
    }
  }

  bellBtn.addEventListener("click", async () => {
    const open = notifBox.style.display !== "block";
    notifBox.style.display = open ? "block" : "none";
    if (open) await loadNotifs(false);
  });

  notifList.addEventListener("click", async (e) => {
    const btn = e.target.closest(".close-btn");
    if (!btn) return;
    const notifId = btn.dataset.id;
    try {
      const res = await fetch(`/overdue/mark-read/${notifId}`, { method: "POST" });
      if (res.ok) {
        const item = document.getElementById(`notif-${notifId}`);
        if (item) {
          item.style.opacity = "0";
          setTimeout(() => {
            item.remove();
            if (!notifList.children.length) {
              notifList.innerHTML = `<li style="padding:10px; text-align:center; color:#888;">ไม่มีแจ้งเตือน</li>`;
            }
          }, 200);
        }
      } else {
        const r = await res.json().catch(()=>({}));
        alert(r.error || "เกิดข้อผิดพลาดในการปิดแจ้งเตือน");
      }
    } catch (err) {
      console.error("❌ close notif error:", err);
    }
  });

  document.addEventListener("click", (e) => {
    if (!wrap.contains(e.target)) notifBox.style.display = "none";
  });
});
