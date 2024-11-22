from flask import Blueprint, request, jsonify
import app
from models import User, FoodItem, FoodType, NutritionalInformation
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt
import jwt
from functools import wraps
from app import db
from config import Config
import re
from flask_mail import Mail, Message

# Blueprints
jwt_auth_blueprint = Blueprint('auth', __name__)
food_item_blueprint = Blueprint('food-items', __name__)
food_type_blueprint = Blueprint('food-type', __name__)
nutritional_info_blueprint = Blueprint('nutritional-information', __name__)
bcrypt = Bcrypt()

# Token blacklist
token_blacklist = set()

mail = Mail()

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
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.get(data['id'])
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
        'exp': datetime.utcnow() + Config.JWT_ACCESS_TOKEN_EXPIRES
    }, Config.SECRET_KEY, algorithm="HS256")

    refresh_token = jwt.encode({
        'id': user.id,
        'exp': datetime.utcnow() + Config.JWT_REFRESH_TOKEN_EXPIRES
    }, Config.JWT_REFRESH_SECRET_KEY, algorithm="HS256")

    return access_token, refresh_token

# Validation utility functions
def is_valid_email(email):
    """Validate the email format using regex."""
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email)

def is_valid_password(password):
    """
    Validate password:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$'
    return re.match(password_regex, password)

@jwt_auth_blueprint.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data or not all(field in data for field in ['first_name', 'last_name', 'email', 'password']):
        return jsonify({"error": "Missing required fields"}), 400

    # Validate email
    if not is_valid_email(data['email']):
        return jsonify({"error": "Invalid email format"}), 400

    # Validate password
    if not is_valid_password(data['password']):
        return jsonify({
            "error": "Password must be at least 8 characters long, include an uppercase letter, a lowercase letter, a number, and a special character"
        }), 400

    try:
        # Check for existing user before creating
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
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

        return jsonify({
            "message": "User registered successfully", 
            "user_id": new_user.id
        }), 201

    except Exception as e:
        db.session.rollback()
        # Log the specific error for debugging
        print(f"Registration error: {str(e)}")
        return jsonify({"error": "Registration failed", "details": str(e)}), 500

@jwt_auth_blueprint.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password are required"}), 400

    # Validate email
    if not is_valid_email(data['email']):
        return jsonify({"error": "Invalid email format"}), 400

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

@jwt_auth_blueprint.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    token = request.headers.get('Authorization').split(" ")[1]
    token_blacklist.add(token)
    return jsonify({'message': 'Successfully logged out'}), 200

@jwt_auth_blueprint.route('/refresh', methods=['POST'])
def refresh():
    data = request.json
    if not data or not data.get('refresh_token'):
        return jsonify({"error": "Refresh token is required"}), 400

    try:
        token = data['refresh_token']
        if token in token_blacklist:
            return jsonify({'message': 'Refresh token has been revoked!'}), 401

        data = jwt.decode(token, Config.JWT_REFRESH_SECRET_KEY, algorithms=["HS256"])
        user = User.query.get(data['id'])
        if not user:
            return jsonify({"error": "User not found"}), 404

        access_token, _ = generate_tokens(user)
        return jsonify({'access_token': access_token}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Refresh token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid refresh token'}), 403
    
@jwt_auth_blueprint.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    if not data or not data.get('email'):
        return jsonify({"error": "Email is required"}), 400

    user = User.query.filter_by(email=data['email']).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Generate a password reset token
    reset_token = jwt.encode({
        'id': user.id,
        'exp': datetime.utcnow() + Config.RESET_PASSWORD_TOKEN_EXPIRES
    }, Config.SECRET_KEY, algorithm="HS256")

    reset_link = f"http://localhost:5000/reset-password/{reset_token}"
    msg = Message(
        "Password Reset Request",
        sender="your_email@example.com",
        recipients=[user.email]
    )
    msg.body = f"Click the link to reset your password: {reset_link}"
    mail.send(msg)

    return jsonify({"message": "Password reset email sent"}), 200


@jwt_auth_blueprint.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    data = request.json
    if not data or not data.get('password'):
        return jsonify({"error": "Password is required"}), 400

    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        user = User.query.get(payload['id'])
        if not user:
            return jsonify({"error": "User not found"}), 404

        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        user.password = hashed_password
        db.session.commit()

        return jsonify({"message": "Password reset successful"}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token has expired"}), 400
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 400

@jwt_auth_blueprint.route('/profile/reset-password', methods=['POST'])
@token_required
def reset_password_from_profile(current_user):
    data = request.json
    if not data or not all(field in data for field in ['current_password', 'new_password']):
        return jsonify({"error": "Current and new passwords are required"}), 400

    if not bcrypt.check_password_hash(current_user.password, data['current_password']):
        return jsonify({"error": "Current password is incorrect"}), 401

    hashed_password = bcrypt.generate_password_hash(data['new_password']).decode('utf-8')
    current_user.password = hashed_password
    db.session.commit()

    return jsonify({"message": "Password updated successfully"}), 200

@food_item_blueprint.route('/save-food-items', methods=['POST'])
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
                date_uploaded=datetime.utcnow(),
                user_id=current_user.id  # Associate the food item with the current user
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

@food_item_blueprint.route('/get-food-items', methods=['GET'])
@token_required
def get_food_items(current_user):
    try:
        food_items = FoodItem.query.filter_by(user_id=current_user.id).order_by(FoodItem.timestamp.desc()).all()
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

@food_item_blueprint.route('/delete-all', methods=['DELETE'])
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
    
@food_item_blueprint.route('/food-items/<int:food_item_id>', methods=['DELETE'])
@token_required
def delete_food_item(current_user, food_item_id):
    try:
        # First, check if the food item exists and belongs to the current user
        food_item = FoodItem.query.filter_by(id=food_item_id, user_id=current_user.id).first()
        
        if not food_item:
            return jsonify({"error": "Food item not found or does not belong to you"}), 404
            
        NutritionalInformation.query.filter_by(food_item_id=food_item_id).delete()

        db.session.delete(food_item)
        db.session.commit()
        
        return jsonify({
            "message": "Food item deleted successfully",
            "deleted_item_id": food_item_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500