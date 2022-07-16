"""Spotify GroupChat app"""

from flask import Flask, redirect, render_template, flash, session, request
from flask_debugtoolbar import DebugToolbarExtension
from flask_bootstrap import Bootstrap5
from twilio.twiml.messaging_response import MessagingResponse

from my_secrets import SECRET_KEY
from models import GuestUser, HostUser, Playlist, connect_db, db
from forms import PhoneForm, CreatePlaylistForm, load_select_playlist_form_choices
from sms import ask_for_playlist_key, invalid_playlist_key_notification, playlist_key_success_notification
from spotify import AUTHORIZATION_URL, add_tracks_to_playlist, get_or_create_guest_user, get_or_create_host_user, get_playlist_key_from_message, get_track_ids_from_message, create_playlist, get_auth_tokens


app = Flask(__name__) # Create Flask object

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///spotify_sms_playlist' # PSQL database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Don't track modifications
app.config['SECRET_KEY'] = SECRET_KEY # SECRET_KEY for debug toolbar
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False # Disable intercepting redirects

toolbar = DebugToolbarExtension(app) # Create debug toolbar object
bootsrap =Bootstrap5(app) # Create bootstrap object


connect_db(app) # Connect database to Flask object 
db.create_all() # Create all tables


@app.route('/')
def root():
  """Redirect to /authorize"""

  return redirect('/authorize')

# -------------------------- AUTHORIZATION/LOGIN ---------------------------

@app.route('/authorize', methods=['GET', 'POST'])
def get_authorization():
  """Make a call to the Spotify to request authorization to access a user's account"""

  return redirect(AUTHORIZATION_URL) # AUTHORIZATION_URL is assembled in spotify.py


@app.route('/login')
def login():
  """Use code from spotify redirect to get authorizion and retrive or ceate a HostUser"""

  code = request.args['code'] # Get code returned from authorization
  auth_data = get_auth_tokens(code) # Get authorization header
  host_user = get_or_create_host_user(auth_data) # Get or create a HostUser based on their spotify profile data
  session['host_user_id'] = host_user.id # Save host_user_id in session

  return redirect('/profile')


@app.route('/log-out')
def log_out():
  """Remove host_user data from session and redirect to the authorization route"""

  session.clear() # Remover user data from session
  return redirect('/authorize')


# -------------------------- PROFILE PAGE ---------------------------

@app.route('/profile/')
def redirect_to_active_playlist():
  """Bring a user to their active playlist page"""

  host_user = get_host_user_from_session()

  # Prevent users from jumping ahead to /profile without first authorizing
  if not host_user:
    return redirect('/authorize')
  
  # If the user soes not have a phone number, rediect the the phone number form
  if not host_user.phone_number:
    flash('Enter your phone number to create a playlist', 'warning')
    return redirect('/phone')

  playlist_id = host_user.active_playlist_id # Get the users active playlist

  # If the user doesn't have an active playlist
  if not playlist_id:
    flash("You don't have any playlists yet", 'warning')
    return redirect("/playlists") # Redirect the user to the playlists page to create a playlist
  else:
    return redirect(f"/profile/{playlist_id}") # Redirect to the user's active playlist page


@app.route('/profile/<string:playlist_id>', methods=['GET', 'POST'])
def show_profile(playlist_id):
  """Show a user's playlist"""
  
  host_user = get_host_user_from_session()

  # Prevent users from jumping ahead to /profile without first authorizing
  if not host_user:
    return redirect('/authorize')

  playlist = Playlist.query.get_or_404(playlist_id) # Get the playlist

  form = load_select_playlist_form_choices(host_user=host_user) # Get a form with all of a host user's playlists as choices

  # When the form is submitted
  if form.validate_on_submit():
    new_playlist_id = form.playlist.data # Get playlist id from form
    return redirect(f"/profile/{new_playlist_id}")  # Redirect to that playlist's page

  return render_template('profile.html', host_user=host_user, playlist=playlist, form=form)


@app.route('/phone', methods = ['GET', 'POST'])
def get_phone_number():
  """Get a user's phone number using the PhoneForm"""

  host_user = get_host_user_from_session()

  # Prevent users from jumping ahead without first authorizing
  if not host_user:
    return redirect('/authorize')

  form = PhoneForm() # Form for getting phone numbers

  if form.validate_on_submit():
    guest_user = GuestUser.query.filter_by(phone_number=form.phone.data).first()
    # if there is a guest user with that phone number
    if guest_user:
      host_user.active_playlist_id = guest_user.active_playlist_id #copy the guest user's active playlist
      db.session.delete(guest_user) # delete guest user to replace them with host user
      db.session.commit()

    host_user.phone_number = form.phone.data # Set host user's phone number
    db.session.add(host_user)
    db.session.commit()
    flash('Phone Number Updated', 'success')
    return redirect('/profile')
  
  return render_template('phone.html', user=host_user, form=form)


@app.route('/playlists', methods = ['GET', 'POST'])
def show_playlists():
  """Show all of users playlists and a """

  host_user = get_host_user_from_session()

  # Prevent users from jumping ahead without first authorizing
  if not host_user:
    return redirect('/authorize')
  
  form = CreatePlaylistForm() # Form for making a new playlist

  # When the form is submitted
  if form.validate_on_submit():
    title = form.title.data # Get title from form
    key = form.key.data.lower()
    create_playlist(host_user=host_user, title=title, key=key) # Create the playlist
    flash('Playlist Created', 'success')
    return redirect('/profile')

  return render_template('playlists.html', host_user=host_user, form=form)


@app.route('/profile/<string:playlist_id>/delete', methods=['POST'])
def delete_playlist(playlist_id):
  """Delete a playlist"""

  playlist = Playlist.query.get_or_404(playlist_id) # Get the playlist

  # If the host user is the owner of the playlist
  if playlist.owner_id == session['host_user_id']:
    # Get users who have that playlist as their active playlist
    guest_users = GuestUser.query.filter_by(active_playlist_id=playlist_id).all()
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

  return redirect('/profile')

@app.route('/profile/<string:playlist_id>/activate', methods=['POST'])
def activate_playlist(playlist_id):
  """Delete a playlist"""

  playlist = Playlist.query.get_or_404(playlist_id) # Get the playlist

  # If the host user is the owner of the playlist
  if playlist.owner_id == session['host_user_id']:
    # Get users who have that playlist as their active playlist
    guest_users = GuestUser.query.filter_by(active_playlist_id=playlist_id).all()
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

  return redirect('/profile')


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
  """Prevent users from jumping ahead to /profile without first authorizing"""

  if 'host_user_id' not in session:
    flash('Please log in', 'warning')
    return None

  else:
    return HostUser.query.get_or_404(session['host_user_id']) # Get host_user using host_user_id in session

