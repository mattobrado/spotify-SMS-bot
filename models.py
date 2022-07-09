from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy() # Create database object

def connect_db(app):
  """Connect database to the Flask app"""

  db.app = app # Connect database to Flask object
  db.init_app(app) # Initialize database

class User(db.Model):
  """User"""

  __tablename__ = "users"

  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.Text, nullable=False)

  # One user can have many playlists
  # Playlists be deleted once they are no longer associated with a user.
  playlists = db.relationship("Playlist", backref="user", cascade="all, delete-orphan")

class Playlist(db.Model):
  """Playlist"""

  __tablename__ = "playlists"

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.Text, nullable=False)

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
  name = db.Column(db.Text, nullable=False)
  artist = db.Column(db.Text, nullable=False)

class PlaylistSong(db.Model):
  """Song in a playlist.
  
  Many-to-many relationship between songs and playlist.
  PlaylistSongs are unique.
  """

  __tablename__ = "playlist_songs"

  playlist_id = db.Column(db.Integer, db.ForeignKey('playlists.id'), primary_key=True)
  song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), primary_key=True)
