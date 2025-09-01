from flask import Flask, request, jsonify
from services.user_service import UserService
from services.auth_service import AuthService
from repositories.json_user_repository import JsonUserRepository

app = Flask(__name__)


user_repo = JsonUserRepository()
user_service = UserService(user_repo)
auth_service = AuthService(user_repo)


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    response, status = user_service.register(data)
    return jsonify(response), status


@app.route("/users", methods=["GET"])
def get_users():
    return jsonify(user_service.get_all_users()), 200


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    response, status = auth_service.login(email, password)
    return jsonify(response), status


if __name__ == "__main__":
    app.run(debug=True)
