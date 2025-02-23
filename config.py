class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:Neethu@localhost:5432/user_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:Neethu@localhost:5432/user_db_test"
    TESTING = True
