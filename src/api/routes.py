"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
import hashlib
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
import bcrypt
from datetime import datetime, timedelta

api = Blueprint('api', __name__)

# Allow CORS requests to this API
CORS(api)


def hash_password(password: str) -> str:
    encoded_password = password.encode("utf-8")
    hashed_password = bcrypt.hashpw(encoded_password, bcrypt.gensalt())
    return hashed_password.decode("utf-8")


@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():

    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    }

    return jsonify(response_body), 200


@api.route("/signup", methods=["POST"])
def handle_signup():
    response_body = {}
    if not request.method == "POST":
        response_body["error"] = "Method not allowed."
        return response_body, 405

    data = request.get_json(silent=True)
    if not data:
        response_body["error"] = "Invalid or empty JSON"
        return response_body, 400

    required_data = ["email", "password"]
    for field in required_data:
        if field not in data:
            response_body["error"] = {f"The {field} is missing: "}
            return response_body, 400
    user = db.session.scalars(db.select(User).filter(
        User.email.ilike(data["email"]))).first()
    if user:
        response_body["message"] = "This user already exists"
        return response_body, 409
    user = User(
        email=data["email"].lower(),
        password=hash_password(data["password"]),
    )

    db.session.add(user)
    db.session.commit()
    response_body["message"] = "User created successfully!"
    return response_body, 201


@api.route("/login", methods=["POST"])
def handle_login():
    response_body = {}
    if not request.method == "POST":
        response_body["error"] = "Method not allowed."
        return response_body, 405

    data = request.get_json(silent=True)
    if not data:
        response_body["error"] = "Invalid or empty JSON"
        return response_body, 400

    required_data = ["email", "password"]
    for field in required_data:
        if field not in data:
            response_body["error"] = {f"The {field} is missing: "}
            return response_body, 400

    user = db.session.scalars(db.select(User).filter(
        User.email.ilike(data["email"]))).first()
    if not user or not bcrypt.checkpw(data["password"].encode("utf-8"), user.password.encode("utf-8")):
        response_body["error"] = "Invalid email or password"
        return response_body, 401

    access_token = create_access_token(
        identity=str(user.id_user))
    response_body = {
        "message": "Login successful",
        "access_token": access_token,
        "user_id": user.id_user,
        "email": user.email
    }
    return response_body, 200


@api.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    response_body = {}
    if not request.method == "GET":
        response_body["error"] = "Method not allowed."
        return response_body, 405

    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    response_body = {
        "id": user.id_user,
        "email": user.email
    }
    return response_body, 200
