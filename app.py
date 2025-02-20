from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure PostgreSQL Database 
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:Neethu@localhost:5432/user_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Define the User model to match the JSON data
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # ID field (primary key)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(2))
    zip = db.Column(db.Integer)
    email = db.Column(db.String(100), unique=True, nullable=False)
    web = db.Column(db.String(255))
    age = db.Column(db.Integer)

# Create tables if they don't exist
with app.app_context():
    db.create_all()
