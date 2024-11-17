import logging
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from flask_cors import CORS
from flasgger import Swagger

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize Swagger
swagger = Swagger(app)

# Database configuration for PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://klsyxpji:5B9bbUaUVCej0LLyTG2da_mSSlPQm4uK@stampy.db.elephantsql.com/klsyxpji'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# FoodType Model
class FoodType(db.Model):
    __tablename__ = 'food_type'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return f'<FoodType {self.type}>'

# FoodItem Model
class FoodItem(db.Model):
    __tablename__ = 'food_item'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    volume = db.Column(db.Float)
    food_type_id = db.Column(db.Integer, db.ForeignKey('food_type.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    date_uploaded = db.Column(db.DateTime, default=datetime.utcnow)  # New column for date_uploaded

    food_type = db.relationship('FoodType', backref=db.backref('food_items', lazy=True))

    def __repr__(self):
        return f'<FoodItem {self.name}>'

# NutritionalInformation Model
class NutritionalInformation(db.Model):
    __tablename__ = 'nutritional_information'
    id = db.Column(db.Integer, primary_key=True)
    food_item_id = db.Column(db.Integer, db.ForeignKey('food_item.id'), nullable=False)
    calories = db.Column(db.Float)
    carbs = db.Column(db.Float)
    fat = db.Column(db.Float)
    protein = db.Column(db.Float)

    food_item = db.relationship('FoodItem', backref=db.backref('nutrition', lazy=True))

    def __repr__(self):
        return f'<NutritionalInformation for FoodItem {self.food_item_id}>'

# Initialize the database
with app.app_context():
    db.create_all()

# # Endpoint to save identified food items
# @app.route('/save-food-items', methods=['POST'])
# def save_food_items():
#     """
#     Save food items and their nutritional information
#     ---
#     parameters:
#       - name: foods
#         in: body
#         required: true
#         type: array
#         items:
#           type: object
#           properties:
#             name:
#               type: string
#             volume:
#               type: number
#             type:
#               type: string
#             calories:
#               type: number
#             carbs:
#               type: number
#             fat:
#               type: number
#             protein:
#               type: number
#     responses:
#       201:
#         description: Food items saved successfully
#       400:
#         description: No data provided
#       500:
#         description: Error occurred
#     """
#     data = request.json
#     if not data:
#         return jsonify({"error": "No data provided"}), 400

#     try:
#         for food in data['foods']:
#             # Check if the food type exists, if not, create it
#             food_type = FoodType.query.filter_by(type=food['type']).first()
#             if not food_type:
#                 food_type = FoodType(type=food['type'])
#                 db.session.add(food_type)
#                 db.session.commit()

#             # Create the food item
#             new_food_item = FoodItem(
#                 name=food['name'],
#                 volume=food.get('volume', None),
#                 food_type_id=food_type.id,
#                 date_uploaded=datetime.utcnow()  # Set the upload time
#             )
#             db.session.add(new_food_item)
#             db.session.commit()

#             # Add nutritional information
#             nutrition = NutritionalInformation(
#                 food_item_id=new_food_item.id,
#                 calories=food.get('calories', None),
#                 carbs=food.get('carbs', None),
#                 fat=food.get('fat', None),
#                 protein=food.get('protein', None)
#             )
#             db.session.add(nutrition)

#         db.session.commit()

#         return jsonify({"message": "Food items saved successfully"}), 201

#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"error": str(e)}), 500

@app.route('/save-food-items', methods=['POST'])
def save_food_items():
    app.logger.debug('Received request data: %s', request.json)
    
    data = request.json
    if not data:
        app.logger.error('No data provided')
        return jsonify({"error": "No data provided"}), 400
 
    try:
        if 'foods' not in data:
            app.logger.error('Missing foods key in data')
            return jsonify({"error": "Missing foods key in request"}), 400

        for food in data['foods']:
            app.logger.debug('Processing food item: %s', food)
            
            # Validate required fields
            if 'type' not in food or 'name' not in food:
                app.logger.error('Missing required fields in food item: %s', food)
                return jsonify({"error": f"Missing required fields in food item: {food}"}), 400

            # Check if the food type exists, if not, create it
            food_type = FoodType.query.filter_by(type=food['type']).first()
            if not food_type:
                food_type = FoodType(type=food['type'])
                db.session.add(food_type)
                db.session.flush()  # Get the ID without committing
                app.logger.debug('Created new food type: %s', food_type.type)

            # Create the food item
            new_food_item = FoodItem(
                name=food['name'],
                volume=food.get('volume', None),
                food_type_id=food_type.id,
                date_uploaded=datetime.utcnow()
            )
            db.session.add(new_food_item)
            db.session.flush()  # Get the ID without committing
            app.logger.debug('Created new food item: %s', new_food_item.name)

            # Add nutritional information
            nutrition = NutritionalInformation(
                food_item_id=new_food_item.id,
                calories=food.get('calories', None),
                carbs=food.get('carbs', None),
                fat=food.get('fat', None),
                protein=food.get('protein', None)
            )
            db.session.add(nutrition)
            app.logger.debug('Added nutritional information for: %s', new_food_item.name)

        db.session.commit()
        app.logger.info('Successfully saved all food items')
        return jsonify({"message": "Food items saved successfully"}), 201
 
    except Exception as e:
        db.session.rollback()
        app.logger.error('Error saving food items: %s', str(e), exc_info=True)
        return jsonify({"error": str(e)}), 500

# Endpoint to get all food items
@app.route('/get-food-items', methods=['GET'])
def get_food_items():
    """
    Get all food items
    ---
    responses:
      200:
        description: A list of food items
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              name:
                type: string
              volume:
                type: number
              food_type:
                type: string
              timestamp:
                type: string
              date_uploaded:
                type: string
      500:
        description: Error occurred
    """
    try:
        food_items = FoodItem.query.all()
        result = []
        
        for food in food_items:
            food_data = {
                'id': food.id,
                'name': food.name,
                'volume': food.volume,
                'food_type': food.food_type.type,
                'timestamp': food.timestamp.isoformat(),
                'date_uploaded': food.date_uploaded
            }
            result.append(food_data)
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to get nutritional information
@app.route('/get-nutritional-info/<int:food_item_id>', methods=['GET'])
def get_nutritional_info(food_item_id):
    """
    Get nutritional information for a specific food item
    ---
    parameters:
      - name: food_item_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Nutritional information for the specified food item
        schema:
          type: object
          properties:
            food_item_id:
              type: integer
            calories:
              type: number
            carbs:
              type: number
            fat:
              type: number
            protein:
              type: number
      404:
        description: Food item not found
      500:
        description: Error occurred
    """
    try:
        nutritional_info = NutritionalInformation.query.filter_by(food_item_id=food_item_id).first()
        if not nutritional_info:
            return jsonify({"error": "Nutritional information not found for this food item"}), 404

        result = {
            'food_item_id': nutritional_info.food_item_id,
            'calories': nutritional_info.calories,
            'carbs': nutritional_info.carbs,
            'fat': nutritional_info.fat,
            'protein': nutritional_info.protein
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Test endpoint
@app.route('/test', methods=['GET'])
def test():
    """
    Test endpoint
    ---
    responses:
      200:
        description: Test route works!
    """
    return jsonify({"message": "Test route works!"})

@app.errorhandler(500)
def handle_500_error(e):
    app.logger.error('Internal Server Error: %s', str(e), exc_info=True)
    return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.logger.setLevel(logging.DEBUG)
    app.run(host='0.0.0.0', port=8080, debug=True)
