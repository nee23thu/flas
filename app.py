from flask import Flask, jsonify
from models import User
from sql_alchemy import db
from flask import request
from sqlalchemy.exc import IntegrityError


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:Neethu@localhost:5432/user_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/api/users', methods=['GET'])
def get_users():
    #Query Parameters
    page = request.args.get("page", 1, type=int)  # Default page 1
    limit = request.args.get("limit", 5, type=int)  # Default limit 5
    search = request.args.get("search", "", type=str)  # Search query
    sort = request.args.get("sort", "id", type=str)  # Sorting field

    #Sorting Logic
    sort_field = getattr(User, sort.lstrip('-'), User.id)  # Default sorting by ID
    if sort.startswith("-"):
        sort_field = sort_field.desc()

    #Filtering Logic (Case-Insensitive Search)
    query = User.query
    if search:
        query = query.filter(
            (User.first_name.ilike(f"%{search}%")) | (User.last_name.ilike(f"%{search}%"))
        )

    # Pagination
    users = query.order_by(sort_field).paginate(page=page, per_page=limit, error_out=False)

    #Converting Users to JSON
    return jsonify({
        "page": page,
        "limit": limit,
        "total_users": users.total,
        "total_pages": users.pages,
        "users": [user.to_dict() for user in users.items]
    })

@app.route('/api/users', methods=['POST'])
def create_user():
    user_data = request.json  # getting JSON payload from request

    # Ensuring 'id' is not in the request body
    if "id" not in user_data:
        return jsonify({"error":"ID is required"}),400
        
     #Creating a new User instance
    new_user = User(
                id=user_data["id"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                company_name=user_data["company_name"],
                city=user_data["city"],
                state=user_data["state"],
                zip=user_data["zip"],
                email=user_data["email"],
                web=user_data["web"],
                age=user_data["age"]
            )

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify(new_user.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)  # Fetching user by ID
    if user is None:
        return jsonify({"error": f"User with ID {user_id} not found"}), 404

    return jsonify(user.to_dict()), 200  # Returning user details


@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)  # Fetching user by ID
    
    if user is None:
        return jsonify({"error": f"User with ID {user_id} not found"}), 404

    data = request.get_json()  # Getting JSON data from request

    # Updating user attributes if provided in the request
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'email' in data:
        user.email = data['email']
    if 'company_name' in data:
        user.company_name = data['company_name']
    if 'city' in data:
        user.city = data['city']
    if 'state' in data:
        user.state = data['state']
    if 'zip' in data:
        user.zip = data['zip']
    if 'web' in data:
        user.web = data['web']
    if 'age' in data:
        user.age = data['age']

    try:
        db.session.commit()  # Save changes
        return jsonify({"message": f"User with ID {user_id} updated successfully"}), 200
    except Exception as e:
        db.session.rollback()  # Rollback changes if an error occurs
        return jsonify({"error": f"Failed to update user: {str(e)}"}), 500
    

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    
    if user is None:
        return jsonify({"error": f"User with ID {user_id} not found"}), 404
    
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": f"User with ID {user_id} deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete user: {str(e)}"}), 500
    

@app.route('/api/users/<int:user_id>', methods=['PATCH'])
def patch_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": f"User with ID {user_id} not found"}), 404
    
    data = request.get_json()
    for key, value in data.items():
        if hasattr(user, key):
            setattr(user, key, value)
    
    try:
        db.session.commit()
        return jsonify({"message": f"User with ID {user_id} updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update user: {str(e)}"}), 500
    

@app.route('/api/users/summary', methods=['GET'])
def get_users_summary():
    total_users = User.query.count()
    avg_age = db.session.query(db.func.avg(User.age)).scalar()
    city_count = db.session.query(User.city, db.func.count(User.id)).group_by(User.city).all()
    
    summary = {
        "total_users": total_users,
        "average_age": avg_age,
        "count_by_city": {city: count for city, count in city_count}
    }
    
    return jsonify(summary), 200