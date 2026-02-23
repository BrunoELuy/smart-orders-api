from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
import jwt, datetime
from app.infrastructure.database.db import db
from app.infrastructure.database.models import User
from flask import current_app

auth_bp = Blueprint("auth", __name__)
bcrypt = Bcrypt()

@auth_bp.record_once
def on_load(state):
    bcrypt.init_app(state.app)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json

    hashed_password = bcrypt.generate_password_hash(
        data["password"]
    ).decode("utf-8")

    user = User(
        name=data["name"],
        email=data["email"],
        password_hash=hashed_password
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json

    user = User.query.filter_by(email=data["email"]).first()

    if not user or not bcrypt.check_password_hash(
        user.password_hash, data["password"]
    ):
        return jsonify({"message": "Invalid credentials"}), 401
    
    token = jwt.encode(
        {
            "user_id": user.id,
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
        },
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )

    return jsonify({"token": token})