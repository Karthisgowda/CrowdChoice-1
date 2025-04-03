import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Define SQLAlchemy base class
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key-for-development")

# Configure MySQL database (for XAMPP/phpMyAdmin)
# Format: mysql+pymysql://username:password@localhost/db_name
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", 
    "mysql+pymysql://root:@localhost/crowdsourced_decisions"
)
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize LoginManager for user authentication
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Initialize the SQLAlchemy with the app
db.init_app(app)

app.logger.info(f"Using database: {app.config['SQLALCHEMY_DATABASE_URI']}")

with app.app_context():
    # Import models to create tables
    import models
    db.create_all()

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Import routes
from routes import *
