from flask import Flask

app = Flask(__name__)

# สร้าง route ทดสอบ
@app.route("/device")
def home():
    return "ทดสอบ 1 2 3!"

if __name__ == "__main__":
    app.run(debug=True)