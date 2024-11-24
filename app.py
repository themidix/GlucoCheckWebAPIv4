#app.y
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from config import Config
from flask_migrate import Migrate 
from authlib.integrations.flask_client import OAuth


db = SQLAlchemy()
bcrypt = Bcrypt()
oauth = OAuth()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    db.init_app(app)
    bcrypt.init_app(app) 

    Migrate(app, db) 
    # Register blueprints
    from routes import jwt_auth_blueprint, google_auth_blueprint, food_item_blueprint, food_type_blueprint, nutritional_info_blueprint, food_image_info_blueprint
    app.register_blueprint(jwt_auth_blueprint, url_prefix="/auth-user")
    app.register_blueprint(google_auth_blueprint, url_prefix="/google-auth")
    app.register_blueprint(food_item_blueprint, url_prefix="/food")
    app.register_blueprint(food_type_blueprint, url_prefix="/food-type")
    app.register_blueprint(nutritional_info_blueprint, url_prefix="/nutritional-information")
    app.register_blueprint(food_image_info_blueprint, url_prefix="/image-information")

    return app
