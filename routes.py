from flask import Flask, request, jsonify
from database import db
from models import User
from config import DATABASE_URI

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

#LIST USERS (GET /api/users)
@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

#GET USER BY ID (GET /api/users/<id>)
@app.route('/api/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_dict())

#CREATE A NEW USER (POST /api/users)
@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = User(**data)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.to_dict()), 201

#UPDATE USER (PUT /api/users/<id>)
@app.route('/api/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.query.get_or_404(id)
    data = request.get_json()
    for key, value in data.items():
        setattr(user, key, value)
    db.session.commit()
    return jsonify(user.to_dict())

#DELETE USER (DELETE /api/users/<id>)
@app.route('/api/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return '', 204

#PARTIALLY UPDATE USER (PATCH /api/users/<id>)
@app.route('/api/users/<int:id>', methods=['PATCH'])
def partial_update_user(id):
    user = User.query.get_or_404(id)
    data = request.get_json()
    for key, value in data.items():
        if hasattr(user, key):
            setattr(user, key, value)
    db.session.commit()
    return jsonify(user.to_dict())

if __name__ == '__main__':
    app.run(debug=True)
