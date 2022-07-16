"""Spotify GroupChat app"""

from flask import Flask, redirect, render_template, flash, session, request
from flask_debugtoolbar import DebugToolbarExtension
from flask_bootstrap import Bootstrap5
from twilio.twiml.messaging_response import MessagingResponse

from my_secrets import SECRET_KEY
from models import GuestUser, Playlist, HostUser, connect_db, db
from forms import PhoneForm, CreatePlaylistForm, SelectPlaylistForm, load_select_playlist_form_choices
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

  flash(f"Welcome {host_user.display_name}!", 'success')
  session['host_user_id'] = host_user.id # Save host_user_id in session

  return redirect('/profile')


@app.route('/switch-user')
def switch_user():
  """Remove user id and authorization header and redirect to the authorization route"""

  session.clear() # Remover user data from session
  return redirect('/authorize')


# -------------------------- PROFILE PAGE ---------------------------

@app.route('/profile/')
def redirect_to_playlist():
  """Bring a user to their active playlist page"""

  # Prevent users from jumping ahead to /profile without first authorizing
  if 'host_user_id' not in session:
    flash('Please log in', 'warning')
    return redirect('/authorize')
  
  host_user = HostUser.query.get_or_404(session['host_user_id']) # Get host_user using host_user_id in session

  playlist_id = host_user.active_playlist_id
  return redirect(f"/profile/{playlist_id}")


@app.route('/profile/<string:playlist_id>', methods=['GET', 'POST'])
def show_profile(playlist_id):
  """Show a user's playlist"""
  
  # Prevent users from jumping ahead to /profile without first authorizing
  if 'host_user_id' not in session:
    flash('Please log in', 'warning')
    return redirect('/authorize')
  
  host_user = HostUser.query.get_or_404(session['host_user_id']) # Get user using user_id in session

  # If the user soes not have a phone number, rediect the the phone number form
  if not host_user.phone_number:
    flash('Enter your phone number to create a playlist', 'warning')
    return redirect('/phone')

  playlist = Playlist.query.get_or_404(playlist_id) # Get the playlist

  select_form = load_select_playlist_form_choices(host_user=host_user)

  # When the form is submitted
  if select_form.validate_on_submit():
    new_playlist_id = select_form.playlist.data 
    flash('Playlist Created', 'success')
    return redirect(f"/profile/{new_playlist_id}")  

  create_form = CreatePlaylistForm() # Form for making a new playlist

  # When the form is submitted
  if create_form.validate_on_submit():
    title = create_form.title.data # Get title from form
    key = create_form.key.data.lower()
    create_playlist(host_user=host_user, title=title, key=key) # Create the playlist
    flash('Playlist Created', 'success')
    return redirect('/profile')

  return render_template('profile.html', user=host_user, playlist=playlist, select_form=select_form, create_form=create_form)


@app.route('/phone', methods = ['GET', 'POST'])
def get_phone_number():
  """Get a user's phone number using the PhoneForm"""

  host_user = HostUser.query.get_or_404(session['host_user_id']) # get HostUser
  form = PhoneForm() # Form for getting phone numbers

  if form.validate_on_submit():
    guest_user = GuestUser.query.filter_by(phone_number=form.phone.data).first()
    # if there is a guest user with that phone number
    if guest_user:
      host_user.active_playlist_id = guest_user.active_playlist_id
      db.session.delete(guest_user) # delete guest user to replace them with host user
      db.session.commit()

    host_user.phone_number = form.phone.data
    db.session.add(host_user)
    db.session.commit()
    flash('Phone Number Updated', 'success')
    return redirect('/profile')
  
  return render_template('phone.html', user=host_user, form=form)


@app.route('/profile/<int:playlist_id>/delete', methods=['POST'])
def delete_playlist(playlist_id):
  """Delete a playlists"""

  playlist = Playlist.query.get_or_404(playlist_id)
  if playlist.user_id == session['user_id']:
    db.session.delete(playlist)
    db.session.commit()
    flash('Playlist Deleted', 'warning')
    return redirect('/profile')
  
  # HostUser is not authorized to delete the playlist
  else:
    flash('You cannot delete that playlist')

  return redirect('/profile')


@app.route('/api/receive_sms', methods=['POST'])
def receive_sms():
  """Route for Twilio to pass in recieved messages"""

  phone_number = request.form['From']
  message = request.form['Body']
  
  track_ids = get_track_ids_from_message(message) # Scan message for track_ids
  playlist_key = get_playlist_key_from_message(message) # Scan message for playlist keys

  print("********************************************************")
  print(track_ids)
  print(playlist_key )

  if playlist_key or track_ids:
    guest_user = get_or_create_guest_user(phone_number=phone_number)

    if playlist_key:
      playlist = Playlist.query.filter_by(key=playlist_key).first() # Get phone number's first playlist
      if playlist:
        guest_user.active_playlist_id = playlist.id
        db.session.add(guest_user)
        db.session.commit()
      else:
          print('send invalid key sms')

    if track_ids:
      if guest_user.active_playlist_id:
        playlist = Playlist.query.filter_by(id=guest_user.active_playlist_id).first() # Get phone number's first playlist
        # If playlist exists
        if playlist:
          add_tracks_to_playlist(playlist=playlist, track_ids=track_ids, added_by=phone_number)
      else:
        print("send sms asking for key goes here")
    


  resp = MessagingResponse ()
  return str(resp)