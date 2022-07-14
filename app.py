"""Spotify GroupChat app"""

from flask import Flask, redirect, render_template, flash, session, request
from flask_debugtoolbar import DebugToolbarExtension
from flask_bootstrap import Bootstrap5
from twilio.twiml.messaging_response import MessagingResponse

from my_secrets import SECRET_KEY
from models import Playlist, connect_db, db, User
from forms import PhoneForm, PlaylistForm
from spotify import AUTHORIZATION_URL, add_tracks_to_playlist, get_track_ids_from_message, create_playlist, get_auth_token_header, get_profile_data


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
  """1st call in the Spotify authorization process.
  
  Request authorization to auth data"""

  return redirect(AUTHORIZATION_URL) # AUTHORIZATION_URL is assembled in spotify.py


@app.route('/login')
def login():
  """2nd call in the Spotify authorization process.
  
  Request auth token"""

  code = request.args['code'] # Get code returned from authorization
  auth_header = get_auth_token_header(code) # Get authorization header

  profile_data = get_profile_data(auth_header) # Make an API request to get profile data

  display_name = profile_data['display_name']
  email = profile_data['email']
  url = profile_data['external_urls']['spotify']
  id = profile_data['id'] # Use same id as spotify

  user = User.query.filter_by(email=email).first() # Look up user

  # If the user is not in the database
  if not user:
    user = User(display_name=display_name, email=email, url=url, id=id, auth_header_json=auth_header) # Create User object
    db.session.add(user) # Add User to Database
    db.session.commit() 
    flash('New Account Created!', 'success')

  else:
    user.auth_header_json = auth_header # Update auth header
    db.session.add(user) # Update User
    db.session.commit() 
    flash(f"Welcome back {user.display_name}!", 'success')
  
  session['user_id'] = user.id # Save user_id in session

  return redirect('/profile')


@app.route('/switch-user')
def switch_user():
  """Remove user id and authorization header and redirect to the authorization route"""

  session.clear() # Remover user_id from session
  return redirect('/authorize')


# -------------------------- PROFILE PAGE ---------------------------

@app.route('/profile', methods=['GET', 'POST'])
def show_profile():
  """Show a user's profile and a list of their SMS playlists"""
  
  # Prevent users from jumping ahead to /profile without first authorizing
  if 'user_id' not in session:
    flash('Please log in', 'warning')
    return redirect('/authorize')
  
  user = User.query.get_or_404(session['user_id']) # Get user using user_id in session
  
  # If the user soes not have a phone number, rediect the the phone number form
  if not user.phone_number:
    flash('Enter your phone number to create a playlist', 'warning')
    return redirect('/phone')

  form = PlaylistForm() # Form for making a new playlist

  # When the form is submitted
  if form.validate_on_submit():
    title = form.title.data # Get title from form
    create_playlist(auth_header=user.auth_header, user_id=user.id, title=title) # Create the playlist
    flash('Playlist Created', 'success')
    return redirect('/profile')

  return render_template('profile.html', user=user, form=form)


@app.route('/phone', methods = ['GET', 'POST'])
def get_phone_number():
  """Get a user's phone number using the PhoneForm"""

  user = User.query.get_or_404(session['user_id']) # get User
  form = PhoneForm() # Form for getting phone numbers

  if form.validate_on_submit():
    user.phone_number = form.phone.data # Save the user's phone number
    db.session.add(user)
    db.session.commit()
    flash('Phone Number Updated', 'success')
    return redirect('/profile')
  
  return render_template('phone.html', user=user, form=form)


@app.route('/profile/<int:playlist_id>/delete', methods=['POST'])
def delete_playlist(playlist_id):
  """Delete a playlists"""

  playlist = Playlist.query.get_or_404(playlist_id)
  if playlist.user_id == session['user_id']:
    db.session.delete(playlist)
    db.session.commit()
    flash('Playlist Deleted', 'warning')
    return redirect('/profile')
  
  # User is not authorized to delete the playlist
  else:
    flash('You cannot delete that playlist')

  return redirect('/profile')


@app.route('/api/receive_sms', methods=['POST'])
def receive_sms():
  """Route for Twilio to pass in recieved messages"""

  phone_number = request.form['From']
  body = request.form['Body']
  
  track_ids = get_track_ids_from_message(body) # Scan message for track_ids

  # If there were track ids in the message body
  if len(track_ids) > 0:
    user = User.query.filter_by(phone_number=phone_number).first() # Get the user based on the phone_number
    playlist = Playlist.query.filter_by(owner_id=user.id).first()
    # If playlist exists
    if playlist:
      add_tracks_to_playlist(playlist=playlist, track_ids=track_ids)  

  resp = MessagingResponse ()
  return str(resp)