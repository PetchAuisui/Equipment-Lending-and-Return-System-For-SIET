function confirmDelete(userId) {
  if (confirm("คุณแน่ใจหรือไม่ว่าจะลบผู้ใช้นี้?")) {
    fetch(`/admin/users/${userId}/delete`, {
      method: "POST",   // หรือ DELETE ถ้า backend รองรับ
      headers: {
        "X-Requested-With": "XMLHttpRequest"
      }
    })
    .then(res => {
      if (res.ok) {
        alert("ลบผู้ใช้เรียบร้อยแล้ว");
        window.location.reload();
      } else {
        alert("เกิดข้อผิดพลาด ไม่สามารถลบผู้ใช้ได้");
      }
    })
    .catch(() => alert("การเชื่อมต่อผิดพลาด"));
  }
  return false; // ป้องกันไม่ให้ <a> โหลดซ้ำ
}