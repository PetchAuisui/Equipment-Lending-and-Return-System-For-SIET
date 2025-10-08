from app import create_app
from app.services.overdue_checker import check_overdue_rents

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

@app.route("/run-check")
def run_check():
    check_overdue_rents()
    return "ตรวจสอบการยืมเกินกำหนดเรียบร้อยแล้ว!"