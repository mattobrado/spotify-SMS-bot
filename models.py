"""SQLAlchemy models"""

import bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy() # Create database object
bcrypt = Bcrypt() # Create bcrypt object

def connect_db(app):
  """Connect database to the Flask app"""

  db.app = app # Connect database to Flask object
  db.init_app(app) # Initialize database

class User(db.Model):
  """User"""

  __tablename__ = "users"

  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.Text, nullable=False)
  password = db.Column(db.Text, nullable=False)

  # One user can have many playlists
  # Playlists be deleted once they are no longer associated with a user.
  playlists = db.relationship("Playlist", backref="user", cascade="all, delete-orphan")

  @classmethod
  def register(cls, username, password):
    """Register user with hashed password & return User object"""

    hashed_password = bcrypt.generate_password_hash(password) # Hash password using bcrypt
    hashed_password_utf8 = hashed_password.decode("utf8") # Convert bytestring into unicode utf8 string

    return cls(username=username,password=hashed_password_utf8)

  @classmethod
  def authenticate(cls, username, password):
    """Validate that user exists & password is correct.
    
    Returns User object if valid, else returns False.
    """

    user = User.query.filter_by(username=username).first() # Get User with username

    # If no user is found, return False
    if user:
      return False
    
    # If password is correct, return User object
    if bcrypt.check_password_hash(user.password, password):
      return user
    else:
      return False # Password was incorrect, return False

class Playlist(db.Model):
  """Playlist"""

  __tablename__ = "playlists"

  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.Text, nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

  # Two-way relationship between playlists and songs
  songs = db.relationship(
    "Song",
    secondary="playlist_songs",
    backref="playlists"
  )


class Song(db.Model):
  """Song"""

  __tablename__ = "songs"
  
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.Text, nullable=False)
  artist = db.Column(db.Text, nullable=False)

class PlaylistSong(db.Model):
  """Song in a playlist.
  
  Many-to-many relationship between songs and playlist.
  PlaylistSongs are unique.
  """

  __tablename__ = "playlist_songs"

  playlist_id = db.Column(db.Integer, db.ForeignKey('playlists.id'), primary_key=True)
  song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), primary_key=True)
