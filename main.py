from flask import Flask

app = Flask(__name__)

# สร้าง route ทดสอบ
@app.route("/")
def home():
    return "Hello, Flask!"

@app.route("/teacher")
def home():
    return "Hello, Project!"


if __name__ == "__main__":
    app.run(debug=True)