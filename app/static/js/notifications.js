// 🧠 แปลประเภทแจ้งเตือนเป็นภาษาไทย
function translateTemplate(template) {
  switch (template) {
    case "overdue":
      return "เกินกำหนด";
    case "due_now":
      return "ใกล้ครบกำหนด";
    case "due_tomorrow":
      return "ครบกำหนดวันพรุ่งนี้";
    default:
      return "แจ้งเตือน";
  }
}


// 🔄 โหลดรายการแจ้งเตือน
async function loadNotifications() {
  const res = await fetch("/api/notifications/unread");
  const data = await res.json();

  const bell = document.getElementById("notifBell");
  const count = document.getElementById("notifCount");
  const list = document.getElementById("notifList");

  if (!bell || !count || !list) return;

  // 🧮 badge จำนวนแจ้งเตือน
  if (data.length > 0) {
    count.textContent = data.length;
    count.classList.remove("d-none");
  } else {
    count.classList.add("d-none");
  }

  // 🧾 สร้างรายการแจ้งเตือน
  list.innerHTML = "";
  if (data.length === 0) {
    list.innerHTML = `<div class="empty-msg">ไม่มีการแจ้งเตือนใหม่</div>`;
    return;
  }

  data.forEach((n) => {
    const div = document.createElement("div");
    div.className = "notification-card";
    div.dataset.type = n.template;
    div.innerHTML = `
      <button class="notification-close" onclick="dismissNotification(${n.id})">&times;</button>
      <div class="d-flex align-items-center mb-1">
        <i class="ri-error-warning-fill notification-icon"></i>
        <strong>${translateTemplate(n.template)}</strong>
      </div>
      <p class="mb-1 small text-dark">
        ${n.payload?.equipment_name ? `<strong>${n.payload.equipment_name}</strong><br>` : ""}
        ${n.payload?.message || n.message}
      </p>

      <p class="text-muted small mb-0">${timeAgo(n.created_at)}</p>
    `;
    list.appendChild(div);
  });
}

// ❌ ปิดแจ้งเตือน (mark as read)
async function dismissNotification(id) {
  const card = document.querySelector(
    `.notification-card button[onclick="dismissNotification(${id})"]`
  )?.closest(".notification-card"); // หา card ที่ปุ่มนี้อยู่   

  const count = document.getElementById("notifCount"); // วงกลมแสดงจำนวนแจ้งเตือน
  const list = document.getElementById("notifList"); // รายการแจ้งเตือนทั้งหมด

  if (card) {
    // fade out effect
    card.style.transition = "opacity 0.3s ease";
    card.style.opacity = "0";

    // รอให้ fade จบก่อนลบ
    setTimeout(() => {
      card.remove();        

      const remaining = list.querySelectorAll(".notification-card").length;

      if (remaining > 0) {
        count.textContent = remaining;   // ✅ อัพเดตเลขใหม่
        count.classList.remove("d-none");      // ✅ ไม่ซ่อนวงกลม
        count.style.display = "inline-block"; // ให้โชว์อยู่ตลอด
      } else {
        count.textContent = "0";         // ✅ แสดงเลข 0
        count.classList.remove("d-none"); // ✅ ไม่ซ่อนวงกลม
        count.style.display = "inline-block"; // ให้โชว์อยู่ตลอด
        list.innerHTML = `<div class="empty-msg">ไม่มีการแจ้งเตือนใหม่</div>`;
      }
    }, 300);
  }

  // เรียก API เปลี่ยนสถานะ
  await fetch(`/api/notifications/dismiss/${id}`, { method: "POST" });

} 

// ⏱ แปลงเวลาเป็น "7m ago"
function timeAgo(datetimeStr) {
  const now = new Date();
  const past = new Date(datetimeStr);
  const diff = Math.floor((now - past) / 60000);
  if (diff < 1) return "Just now";
  if (diff < 60) return `${diff}m ago`;
  const hours = Math.floor(diff / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

// 🛎 toggle dropdown
document.addEventListener("DOMContentLoaded", () => {
  const bell = document.getElementById("notifBell");
  const dropdown = document.getElementById("notifDropdown");

  if (!bell || !dropdown) return;

  bell.addEventListener("click", () => {
    dropdown.style.display = (dropdown.style.display === "none" ? "block" : "none");
    loadNotifications();
  });

  // ปิดเมื่อคลิกนอกกรอบ
  document.addEventListener("click", (e) => {
    if (!bell.contains(e.target) && !dropdown.contains(e.target)) {
      dropdown.style.display = "none";
    }
  });

  // โหลดทุก 60 วินาที
  loadNotifications();
  setInterval(loadNotifications, 60000);
});
