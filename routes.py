from flask import Blueprint, jsonify, request
from database import db
from models import User
from flask_jwt_extended import create_access_token, jwt_required
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging

users_bp = Blueprint("users", __name__)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(get_remote_address, default_limits=["100 per hour"])


# login function to get the access/JWT token
@users_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.json
        email = data.get("email")

        if not data:
            return jsonify({"error": "Invalid credentials"}), 400
        user = User.query.filter_by(email=email).first()
        if user:
            access_token = create_access_token(identity=email)
            return (
                jsonify({"msg": "Login successful", "access_token": access_token}),
                200,
            )
        else:
            return jsonify({"msg": "Bad email"}), 401

    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"error": "Internal server error"}), 500


# Get all users (JWT Required, Rate-Limited, City Filter)
@users_bp.route("/", methods=["GET"])
@jwt_required()
@limiter.limit("5 per minute")
def get_users():
    try:
        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 5, type=int)
        search = request.args.get("search", "", type=str)
        sort = request.args.get("sort", "id", type=str)
        city_filter = request.args.get("city", "").lower()

        sort_field = getattr(User, sort.lstrip("-"), User.id)
        if sort.startswith("-"):
            sort_field = sort_field.desc()

        query = User.query
        if search:
            query = query.filter(
                (User.first_name.ilike(f"%{search}%"))
                | (User.last_name.ilike(f"%{search}%"))
            )
        if city_filter:
            query = query.filter(User.city.ilike(f"%{city_filter}%"))

        users = query.order_by(sort_field).paginate(
            page=page, per_page=limit, error_out=False
        )

        return jsonify(
            {
                "page": page,
                "limit": limit,
                "total_users": users.total,
                "total_pages": users.pages,
                "users": [user.to_dict() for user in users.items],
            }
        )
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        return jsonify({"error": "Internal server error"}), 500


# Create a new user (JWT Required)
@users_bp.route("/", methods=["POST"])
@jwt_required()
def create_user():
    try:
        user_data = request.json
        if "id" not in user_data:
            return jsonify({"error": "ID is required"}), 400

        new_user = User(**user_data)
        db.session.add(new_user)
        db.session.commit()
        return jsonify(new_user.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating user: {e}")
        return jsonify({"error": "Failed to create user"}), 500


# Get user by ID (JWT Required)
@users_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify(user.to_dict()), 200
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        return jsonify({"error": "Internal server error"}), 500


# Fully update user (PUT) - JWT Required
@users_bp.route("/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        for key in ["first_name", "last_name", "email", "age", "city"]:
            if key in data:
                setattr(user, key, data[key])
            else:
                return jsonify({"error": f"Missing required field: {key}"}), 400

        db.session.commit()
        return jsonify({"message": f"User with ID {user_id} updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating user: {e}")
        return jsonify({"error": "Failed to update user"}), 500


# Partially update user (PATCH) - JWT Required
@users_bp.route("/<int:user_id>", methods=["PATCH"])
@jwt_required()
def patch_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        for key, value in data.items():
            if hasattr(user, key):
                setattr(user, key, value)

        db.session.commit()
        return jsonify({"message": f"User with ID {user_id} updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating user: {e}")
        return jsonify({"error": "Failed to update user"}), 500


# Delete a user (JWT Required)
@users_bp.route("/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": f"User with ID {user_id} deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting user: {e}")
        return jsonify({"error": "Failed to delete user"}), 500


# Get summary statistics of users (JWT Required)
@users_bp.route("/summary", methods=["GET"])
@jwt_required()
def get_users_summary():
    try:
        total_users = User.query.count()
        avg_age = db.session.query(db.func.avg(User.age)).scalar()
        city_count = (
            db.session.query(User.city, db.func.count(User.id))
            .group_by(User.city)
            .all()
        )

        summary = {
            "total_users": total_users,
            "average_age": avg_age,
            "count_by_city": {city: count for city, count in city_count},
        }

        return jsonify(summary), 200
    except Exception as e:
        logger.error(f"Error fetching user summary: {e}")
        return jsonify({"error": "Failed to fetch summary"}), 500
