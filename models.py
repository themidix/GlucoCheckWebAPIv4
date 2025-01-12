#models.py
from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash

# Models
class FoodType(db.Model):
    __tablename__ = 'food_type'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False, unique=True)

class FoodItem(db.Model):
    __tablename__ = 'food_item'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    volume = db.Column(db.Float)
    food_type_id = db.Column(db.Integer, db.ForeignKey('food_type.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    date_uploaded = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    food_type = db.relationship('FoodType', backref=db.backref('food_items', lazy=True))
    user = db.relationship('User', backref=db.backref('food_items', lazy=True))

    __table_args__ = (
        db.Index('idx_food_timestamp', 'timestamp'),
        db.Index('idx_food_user_id', 'user_id'),
        db.Index('idx_food_type_id', 'food_type_id')
    )

class NutritionalInformation(db.Model):
    __tablename__ = 'nutritional_information'
    id = db.Column(db.Integer, primary_key=True)
    food_item_id = db.Column(db.Integer, db.ForeignKey('food_item.id'), nullable=False)
    calories = db.Column(db.Float)
    carbs = db.Column(db.Float)
    fat = db.Column(db.Float)
    protein = db.Column(db.Float)

    food_item = db.relationship('FoodItem', backref=db.backref('nutrition', lazy=True))

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default="GLUCOCHECK_USER")
    is_admin = db.Column(db.Boolean, default=False)
    
    # Add helper methods for role checking
    def is_super_user(self):
        return self.role == "GLUCOCHECK_ADMIN" and self.is_admin
    
    @staticmethod
    def create_admin_user(email, password, first_name, last_name):
        admin = User(
            email=email,
            password=password,  # Make sure to hash this password
            first_name=first_name,
            last_name=last_name,
            role="GLUCOCHECK_ADMIN",
            is_admin=True
        )
        return admin

