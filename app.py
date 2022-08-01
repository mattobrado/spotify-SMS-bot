"""Spotify GroupChat app"""

from flask import Flask, redirect, render_template, flash, session, request
from flask_debugtoolbar import DebugToolbarExtension
from flask_bootstrap import Bootstrap5
from twilio.twiml.messaging_response import MessagingResponse
import os

# from my_secrets import SECRET_KEY
from models import Playlist, connect_db, db
from sms import ask_for_playlist_key, invalid_playlist_key_notification, playlist_key_success_notification
from spotify import add_tracks_to_playlist, get_or_create_guest_user, get_playlist_key_from_message, get_track_ids_from_message, create_playlist
from demo.routes import demo
from auth.routes import auth
from ui.routes import user

app = Flask(__name__) # Create Flask object
app.register_blueprint(demo, url_prefix="/demo")
app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(user, url_prefix="/user")

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','postgres:///spotify_sms_playlist').replace("://", "ql://", 1) # PSQL database

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Don't track modifications
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'calebshouse') # SECRET_KEY for debug toolbar
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False # Disable intercepting redirects

toolbar = DebugToolbarExtension(app) # Create debug toolbar object
bootsrap =Bootstrap5(app) # Create bootstrap object


connect_db(app) # Connect database to Flask object 
db.create_all() # Create all tables


@app.route('/')
def root():
  """Redirect to auth /auth"""

  return redirect('/auth')


# -------------------------- Recieving Texts ---------------------------

@app.route('/api/receive_sms', methods=['POST'])
def receive_sms():
  """Route for Twilio to pass in recieved messages"""

  phone_number = request.form['From']
  message = request.form['Body']
  
  track_ids = get_track_ids_from_message(message) # Scan message for track_ids
  playlist_key = get_playlist_key_from_message(message) # Scan message for playlist keys

  # If the message contained either a playlist key or track id
  if playlist_key or track_ids:
    guest_user = get_or_create_guest_user(phone_number=phone_number) # Get the guest user object

    # If the message contined a playlist key
    if playlist_key:
      playlist = Playlist.query.filter_by(key=playlist_key).first() # Get phone number's first playlist
      
      # If the key belongs to a playlist
      if playlist:
        guest_user.active_playlist_id = playlist.id # Set the guest user's active playlist to that playlist
        db.session.add(guest_user)
        db.session.commit()
        playlist_key_success_notification(phone_number=phone_number, playlist=playlist) # Send a message to the user
      else:
        invalid_playlist_key_notification(phone_number, playlist_key)

    # If the message contained track ids
    if track_ids:
      # If the guest user has an active playlist
      if guest_user.active_playlist_id:
        playlist = Playlist.query.filter_by(id=guest_user.active_playlist_id).first() # Get phone number's first playlist
        # If playlist in valid
        if playlist:
          add_tracks_to_playlist(playlist=playlist, track_ids=track_ids, added_by=phone_number) # Add the tracks to the playlist
      else:
        ask_for_playlist_key(phone_number) # Ask the guest user for a playlist key
    
  return str(MessagingResponse())
