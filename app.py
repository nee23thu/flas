from flask import Flask
from database import db
from routes import users_bp  # Import the users blueprint
from flask_swagger_ui import get_swaggerui_blueprint
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a Flask application instance
app = Flask(__name__)
app.config.from_object(Config)  # Load configuration from config.py

# Initialize the database
db.init_app(app)

# Initialize JWT
app.config["JWT_SECRET_KEY"] = "your-secret-key"
jwt = JWTManager(app)

# Initialize Rate Limiter
limiter = Limiter(get_remote_address, app=app, default_limits=["100 per hour"])

# Register blueprints
app.register_blueprint(users_bp, url_prefix="/api/users")

# Swagger UI configuration
SWAGGER_URL = "/docs"
API_URL = "/static/swagger.yaml"

swagger_ui_bp = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "User Management API"}
)

app.register_blueprint(swagger_ui_bp, url_prefix=SWAGGER_URL)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
