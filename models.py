"""SQLAlchemy models"""

from flask_sqlalchemy import SQLAlchemy
import phonenumbers

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
  access_token = db.Column(db.Text)
  refresh_token = db.Column(db.Text)

  phone_number = db.Column(db.Text, db.ForeignKey('phone_numbers.number'))

  playlists = db.relationship('Playlist', backref='owner', cascade='all, delete-orphan')

  # @property
  # def playlists(self):
  #   """Get all playlists with owner_id = this user's id
    
  #   Needed to write this out instead on using a db.ForeignKey() argument in 
  #   playlists.owner_id because we're already using a db.ForeignKey() to link the 
  #   user's active playlist to a the Playlist table"""
  #   found_playlists = Playlist.query.filter_by(owner_id=self.id).all()
  #   found_playlists.reverse() # Return in reverse order so more recent playlists are first
  #   return found_playlists

  @property
  def auth_header(self):
    """Create the authorization header from the acccess token
    
    Return as a python dictionary"""

    return {'Authorization': f'Bearer {self.access_token}'}


class PhoneNumber(db.Model):
  """Phone Number
  
  could belong to a user or not"""
  
  __tablename__ = 'phone_numbers'

  number = db.Column(db.Text, primary_key=True)
  active_playlist = db.Column(db.Text, db.ForeignKey('playlists.id'))


class Playlist(db.Model):
  """Playlist"""

  __tablename__ = 'playlists'

  id = db.Column(db.Text, primary_key=True)
  title = db.Column(db.Text, nullable=False)
  key = db.Column(db.Text, unique=True, nullable=False)
  url = db.Column(db.Text, nullable=False)
  endpoint = db.Column(db.Text, nullable=False)
  owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


class Track(db.Model):
  """Track"""

  __tablename__ = 'tracks'

  id = db.Column(db.Text, primary_key=True)
  title = db.Column(db.Text, nullable=False)
  artist = db.Column(db.Text, nullable=False)


class TrackInPlaylist(db.Model):
  """A track in a playlist that was added by someone with a text message"""

  playlist_id = db.Column(db.Text, db.ForeignKey('playlists.id'), primary_key=True)
  track_id = db.Column(db.Text, db.ForeignKey('tracks.id'), primary_key=True)
  added_by = db.Column(db.Text, unique=True)
