from functools import wraps
from flask import request, jsonify, current_app
import jwt
from app.infrastructure.database.models import User

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"message": "Token is missing"}), 401
        
        try:
            # Bearer <token>
            token = auth_header.split(" ")[1]

            data = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )

            current_user = User.query.get(data["user_id"])
            if not current_user:
                return jsonify({"message": "Token expired"}), 401
        
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated