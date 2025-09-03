from flask import Flask

app = Flask(__name__)

# สร้าง route ทดสอบ
@app.route("/")
def home():
    return "Hello, Flask!"

@app.route("/navbar")
def home():
    return "navbar"

if __name__ == "__main__":
    app.run(debug=True)