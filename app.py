from app import create_app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True , use_reloader=False) # ปิด reloader เพื่อไม่ให้รันซ้ำ 2 รอบ 
                                                                        # (debug=True จะเปิด reloader อัตโนมัติ) และทำให้ scheduler รันซ้ำ
                                                                        # เพราะ reloader จะสร้าง process ใหม่อีกอัน 
