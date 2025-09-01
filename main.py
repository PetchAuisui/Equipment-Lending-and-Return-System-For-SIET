from flask import Flask, request, jsonify
from services.user_service import UserService

app = Flask(__name__)

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    response, status = UserService.register(data)
    return jsonify(response), status

if __name__ == "__main__":
    app.run(debug=True)
