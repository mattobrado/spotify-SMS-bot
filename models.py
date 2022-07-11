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
  """Model to hold spotify user data"""

  __tablename__ = "users"

  id = db.Column(db.Integer, primary_key=True)
  display_name = db.Column(db.Text, nullable=False)
  email = db.Column(db.Text, nullable=False, unique=True)
  url = db.Column(db.Text, nullable=False)
  # phone_number

  # One user can have many playlists
  # Playlists are deleted once they are no longer associated with a user.
  playlists = db.relationship("Playlist", backref="user", cascade="all, delete-orphan")


class Playlist(db.Model):
  """Playlist"""

  __tablename__ = "playlists"

  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.Text, nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
  url = db.Column(db.Text, nullable=False)

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
