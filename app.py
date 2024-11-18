from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt
import jwt
from functools import wraps
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuration
class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://klsyxpji:5B9bbUaUVCej0LLyTG2da_mSSlPQm4uK@stampy.db.elephantsql.com/klsyxpji'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your_secret_key_here'
    JWT_REFRESH_SECRET_KEY = 'your_refresh_secret_key_here'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)

app.config.from_object(Config)

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Token blacklist set to store invalidated tokens
token_blacklist = set()

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

    food_type = db.relationship('FoodType', backref=db.backref('food_items', lazy=True))

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
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default="GLUCOCHECK_USER")

# Initialize database
with app.app_context():
    db.create_all()

# Authentication utilities
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')

        if auth_header:
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Invalid token format!'}), 403

        if not token:
            return jsonify({'message': 'Token is missing!'}), 403

        if token in token_blacklist:
            return jsonify({'message': 'Token has been revoked!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['id']).first()
            if not current_user:
                return jsonify({'message': 'User not found!'}), 404
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 403

        return f(current_user, *args, **kwargs)
    return decorated_function

def generate_tokens(user):
    access_token = jwt.encode({
        'id': user.id,
        'exp': datetime.utcnow() + app.config['JWT_ACCESS_TOKEN_EXPIRES']
    }, app.config['SECRET_KEY'], algorithm="HS256")

    refresh_token = jwt.encode({
        'id': user.id,
        'exp': datetime.utcnow() + app.config['JWT_REFRESH_TOKEN_EXPIRES']
    }, app.config['JWT_REFRESH_SECRET_KEY'], algorithm="HS256")

    return access_token, refresh_token

# Routes
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    required_fields = ['first_name', 'last_name', 'email', 'password']
    
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"error": "Email already in use"}), 400

        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        new_user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password are required"}), 400

    try:
        user = User.query.filter_by(email=data['email']).first()
        if user and bcrypt.check_password_hash(user.password, data['password']):
            access_token, refresh_token = generate_tokens(user)
            return jsonify({
                'message': 'Login successful',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            }), 200
        return jsonify({'error': 'Invalid email or password'}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    token = request.headers.get('Authorization').split(" ")[1]
    token_blacklist.add(token)
    return jsonify({'message': 'Successfully logged out'}), 200

@app.route('/refresh', methods=['POST'])
def refresh():
    data = request.json
    if not data or not data.get('refresh_token'):
        return jsonify({"error": "Refresh token is required"}), 400

    try:
        token = data['refresh_token']
        if token in token_blacklist:
            return jsonify({'message': 'Refresh token has been revoked!'}), 401

        data = jwt.decode(token, app.config['JWT_REFRESH_SECRET_KEY'], algorithms=["HS256"])
        user = User.query.filter_by(id=data['id']).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        access_token, _ = generate_tokens(user)
        return jsonify({'access_token': access_token}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Refresh token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid refresh token'}), 403

@app.route('/save-food-items', methods=['POST'])
@token_required
def save_food_items(current_user):
    data = request.json
    if not data or 'foods' not in data:
        return jsonify({"error": "No food data provided"}), 400

    try:
        for food in data['foods']:
            food_type = FoodType.query.filter_by(type=food['type']).first()
            if not food_type:
                food_type = FoodType(type=food['type'])
                db.session.add(food_type)
                db.session.flush()

            new_food_item = FoodItem(
                name=food['name'],
                volume=food.get('volume'),
                food_type_id=food_type.id,
                timestamp=datetime.utcnow(),
                date_uploaded=datetime.utcnow()
            )
            db.session.add(new_food_item)
            db.session.flush()

            nutrition = NutritionalInformation(
                food_item_id=new_food_item.id,
                calories=food.get('calories'),
                carbs=food.get('carbs'),
                fat=food.get('fat'),
                protein=food.get('protein')
            )
            db.session.add(nutrition)

        db.session.commit()
        return jsonify({"message": "Food items saved successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/get-food-items', methods=['GET'])
@token_required
def get_food_items(current_user):
    try:
        food_items = FoodItem.query.order_by(FoodItem.timestamp.desc()).all()
        result = [{
            'id': food.id,
            'name': food.name,
            'volume': food.volume,
            'food_type': food.food_type.type,
            'timestamp': food.timestamp,
            'date_uploaded': food.date_uploaded,
            'nutrition': {
                'calories': food.nutrition[0].calories if food.nutrition else None,
                'carbs': food.nutrition[0].carbs if food.nutrition else None,
                'fat': food.nutrition[0].fat if food.nutrition else None,
                'protein': food.nutrition[0].protein if food.nutrition else None
            }
        } for food in food_items]

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delete-all', methods=['DELETE'])
def delete_all_data():
    """
    Delete all data from the database (FoodType, FoodItem, NutritionalInformation)
    ---
    responses:
      200:
        description: All data has been deleted successfully
      500:
        description: Error occurred while deleting data
    """
    try:
        # Start by deleting nutritional information
        db.session.query(NutritionalInformation).delete()

        # Then delete food items
        db.session.query(FoodItem).delete()

        # Finally, delete food types
        db.session.query(FoodType).delete()

        # Commit the changes to the database
        db.session.commit()

        # Log the action
        app.logger.info('All data deleted successfully')

        return jsonify({"message": "All data has been deleted successfully"}), 200

    except Exception as e:
        # Rollback any changes if an error occurs
        db.session.rollback()
        app.logger.error('Error deleting all data: %s', str(e), exc_info=True)
        return jsonify({"error": str(e)}), 500
    
@app.route('/food-items/<int:food_item_id>', methods=['DELETE'])
@token_required
def delete_food_item(current_user, food_item_id):
    try:
        # First, check if the food item exists
        food_item = FoodItem.query.get(food_item_id)
        
        if not food_item:
            return jsonify({"error": "Food item not found"}), 404
            
        NutritionalInformation.query.filter_by(food_item_id=food_item_id).delete()
        
        # Delete the food item
        db.session.delete(food_item)
        db.session.commit()
        
        return jsonify({
            "message": "Food item deleted successfully",
            "deleted_item_id": food_item_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)