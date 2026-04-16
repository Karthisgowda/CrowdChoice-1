import os
import logging
from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Define SQLAlchemy base class
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Create Flask app
BASE_DIR = Path(__file__).resolve().parent
app = Flask(
    __name__,
    static_folder=str(BASE_DIR / "public" / "static"),
    template_folder=str(BASE_DIR / "templates"),
)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key-for-development")

# Configure database
database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    # Fix for newer psycopg2 versions that expect postgresql://
    database_url = database_url.replace("postgres://", "postgresql://", 1)

if not database_url:
    instance_dir = Path("/tmp") if os.environ.get("VERCEL") else BASE_DIR / "instance"
    instance_dir.mkdir(exist_ok=True)
    database_url = f"sqlite:///{(instance_dir / 'crowdchoice.db').as_posix()}"

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the SQLAlchemy with the app
db.init_app(app)

app.logger.info(f"Using database: {app.config['SQLALCHEMY_DATABASE_URI']}")

with app.app_context():
    # Import models to create tables
    import models
    db.create_all()

# Import routes
from routes import *
