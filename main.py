from flask import Flask, request, jsonify
from services.user_service import UserService
from repositories.json_user_repository import JsonUserRepository

app = Flask(__name__)


user_service = UserService(JsonUserRepository())

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    response, status = user_service.register(data)
    return jsonify(response), status

@app.route("/users", methods=["GET"])
def get_users():
    return jsonify(user_service.get_all_users()), 200

if __name__ == "__main__":
    app.run(debug=True)
