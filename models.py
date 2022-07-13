"""SQLAlchemy models"""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy() # Create database object
bcrypt = Bcrypt() # Create bcrypt object

def connect_db(app):
  """Connect database to the Flask app"""

  db.app = app # Connect database to Flask object
  db.init_app(app) # Initialize database


class User(db.Model):
  """ A host user is associated with a spotify account
  The playlist is stored on their account
  Model to hold spotify user data"""

  __tablename__ = "users"

  id = db.Column(db.Integer, primary_key=True)
  display_name = db.Column(db.Text, nullable=False)
  email = db.Column(db.Text, nullable=False, unique=True)
  url = db.Column(db.Text, nullable=False)
  phone_number = db.Column(db.Text, unique=True)
  auth_header = db.Column(db.Text, unique=True)
  
  playlists = db.relationship("Playlist", backref="owner", cascade="all, delete-orphan")


class Playlist(db.Model):
  """Playlist"""

  __tablename__ = "playlists"

  id = db.Column(db.Text, primary_key=True)
  title = db.Column(db.Text, nullable=False)
  url = db.Column(db.Text, nullable=False)
  endpoint = db.Column(db.Text, nullable=False)
  owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)