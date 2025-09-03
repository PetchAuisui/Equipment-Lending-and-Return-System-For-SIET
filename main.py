from flask import Flask

app = Flask(__name__)

# สร้าง route ทดสอบ
@app.route("/")
def home():
    return "ของผมหายไปไหน"


if __name__ == "__main__":
    app.run(debug=True)