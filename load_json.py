import json
from app import app, db, User  # Import from your Flask application

# Read JSON data from the file
with open('users.json', 'r') as file:
    users = json.load(file)

# Use Flask's application context to access the database
with app.app_context():
    for user_data in users:
        # Check if the user already exists to prevent duplicates
        existing_user = User.query.filter_by(email=user_data["email"]).first()
        if not existing_user:
            # Create a new user entry
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
            db.session.add(new_user)

    # Commit the changes to the database
    db.session.commit()

print("JSON data has been successfully inserted into the database!")
print("Loading JSON file...")
print("Connecting to PostgreSQL database...")
print("Inserting data into the database...")
print("Data successfully inserted!")

