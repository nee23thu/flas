from flask import Blueprint, jsonify, request
from models import User
import logging

users_bp = Blueprint("users", __name__)
logger = logging.getLogger(__name__)


@users_bp.route("/", methods=["GET"])
def get_users():
    try:
        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 5, type=int)
        search = request.args.get("search", "", type=str)
        sort = request.args.get("sort", "id", type=str)

        sort_field = getattr(User, sort.lstrip("-"), User.id)
        if sort.startswith("-"):
            sort_field = sort_field.desc()

        query = User.query
        if search:
            query = query.filter(
                (User.first_name.ilike(f"%{search}%"))
                | (User.last_name.ilike(f"%{search}%"))
            )

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
