from flask import Flask

app = Flask(__name__)

# สร้าง route ทดสอบ
@app.route("/")
def home():
    return "Hello, Flask!"

@app.route("/delay")
def delayed_notification():
    return "ครบกำหนดเล้ว เอาของมาคืนด้วยนะครับ"

if __name__ == "__main__":
    app.run(debug=True)