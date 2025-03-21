import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import pymongo
from pymongo import MongoClient

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

# Configure the database for SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///polls.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize MongoDB connection
mongo_password = os.environ.get("MONGODB_PASSWORD")
if mongo_password:
    try:
        # Properly escape password for MongoDB URI
        from urllib.parse import quote_plus
        escaped_password = quote_plus(mongo_password)
        mongodb_uri = f"mongodb+srv://karthiksgowda28:{escaped_password}@railwayapp.tnohc.mongodb.net/?retryWrites=true&w=majority&appName=railwayapp"
        
        # Connect with a timeout
        mongo_client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        mongo_db = mongo_client.polls_db
        
        # Test connection
        mongo_client.admin.command('ping')
        app.logger.info("MongoDB connection successful!")
        app.config['MONGODB_CONNECTED'] = True
    except Exception as e:
        app.logger.error(f"MongoDB connection error: {e}")
        app.config['MONGODB_CONNECTED'] = False
        # Fallback to SQLite only
        app.logger.info("Continuing with SQLite database only.")
else:
    app.logger.warning("MongoDB password not provided. MongoDB features will be disabled.")
    app.config['MONGODB_CONNECTED'] = False

# Initialize the SQLAlchemy with the app
db.init_app(app)

with app.app_context():
    # Import models to create tables
    import models
    db.create_all()

# Import routes
from routes import *
