from sql_alchemy import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(255))
    city = db.Column(db.String(100))
    state = db.Column(db.String(10))
    zip = db.Column(db.Integer)
    email = db.Column(db.String(255), unique=True, nullable=False)
    web = db.Column(db.String(255))
    age = db.Column(db.Integer)

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}
