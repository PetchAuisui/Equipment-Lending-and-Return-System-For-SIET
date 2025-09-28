document.addEventListener("DOMContentLoaded", () => {
  // ปุ่มลบ
  document.querySelectorAll(".btn-delete").forEach(btn => {
    btn.addEventListener("click", e => {
      if (!confirm("คุณแน่ใจหรือไม่ว่าจะลบผู้ใช้นี้?")) {
        e.preventDefault();
      }
    });
  });

  // ปุ่ม clear search
  const searchInput = document.querySelector(".searchbar input[type='text']");
  if (searchInput) {
    const clearBtn = document.createElement("button");
    clearBtn.type = "button";
    clearBtn.textContent = "ล้าง";
    clearBtn.className = "btn-clear-search";
    clearBtn.style.marginLeft = "6px";

    clearBtn.addEventListener("click", () => {
      searchInput.value = "";
      searchInput.form.submit();
    });

    searchInput.insertAdjacentElement("afterend", clearBtn);
  }
});
