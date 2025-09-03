from flask import Flask

app = Flask(__name__)

# สร้าง route ทดสอบ
@app.route("/")
def home():
    return "Hello, Flask!"

@app.route("/equipment")
def home():
    return "Hello, My feature Equeipment!"

if __name__ == "__main__":
    app.run(debug=True)