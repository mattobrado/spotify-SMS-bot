"""SQLAlchemy models"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy() # Create database object

def connect_db(app):
  """Connect database to the Flask app"""

  db.app = app # Connect database to Flask object
  db.init_app(app) # Initialize database


class User(db.Model):
  """ A host user is associated with a spotify account
  The playlist is stored on their account
  Model to hold spotify user data"""

  __tablename__ = 'users'

  id = db.Column(db.Integer, primary_key=True)
  display_name = db.Column(db.Text, nullable=False)
  email = db.Column(db.Text, nullable=False, unique=True)
  url = db.Column(db.Text, nullable=False)
  phone_number = db.Column(db.Text, unique=True)
  access_token = db.Column(db.Text)
  refresh_token = db.Column(db.Text)

  active_playlist_id = db.Column(db.Text, db.ForeignKey('playlists.id'), nullable=True)
  # playlists = db.relationship('Playlist', backref='owner', cascade='all, delete-orphan')

  @property
  def playlists(self):
    """Get all playlists with owner_id = this user's id
    
    Needed to write this out instead on using a db.ForeignKey() argument in 
    playlists.owner_id because we're already using a db.ForeignKey() to link the 
    user's active playlist to a the Playlist table"""
    found_playlists = Playlist.query.filter_by(owner_id=self.id).all()
    found_playlists.reverse() # Return in reverse order so more recent playlists are first
    return found_playlists

  @property
  def auth_header(self):
    """Create the authorization header from the acccess token
    
    Return as a python dictionary"""

    return {'Authorization': f'Bearer {self.access_token}'}


class Playlist(db.Model):
  """Playlist"""

  __tablename__ = 'playlists'

  id = db.Column(db.Text, primary_key=True)
  title = db.Column(db.Text, nullable=False)
  url = db.Column(db.Text, nullable=False)
  endpoint = db.Column(db.Text, nullable=False)
  owner_id = db.Column(db.Integer, nullable=False)
