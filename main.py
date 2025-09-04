from flask import Flask, send_from_directory

app = Flask(__name__)

@app.route('/navbar/<path:filename>')
def navbar_static(filename):
    return send_from_directory('navbar', filename)


@app.route('/')
def home():
    return send_from_directory('home', 'home.html')
# ส่งไฟล์อื่น ๆ ในโฟลเดอร์ home/ เช่น home.css, home.js
@app.route('/home/<path:filename>')
def home_static(filename):
    return send_from_directory('home', filename)

@app.route('/Login')
def Login():
    return send_from_directory('Login', 'Login.html')
# ส่งไฟล์อื่น ๆ ในโฟลเดอร์ login/ เช่น login.css, login.js
@app.route('/Login/<path:filename>')
def Login_static(filename):
    return send_from_directory('Login', filename)

@app.route('/Equipment')
def Equipment():
    return send_from_directory('Equipment', 'Equipment.html')
@app.route('/Equipment/<path:filename>')
def Equipment_static(filename):
    return send_from_directory('Equipment', filename)

@app.route('/Track_status')
def Track_status():
    return send_from_directory('Track_status', 'Track_status.html')
@app.route('/Track_status/<path:filename>')
def Track_status_static(filename):
    return send_from_directory('Track_status', filename)

@app.route('/Policy')
def Policy():
    return send_from_directory('Policy', 'Policy.html')
@app.route('/Policy/<path:filename>')
def Policy_static(filename):
    return send_from_directory('Policy', filename)

@app.route('/About_Us')
def About_Us():
    return send_from_directory('About_Us', 'About_Us.html')
@app.route('/About_Us/<path:filename>')
def About_Us_static(filename):
    return send_from_directory('About_Us', filename)

@app.route('/Register')
def Register():
    return send_from_directory('Register', 'Register.html')
@app.route('/Register/<path:filename>')
def Register_static(filename):
    return send_from_directory('Register', filename)

if __name__ == "__main__":
    app.run(debug=True)
