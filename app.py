"""Spotify GroupChat app"""

from flask import Flask, redirect, render_template, flash, session, request
from flask_debugtoolbar import DebugToolbarExtension
from flask_bootstrap import Bootstrap5
from twilio.twiml.messaging_response import MessagingResponse
import os

# from my_secrets import SECRET_KEY
from models import GuestUser, HostUser, Playlist, connect_db, db
from forms import CreatePlaylistForm, load_select_playlist_form_choices
from sms import ask_for_playlist_key, invalid_playlist_key_notification, playlist_key_success_notification
from spotify import add_tracks_to_playlist, get_or_create_guest_user, get_playlist_key_from_message, get_track_ids_from_message, create_playlist
from demo.routes import demo
from auth.routes import auth

app = Flask(__name__) # Create Flask object
app.register_blueprint(demo, url_prefix="/demo")
app.register_blueprint(auth, url_prefix="/auth")

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


# -------------------------- USER PAGE ---------------------------

@app.route('/user/')
def redirect_to_active_playlist():
  """Bring a user to their active playlist page"""

  host_user = get_host_user_from_session()

  # Prevent users from jumping ahead to /user without first authorizing
  if not host_user:
    return redirect('/auth')
  
  # If the user soes not have a phone number, rediect the the phone number form
  if not host_user.phone_number:
    return redirect('/auth/phone')

  playlist_id = host_user.active_playlist_id # Get the users active playlist

  # If the user doesn't have an active playlist
  if not playlist_id:
    flash("You don't have any playlists yet", 'warning')
    return redirect("/playlists") # Redirect the user to the playlists page to create a playlist
  else:
    return redirect(f"/user/{playlist_id}") # Redirect to the user's active playlist page


@app.route('/user/<string:id>', methods=['GET', 'POST'])
def show_playlist(id):
  """Show a user's playlist"""
  
  host_user = get_host_user_from_session()

  # Prevent users from jumping ahead to /user without first authorizing
  if not host_user:
    return redirect('/auth')

  playlist = Playlist.query.filter_by(id = id).first() # Get the playlist

  if not playlist:
    return redirect("/playlists") # Redirect the user to the playlists page to create a playlist

  form = load_select_playlist_form_choices(host_user=host_user) # Get a form with all of a host user's playlists as choices

  # When the form is submitted
  if form.validate_on_submit():
    new_playlist_id = form.playlist.data # Get playlist id from form
    return redirect(f"/user/{new_playlist_id}")  # Redirect to that playlist's page

  return render_template('profile.html', host_user=host_user, playlist=playlist, form=form)


@app.route('/playlists', methods = ['GET', 'POST'])
def show_playlists():
  """Show all of users playlists and a """

  host_user = get_host_user_from_session()

  # Prevent users from jumping ahead without first authorizing
  if not host_user:
    return redirect('/auth')
  
  form = CreatePlaylistForm() # Form for making a new playlist

  # When the form is submitted
  if form.validate_on_submit():
    title = form.title.data # Get title from form
    key = form.key.data.lower()
    create_playlist(host_user=host_user, title=title, key=key) # Create the playlist
    flash('Playlist Created', 'success')
    return redirect('/user')

  return render_template('playlists.html', host_user=host_user, form=form)


@app.route('/user/<string:id>/delete', methods=['POST'])
def delete_playlist(id):
  """Delete a playlist"""

  playlist = Playlist.query.get_or_404(id) # Get the playlist

  # If the host user is the owner of the playlist
  if playlist.owner_id == session['host_user_id']:
    # Get users who have that playlist as their active playlist
    guest_users = GuestUser.query.filter_by(active_playlist_id=id).all()
    for guest_user in guest_users:
      guest_user.active_playlist_id = None # Set thier active playlist id to None
      db.session.add(guest_user)
    
    db.session.delete(playlist) # delete the playlist (This will not delete the playlist on spotify)
    db.session.commit()
    flash('Playlist Deleted', 'warning')
    return redirect('/playlists')
  
  # HostUser is not authorized to delete the playlist
  else:
    flash('You cannot delete that playlist')

  return redirect('/user')

@app.route('/user/<string:id>/activate', methods=['POST'])
def activate_playlist(id):
  """Set a playlist to be a user's active playlist"""

  host_user = get_host_user_from_session()
  playlist = Playlist.query.get_or_404(id) # Get the playlist

  if playlist:
    host_user.active_playlist_id = playlist.id
    db.session.add(host_user) 
    db.session.commit()
    flash('Playlist activated, songs recieved from you will go here', 'success')
    return redirect(f"/user/{playlist.id}")

  return redirect('/user')


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


def get_host_user_from_session():
  """Prevent users from jumping ahead to /user without first authorizing"""

  if 'host_user_id' not in session:
    return None
  else:
    return HostUser.query.get_or_404(session['host_user_id']) # Get host_user using host_user_id in session

